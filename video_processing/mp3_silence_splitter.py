"""
MP3 Track Splitter — two detection modes:
  1. Silence Detection (ffmpeg silencedetect) — for albums with gaps between tracks
  2. Music Change Detection (librosa spectral analysis) — for continuous mixes
     where songs blend together without silence gaps.
Displays a waveform with editable split points, and exports individual tracks.
"""

import sys
import os
import re
import shutil
import subprocess
import tempfile
import numpy as np
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QGroupBox,
    QTableWidget, QTableWidgetItem, QProgressBar, QHeaderView, QMessageBox,
    QAbstractItemView, QSpinBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QFont
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from pydub import AudioSegment


DEFAULT_MUSIC_DIR = r"C:\Users\EranGross\OneDrive - Gross\Music"

# Silence detection parameters tuned for album compilations:
# - Songs in compilations typically have 1.5-4 seconds of silence between them
# - Threshold of -48 dB works well for most music recordings
SILENCE_DURATION = 2.0     # seconds — minimum gap to consider a track boundary
SILENCE_THRESHOLD = -48    # dB — below this is silence


def _find_ffmpeg() -> str | None:
    path = shutil.which("ffmpeg")
    if path:
        return path
    for candidate in [
        os.path.join(os.environ.get("ProgramFiles", r"C:\Program Files"), "ffmpeg", "bin", "ffmpeg.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Links", "ffmpeg.exe"),
        r"C:\ffmpeg\bin\ffmpeg.exe",
    ]:
        if os.path.isfile(candidate):
            return candidate
    return None


FFMPEG = _find_ffmpeg()

_silence_start_re = re.compile(r"silence_start:\s*([\d.]+)")
_silence_end_re = re.compile(r"silence_end:\s*([\d.]+)")


# ---------------------------------------------------------------------------
# Worker threads
# ---------------------------------------------------------------------------

class AudioLoadThread(QThread):
    """Load audio for waveform display (pydub, mono)."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        try:
            audio = AudioSegment.from_file(self.path)
            audio = audio.set_channels(1)
            self.finished.emit(audio)
        except Exception as e:
            self.error.emit(str(e))


class DetectionThread(QThread):
    """Run ffmpeg silencedetect and parse silence gaps."""
    finished = pyqtSignal(list)  # list of (silence_start_s, silence_end_s)
    error = pyqtSignal(str)

    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath

    def run(self):
        try:
            if not FFMPEG:
                self.error.emit("ffmpeg not found on system PATH")
                return

            cmd = [
                FFMPEG, "-hide_banner", "-i", self.filepath,
                "-af", f"silencedetect=noise={SILENCE_THRESHOLD}dB:d={SILENCE_DURATION}",
                "-f", "null", "-"
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=120,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            output = result.stderr

            silence_starts = []
            silence_ends = []
            for line in output.splitlines():
                m = _silence_start_re.search(line)
                if m:
                    silence_starts.append(float(m.group(1)))
                m = _silence_end_re.search(line)
                if m:
                    silence_ends.append(float(m.group(1)))

            # Build silence gap list as (start_s, end_s)
            gaps = list(zip(silence_starts, silence_ends))
            self.finished.emit(gaps)
        except Exception as e:
            self.error.emit(str(e))


class MusicChangeDetectionThread(QThread):
    """Detect song boundaries via spectral novelty — works without silence gaps.

    Uses MFCCs (timbre), chroma (tonality), and spectral contrast to build a
    novelty curve.  Peaks in the novelty curve correspond to points where the
    musical character changes, i.e. song boundaries.
    """
    finished = pyqtSignal(list)   # list of boundary times in seconds
    status = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, filepath, expected_tracks=0):
        super().__init__()
        self.filepath = filepath
        self.expected_tracks = expected_tracks  # 0 = auto-detect

    def run(self):
        try:
            import librosa
            from scipy.signal import find_peaks
            from scipy.ndimage import uniform_filter1d

            self.status.emit("Loading audio with librosa (may take a moment)…")
            y, sr = librosa.load(self.filepath, sr=22050, mono=True)
            duration = librosa.get_duration(y=y, sr=sr)

            self.status.emit("Extracting spectral features…")
            hop_length = 512

            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=hop_length)
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop_length)
            contrast = librosa.feature.spectral_contrast(y=y, sr=sr, hop_length=hop_length)

            # Downsample to ~1 frame/second for efficiency
            fps = sr / hop_length
            block = max(1, int(fps))
            n_frames = mfcc.shape[1]
            n_blocks = n_frames // block

            def downsample(feat):
                trim = n_blocks * block
                return feat[:, :trim].reshape(feat.shape[0], n_blocks, block).mean(axis=2)

            features = np.vstack([
                librosa.util.normalize(downsample(mfcc), axis=1),
                librosa.util.normalize(downsample(chroma), axis=1),
                librosa.util.normalize(downsample(contrast), axis=1),
            ])  # shape: (n_features, n_blocks)

            self.status.emit("Computing novelty curve…")

            # Sliding-window cosine distance between past and future blocks
            window = 15  # seconds (at 1 fps)
            feat_T = features.T  # (n_blocks, n_features)
            novelty = np.zeros(n_blocks)

            for i in range(window, n_blocks - window):
                left = feat_T[i - window:i].mean(axis=0)
                right = feat_T[i:i + window].mean(axis=0)
                norm_l = np.linalg.norm(left)
                norm_r = np.linalg.norm(right)
                if norm_l > 0 and norm_r > 0:
                    novelty[i] = 1.0 - np.dot(left, right) / (norm_l * norm_r)

            # Smooth and normalize
            novelty = uniform_filter1d(novelty, size=5)
            peak = novelty.max()
            if peak > 0:
                novelty /= peak

            self.status.emit("Finding song boundaries…")

            min_dist = 60  # at least 60 s between songs

            if self.expected_tracks > 1:
                n_boundaries = self.expected_tracks - 1
                peaks, props = find_peaks(novelty, distance=min_dist, prominence=0.05)
                if len(peaks) > n_boundaries:
                    top = np.argsort(props["prominences"])[-n_boundaries:]
                    peaks = np.sort(peaks[top])
                elif len(peaks) < n_boundaries:
                    # relax constraints
                    peaks, props = find_peaks(novelty, distance=min_dist // 2, prominence=0.02)
                    if len(peaks) > n_boundaries:
                        top = np.argsort(props["prominences"])[-n_boundaries:]
                        peaks = np.sort(peaks[top])
            else:
                peaks, _ = find_peaks(novelty, distance=min_dist, prominence=0.15, height=0.1)

            # Convert frame indices → seconds (1 fps after downsampling)
            boundary_times = peaks.astype(float).tolist()
            boundary_times = [t for t in boundary_times if 15 < t < duration - 15]

            self.finished.emit(boundary_times)
        except Exception as e:
            self.error.emit(str(e))


class SplitExportThread(QThread):
    """Export segments using ffmpeg — no re-encoding for MP3."""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, input_path, segments_sec, output_dir):
        super().__init__()
        self.input_path = input_path
        self.segments_sec = segments_sec  # list of (start_s, end_s)
        self.output_dir = output_dir

    def run(self):
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            total = len(self.segments_sec)
            ext = Path(self.input_path).suffix or ".mp3"

            for i, (start_s, end_s) in enumerate(self.segments_sec):
                filename = f"Track_{i + 1:02d}{ext}"
                filepath = os.path.join(self.output_dir, filename)
                duration = end_s - start_s
                self.progress.emit(
                    int((i / total) * 100),
                    f"Exporting {filename} ({i + 1}/{total})",
                )
                cmd = [
                    FFMPEG, "-hide_banner", "-y",
                    "-ss", f"{start_s:.3f}",
                    "-i", self.input_path,
                    "-t", f"{duration:.3f}",
                    "-c", "copy",
                    filepath,
                ]
                subprocess.run(
                    cmd, capture_output=True, timeout=60,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                )
            self.progress.emit(100, f"Done — {total} tracks exported")
            self.finished.emit(True, self.output_dir)
        except Exception as e:
            self.finished.emit(False, str(e))


# ---------------------------------------------------------------------------
# Waveform widget
# ---------------------------------------------------------------------------

class WaveformCanvas(FigureCanvasQTAgg):
    split_points_changed = pyqtSignal()

    DISPLAY_POINTS = 15_000

    def __init__(self, parent=None):
        self.fig = Figure(figsize=(10, 2.5), dpi=100)
        self.fig.patch.set_facecolor("#2b2b2b")
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

        self._duration_s = 0.0
        self._samples_x = None
        self._env_max = None
        self._env_min = None
        self._split_s: list[float] = []    # split points in seconds
        self._vlines = []

        self.mpl_connect("button_press_event", self._on_click)

    def set_audio(self, audio: AudioSegment):
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
        self._duration_s = len(audio) / 1000.0
        n = len(samples)
        chunk = max(1, n // self.DISPLAY_POINTS)
        trim = (n // chunk) * chunk
        reshaped = samples[:trim].reshape(-1, chunk)
        self._env_max = reshaped.max(axis=1)
        self._env_min = reshaped.min(axis=1)
        self._samples_x = np.linspace(0, self._duration_s, len(self._env_max))
        self._split_s.clear()
        self._draw()

    def set_split_points_from_gaps(self, gaps: list[tuple[float, float]]):
        """Set split points at the midpoint of each detected silence gap."""
        self._split_s.clear()
        for start_s, end_s in gaps:
            self._split_s.append((start_s + end_s) / 2.0)
        self._draw_split_lines()
        self.split_points_changed.emit()

    def set_split_points_from_times(self, times: list[float]):
        """Set split points from exact boundary times (music change detection)."""
        self._split_s = list(times)
        self._draw_split_lines()
        self.split_points_changed.emit()

    def get_segments(self) -> list[tuple[float, float]]:
        """Return contiguous segment ranges (seconds) from split points."""
        points = sorted(self._split_s)
        segs = []
        prev = 0.0
        for p in points:
            segs.append((prev, p))
            prev = p
        segs.append((prev, self._duration_s))
        return segs

    def _draw(self):
        self.ax.clear()
        self.ax.set_facecolor("#2b2b2b")
        if self._samples_x is None:
            self.draw()
            return
        self.ax.fill_between(
            self._samples_x, self._env_min, self._env_max,
            color="#4fc3f7", alpha=0.85,
        )
        self.ax.set_xlim(self._samples_x[0], self._samples_x[-1])
        peak = max(abs(self._env_min.min()), abs(self._env_max.max())) or 1
        self.ax.set_ylim(-peak * 1.05, peak * 1.05)
        self.ax.set_xlabel("Time (s)", color="white", fontsize=8)
        self.ax.tick_params(colors="white", labelsize=7)
        for spine in self.ax.spines.values():
            spine.set_color("#555")
        self.fig.tight_layout(pad=0.4)
        self._draw_split_lines()

    def _draw_split_lines(self):
        for vl in self._vlines:
            try:
                vl.remove()
            except ValueError:
                pass
        self._vlines.clear()
        for s in self._split_s:
            vl = self.ax.axvline(s, color="red", linewidth=1.2, alpha=0.85)
            self._vlines.append(vl)
        self.draw()

    def _on_click(self, event):
        if event.inaxes is not self.ax or self._samples_x is None:
            return
        clicked_s = event.xdata
        if event.button == 1:  # left click — add split point
            self._split_s.append(clicked_s)
        elif event.button == 3:  # right click — remove nearest
            if not self._split_s:
                return
            nearest = min(self._split_s, key=lambda p: abs(p - clicked_s))
            self._split_s.remove(nearest)
        self._draw_split_lines()
        self.split_points_changed.emit()


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class MP3SilenceSplitter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MP3 Track Splitter")
        self.resize(1000, 750)

        self._input_path: str | None = None
        self._audio: AudioSegment | None = None
        self._thread = None
        self._temp_preview: str | None = None

        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)
        self._audio_output.setVolume(0.8)

        self._build_ui()
        self._connect_signals()
        self._set_buttons_state(audio_loaded=False)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(6)

        # --- File row ---
        file_group = QGroupBox("Files")
        fg = QHBoxLayout(file_group)
        fg.addWidget(QLabel("Input:"))
        self.input_edit = QLineEdit()
        self.input_edit.setReadOnly(True)
        fg.addWidget(self.input_edit, stretch=1)
        self.btn_browse_input = QPushButton("Browse…")
        fg.addWidget(self.btn_browse_input)
        fg.addWidget(QLabel("Output Dir:"))
        self.output_edit = QLineEdit()
        fg.addWidget(self.output_edit, stretch=1)
        self.btn_browse_output = QPushButton("Browse…")
        fg.addWidget(self.btn_browse_output)
        layout.addWidget(file_group)

        # --- Info label ---
        self.info_label = QLabel(
            "Silence mode: splits at quiet gaps  |  Music Change mode: splits where the song changes  |  "
            "Left-click waveform to add split  |  Right-click to remove"
        )
        self.info_label.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(self.info_label)

        # --- Action buttons ---
        btn_row = QHBoxLayout()
        self.btn_detect = QPushButton("  Detect by Silence  ")
        self.btn_detect.setStyleSheet(
            "QPushButton { background-color: #388e3c; color: white; padding: 8px 16px; font-weight: bold; }"
            "QPushButton:disabled { background-color: #555; }"
        )
        btn_row.addWidget(self.btn_detect)

        self.btn_detect_music = QPushButton("  Detect by Music Change  ")
        self.btn_detect_music.setStyleSheet(
            "QPushButton { background-color: #e65100; color: white; padding: 8px 16px; font-weight: bold; }"
            "QPushButton:disabled { background-color: #555; }"
        )
        btn_row.addWidget(self.btn_detect_music)

        btn_row.addWidget(QLabel("Expected tracks:"))
        self.spin_tracks = QSpinBox()
        self.spin_tracks.setRange(0, 99)
        self.spin_tracks.setValue(0)
        self.spin_tracks.setSpecialValueText("Auto")
        self.spin_tracks.setToolTip("0 = auto-detect number of tracks.\nSet a number if you know how many songs are in the file.")
        self.spin_tracks.setFixedWidth(70)
        btn_row.addWidget(self.spin_tracks)

        self.btn_export = QPushButton("  Split && Export  ")
        self.btn_export.setStyleSheet(
            "QPushButton { background-color: #1976d2; color: white; padding: 8px 16px; font-weight: bold; }"
            "QPushButton:disabled { background-color: #555; }"
        )
        btn_row.addWidget(self.btn_export)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # --- Waveform ---
        self.canvas = WaveformCanvas()
        self.canvas.setMinimumHeight(160)
        layout.addWidget(self.canvas, stretch=1)

        # --- Segments table ---
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["#", "Start", "End", "Duration", "Play"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setMinimumHeight(120)
        layout.addWidget(self.table, stretch=1)

        # --- Progress ---
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        self.status_label = QLabel("Ready — ffmpeg: " + (FFMPEG or "NOT FOUND"))
        layout.addWidget(self.status_label)

    def _connect_signals(self):
        self.btn_browse_input.clicked.connect(self._browse_input)
        self.btn_browse_output.clicked.connect(self._browse_output)
        self.btn_detect.clicked.connect(self._run_detection)
        self.btn_detect_music.clicked.connect(self._run_music_change_detection)
        self.btn_export.clicked.connect(self._run_export)
        self.canvas.split_points_changed.connect(self._sync_table_from_canvas)

    def _set_buttons_state(self, audio_loaded=False, segments_ready=False):
        self.btn_detect.setEnabled(audio_loaded and FFMPEG is not None)
        self.btn_detect_music.setEnabled(audio_loaded)
        self.btn_export.setEnabled(segments_ready and FFMPEG is not None)

    # -- file browsing --

    def _browse_input(self):
        start_dir = DEFAULT_MUSIC_DIR if os.path.isdir(DEFAULT_MUSIC_DIR) else ""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Audio File", start_dir,
            "Audio Files (*.mp3 *.wav *.flac *.ogg *.m4a *.wma);;All Files (*)"
        )
        if not path:
            return
        self._input_path = path
        self.input_edit.setText(path)
        base = Path(path)
        out_dir = base.parent / f"{base.stem}_split"
        self.output_edit.setText(str(out_dir))
        self._load_audio(path)

    def _browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.output_edit.setText(path)

    # -- audio loading (for waveform only) --

    def _load_audio(self, path):
        self._set_buttons_state(audio_loaded=False)
        self.status_label.setText("Loading audio for waveform…")
        self.progress.setValue(0)
        self._thread = AudioLoadThread(path)
        self._thread.finished.connect(self._on_audio_loaded)
        self._thread.error.connect(self._on_error)
        self._thread.start()

    def _on_audio_loaded(self, audio: AudioSegment):
        self._audio = audio
        dur = len(audio) / 1000
        mins, secs = divmod(dur, 60)
        self.status_label.setText(
            f"Loaded — {int(mins)}m {secs:.1f}s | {audio.frame_rate} Hz | Click 'Detect' to find tracks"
        )
        self.canvas.set_audio(audio)
        self._set_buttons_state(audio_loaded=True)

    # -- detection via ffmpeg silencedetect --

    def _run_detection(self):
        if not self._input_path:
            return
        self.btn_detect.setEnabled(False)
        self.status_label.setText("Running ffmpeg silencedetect…")
        self.progress.setValue(0)
        self._thread = DetectionThread(self._input_path)
        self._thread.finished.connect(self._on_detection_done)
        self._thread.error.connect(self._on_error)
        self._thread.start()

    def _on_detection_done(self, gaps: list):
        self.canvas.set_split_points_from_gaps(gaps)
        segments = self.canvas.get_segments()
        self._populate_table(segments)
        self.status_label.setText(
            f"Found {len(gaps)} silence gaps → {len(segments)} tracks  |  "
            "Edit on waveform if needed, then Split & Export"
        )
        self._set_buttons_state(audio_loaded=True, segments_ready=len(segments) > 0)

    # -- music change detection via librosa --

    def _run_music_change_detection(self):
        if not self._input_path:
            return
        self.btn_detect_music.setEnabled(False)
        self.btn_detect.setEnabled(False)
        self.status_label.setText("Analyzing spectral features…")
        self.progress.setValue(0)
        expected = self.spin_tracks.value()
        self._thread = MusicChangeDetectionThread(self._input_path, expected_tracks=expected)
        self._thread.finished.connect(self._on_music_change_done)
        self._thread.status.connect(self._on_music_change_status)
        self._thread.error.connect(self._on_error)
        self._thread.start()

    def _on_music_change_status(self, msg: str):
        self.status_label.setText(msg)

    def _on_music_change_done(self, boundary_times: list):
        self.canvas.set_split_points_from_times(boundary_times)
        segments = self.canvas.get_segments()
        self._populate_table(segments)
        self.status_label.setText(
            f"Found {len(boundary_times)} music changes → {len(segments)} tracks  |  "
            "Edit on waveform if needed, then Split & Export"
        )
        self._set_buttons_state(audio_loaded=True, segments_ready=len(segments) > 0)

    # -- table --

    @staticmethod
    def _fmt_time(seconds: float) -> str:
        mins, secs = divmod(seconds, 60)
        return f"{int(mins):02d}:{secs:05.2f}"

    def _populate_table(self, segments: list[tuple[float, float]]):
        self.table.setRowCount(len(segments))
        for i, (start_s, end_s) in enumerate(segments):
            dur = end_s - start_s
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table.setItem(i, 1, QTableWidgetItem(self._fmt_time(start_s)))
            self.table.setItem(i, 2, QTableWidgetItem(self._fmt_time(end_s)))
            self.table.setItem(i, 3, QTableWidgetItem(self._fmt_time(dur)))
            btn = QPushButton("▶")
            btn.setFixedWidth(40)
            btn.clicked.connect(
                lambda checked, s=start_s, e=end_s: self._play_segment(s, e)
            )
            self.table.setCellWidget(i, 4, btn)

    def _sync_table_from_canvas(self):
        segments = self.canvas.get_segments()
        self._populate_table(segments)
        self._set_buttons_state(audio_loaded=self._audio is not None, segments_ready=len(segments) > 0)

    # -- playback --

    def _play_segment(self, start_s: float, end_s: float):
        if self._audio is None:
            return
        self._player.stop()
        self._cleanup_temp()
        start_ms = int(start_s * 1000)
        end_ms = int(end_s * 1000)
        chunk = self._audio[start_ms:end_ms]
        # Only play first 15 seconds for preview
        if len(chunk) > 15000:
            chunk = chunk[:15000]
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.close()
        self._temp_preview = tmp.name
        chunk.export(self._temp_preview, format="wav")
        self._player.setSource(QUrl.fromLocalFile(self._temp_preview))
        self._player.play()
        preview_dur = min(end_s - start_s, 15.0)
        self.status_label.setText(f"Playing preview ({preview_dur:.1f}s)…")

    def _cleanup_temp(self):
        if self._temp_preview and os.path.exists(self._temp_preview):
            try:
                os.remove(self._temp_preview)
            except OSError:
                pass
            self._temp_preview = None

    # -- export --

    def _run_export(self):
        if not self._input_path:
            return
        segments = self.canvas.get_segments()
        if not segments:
            return
        output_dir = self.output_edit.text().strip()
        if not output_dir:
            QMessageBox.warning(self, "No Output Directory", "Please set an output directory.")
            return
        self.btn_export.setEnabled(False)
        self.status_label.setText("Exporting…")
        self._thread = SplitExportThread(self._input_path, segments, output_dir)
        self._thread.progress.connect(self._on_export_progress)
        self._thread.finished.connect(self._on_export_done)
        self._thread.start()

    def _on_export_progress(self, pct: int, msg: str):
        self.progress.setValue(pct)
        self.status_label.setText(msg)

    def _on_export_done(self, success: bool, msg: str):
        if success:
            self.progress.setValue(100)
            self.status_label.setText(f"Export complete → {msg}")
            QMessageBox.information(self, "Export Complete", f"Tracks saved to:\n{msg}")
        else:
            self._on_error(msg)
        self._set_buttons_state(audio_loaded=True, segments_ready=True)

    def _on_error(self, msg: str):
        self.status_label.setText(f"Error: {msg}")
        QMessageBox.critical(self, "Error", msg)
        if self._audio is not None:
            self._set_buttons_state(audio_loaded=True)

    def closeEvent(self, event):
        self._player.stop()
        self._cleanup_temp()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 9))
    window = MP3SilenceSplitter()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
