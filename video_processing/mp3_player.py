"""
MP3 Player — full-featured desktop audio player.

Features:
  - Play/Pause/Stop/Next/Previous with seek bar
  - Volume control with mute toggle
  - Playlist management (add files, add folder, remove, clear, drag-drop reorder)
  - Shuffle and repeat modes (off, one, all)
  - Album art display from embedded metadata
  - Track info (title, artist, album, duration)
  - Search/filter playlist
  - Keyboard shortcuts
  - Dark theme (Fusion)
  - System tray integration
  - Remembers playlist and state across sessions
"""

import sys
import os
import json
import random
import base64
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QSlider, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QLineEdit,
    QMenu, QSystemTrayIcon, QStyle, QStatusBar, QSplitter,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QUrl, QSize, QTimer, pyqtSignal, QThread, QMimeData
from PyQt6.QtGui import (
    QFont, QPalette, QColor, QIcon, QPixmap, QImage, QPainter,
    QAction, QShortcut, QKeySequence, QDrag,
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

try:
    from mutagen import File as MutagenFile
    from mutagen.mp3 import MP3
    from mutagen.id3 import ID3
    HAS_MUTAGEN = True
except ImportError:
    HAS_MUTAGEN = False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

APP_NAME = "MP3 Player"
STATE_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "MP3Player")
STATE_FILE = os.path.join(STATE_DIR, "state.json")
SUPPORTED_FORMATS = (
    "*.mp3", "*.wav", "*.flac", "*.ogg", "*.m4a", "*.wma", "*.aac", "*.opus",
)
SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".wma", ".aac", ".opus"}
DEFAULT_MUSIC_DIR = os.path.join(os.path.expanduser("~"), "Music")

ICON_SIZE = 32
ART_SIZE = 220


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def _format_ms(ms: int) -> str:
    """Format milliseconds to MM:SS."""
    if ms < 0:
        ms = 0
    total_sec = ms // 1000
    minutes = total_sec // 60
    seconds = total_sec % 60
    return f"{minutes}:{seconds:02d}"


def _extract_metadata(filepath: str) -> dict:
    """Extract metadata from audio file using mutagen."""
    info = {
        "path": filepath,
        "title": Path(filepath).stem,
        "artist": "",
        "album": "",
        "duration_ms": 0,
        "cover_data": None,
    }
    if not HAS_MUTAGEN:
        return info
    try:
        audio = MutagenFile(filepath)
        if audio is None:
            return info
        # Duration
        if audio.info and hasattr(audio.info, "length"):
            info["duration_ms"] = int(audio.info.length * 1000)
        # ID3 tags (MP3)
        if hasattr(audio, "tags") and audio.tags:
            tags = audio.tags
            # Title
            for key in ("TIT2", "title", "\xa9nam"):
                if key in tags:
                    val = tags[key]
                    info["title"] = str(val[0]) if isinstance(val, list) else str(val)
                    break
            # Artist
            for key in ("TPE1", "artist", "\xa9ART"):
                if key in tags:
                    val = tags[key]
                    info["artist"] = str(val[0]) if isinstance(val, list) else str(val)
                    break
            # Album
            for key in ("TALB", "album", "\xa9alb"):
                if key in tags:
                    val = tags[key]
                    info["album"] = str(val[0]) if isinstance(val, list) else str(val)
                    break
            # Cover art — ID3 APIC frames
            for key in tags:
                if str(key).startswith("APIC"):
                    apic = tags[key]
                    if hasattr(apic, "data"):
                        info["cover_data"] = apic.data
                    break
            # Cover art — MP4/M4A
            if info["cover_data"] is None and "covr" in tags:
                covers = tags["covr"]
                if covers:
                    info["cover_data"] = bytes(covers[0])
            # Cover art — FLAC
        if info["cover_data"] is None and hasattr(audio, "pictures"):
            for pic in audio.pictures:
                if hasattr(pic, "data"):
                    info["cover_data"] = pic.data
                    break
    except Exception:
        pass
    return info


def _load_state() -> dict:
    """Load saved application state."""
    try:
        if os.path.isfile(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_state(state: dict):
    """Save application state to disk."""
    try:
        os.makedirs(STATE_DIR, exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass


def _make_default_art_pixmap(size: int = ART_SIZE) -> QPixmap:
    """Create a default music note icon pixmap."""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(50, 50, 50))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(80, 80, 80))
    painter.drawRoundedRect(0, 0, size, size, 12, 12)
    painter.setPen(QColor(120, 120, 120))
    font = QFont("Segoe UI", size // 3)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "\u266b")
    painter.end()
    return pixmap


def _cover_to_pixmap(data: bytes, size: int = ART_SIZE) -> QPixmap | None:
    """Convert cover art bytes to a scaled QPixmap."""
    if not data:
        return None
    img = QImage()
    if img.loadFromData(data):
        return QPixmap.fromImage(img).scaled(
            size, size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
    return None


def _make_app_icon() -> QIcon:
    """Create a simple app icon (play triangle on dark circle)."""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(0, 120, 215))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, size - 4, size - 4)
    painter.setBrush(QColor(255, 255, 255))
    from PyQt6.QtGui import QPolygonF
    from PyQt6.QtCore import QPointF
    tri = QPolygonF([
        QPointF(size * 0.38, size * 0.25),
        QPointF(size * 0.38, size * 0.75),
        QPointF(size * 0.78, size * 0.50),
    ])
    painter.drawPolygon(tri)
    painter.end()
    return QIcon(pixmap)


# ---------------------------------------------------------------------------
# Metadata loader thread
# ---------------------------------------------------------------------------

class MetadataLoaderThread(QThread):
    """Load metadata for a list of file paths in the background."""
    loaded = pyqtSignal(int, dict)  # (index, metadata_dict)
    finished_all = pyqtSignal()

    def __init__(self, filepaths: list[str], start_index: int = 0):
        super().__init__()
        self._filepaths = filepaths
        self._start_index = start_index

    def run(self):
        for i, fp in enumerate(self._filepaths):
            meta = _extract_metadata(fp)
            self.loaded.emit(self._start_index + i, meta)
        self.finished_all.emit()


# ---------------------------------------------------------------------------
# Custom seek slider (click-to-position)
# ---------------------------------------------------------------------------

class ClickSlider(QSlider):
    """QSlider subclass that jumps to clicked position."""

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.maximum() > 0:
            if self.orientation() == Qt.Orientation.Horizontal:
                val = int(event.position().x() / self.width() * self.maximum())
            else:
                val = int((1 - event.position().y() / self.height()) * self.maximum())
            self.setValue(val)
            self.sliderMoved.emit(val)
            event.accept()
        else:
            super().mousePressEvent(event)


# ---------------------------------------------------------------------------
# Reorderable playlist table
# ---------------------------------------------------------------------------

class PlaylistTable(QTableWidget):
    """QTableWidget with internal drag-drop reorder support."""
    order_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.verticalHeader().setSectionsMovable(True)
        self.verticalHeader().setDragEnabled(True)
        self.verticalHeader().setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

    def dropEvent(self, event):
        super().dropEvent(event)
        self.order_changed.emit()


# ---------------------------------------------------------------------------
# Main window
# ---------------------------------------------------------------------------

class MP3Player(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(900, 650)
        self.resize(1000, 750)

        # Data
        self._playlist: list[dict] = []  # list of metadata dicts
        self._current_index: int = -1
        self._shuffle = False
        self._repeat_mode = "off"  # off, one, all
        self._shuffle_order: list[int] = []
        self._shuffle_pos: int = -1
        self._is_user_seeking = False
        self._muted = False
        self._pre_mute_volume = 80

        # Media player
        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)
        self._audio_output.setVolume(0.8)

        self._loader_thread: MetadataLoaderThread | None = None
        self._default_art = _make_default_art_pixmap()

        self._build_ui()
        self._build_menu()
        self._build_tray()
        self._connect_signals()
        self._setup_shortcuts()
        self._restore_state()

    # -----------------------------------------------------------------------
    # UI construction
    # -----------------------------------------------------------------------

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # --- Top section: album art + track info ---
        top_layout = QHBoxLayout()
        top_layout.setSpacing(15)

        # Album art
        self._art_label = QLabel()
        self._art_label.setFixedSize(ART_SIZE, ART_SIZE)
        self._art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._art_label.setPixmap(self._default_art)
        self._art_label.setStyleSheet(
            "QLabel { background-color: #323232; border-radius: 10px; }"
        )
        top_layout.addWidget(self._art_label)

        # Track info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        self._title_label = QLabel("No track loaded")
        self._title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        self._title_label.setWordWrap(True)
        self._title_label.setStyleSheet("color: #ffffff;")
        info_layout.addWidget(self._title_label)

        self._artist_label = QLabel("")
        self._artist_label.setFont(QFont("Segoe UI", 13))
        self._artist_label.setStyleSheet("color: #b0b0b0;")
        info_layout.addWidget(self._artist_label)

        self._album_label = QLabel("")
        self._album_label.setFont(QFont("Segoe UI", 11))
        self._album_label.setStyleSheet("color: #808080;")
        info_layout.addWidget(self._album_label)

        info_layout.addStretch()
        top_layout.addLayout(info_layout, stretch=1)
        main_layout.addLayout(top_layout)

        # --- Seek bar ---
        seek_layout = QHBoxLayout()
        self._time_current = QLabel("0:00")
        self._time_current.setFixedWidth(45)
        self._time_current.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._time_current.setStyleSheet("color: #ccc; font-size: 11px;")
        seek_layout.addWidget(self._time_current)

        self._seek_slider = ClickSlider(Qt.Orientation.Horizontal)
        self._seek_slider.setRange(0, 0)
        self._seek_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px; background: #444; border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #0078d7; width: 14px; height: 14px;
                margin: -4px 0; border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #0078d7; border-radius: 3px;
            }
        """)
        seek_layout.addWidget(self._seek_slider, stretch=1)

        self._time_total = QLabel("0:00")
        self._time_total.setFixedWidth(45)
        self._time_total.setStyleSheet("color: #ccc; font-size: 11px;")
        seek_layout.addWidget(self._time_total)
        main_layout.addLayout(seek_layout)

        # --- Transport controls ---
        transport = QHBoxLayout()
        transport.setSpacing(6)

        btn_style = """
            QPushButton {
                background-color: #3a3a3a; color: white; border: none;
                border-radius: 6px; padding: 8px 14px; font-size: 15px;
            }
            QPushButton:hover { background-color: #505050; }
            QPushButton:pressed { background-color: #606060; }
        """
        btn_style_active = """
            QPushButton {
                background-color: #0078d7; color: white; border: none;
                border-radius: 6px; padding: 8px 14px; font-size: 15px;
            }
            QPushButton:hover { background-color: #1a8ae6; }
        """

        self._btn_shuffle = QPushButton("\U0001f500")  # 🔀
        self._btn_shuffle.setToolTip("Shuffle")
        self._btn_shuffle.setFixedSize(42, 42)
        self._btn_shuffle.setStyleSheet(btn_style)
        transport.addWidget(self._btn_shuffle)

        self._btn_prev = QPushButton("\u23ee")  # ⏮
        self._btn_prev.setToolTip("Previous (P / Left)")
        self._btn_prev.setFixedSize(42, 42)
        self._btn_prev.setStyleSheet(btn_style)
        transport.addWidget(self._btn_prev)

        self._btn_play = QPushButton("\u25b6")  # ▶
        self._btn_play.setToolTip("Play / Pause (Space)")
        self._btn_play.setFixedSize(52, 52)
        self._btn_play.setStyleSheet("""
            QPushButton {
                background-color: #0078d7; color: white; border: none;
                border-radius: 26px; font-size: 20px;
            }
            QPushButton:hover { background-color: #1a8ae6; }
            QPushButton:pressed { background-color: #005a9e; }
        """)
        transport.addWidget(self._btn_play)

        self._btn_stop = QPushButton("\u23f9")  # ⏹
        self._btn_stop.setToolTip("Stop (S)")
        self._btn_stop.setFixedSize(42, 42)
        self._btn_stop.setStyleSheet(btn_style)
        transport.addWidget(self._btn_stop)

        self._btn_next = QPushButton("\u23ed")  # ⏭
        self._btn_next.setToolTip("Next (N / Right)")
        self._btn_next.setFixedSize(42, 42)
        self._btn_next.setStyleSheet(btn_style)
        transport.addWidget(self._btn_next)

        self._btn_repeat = QPushButton("\U0001f501")  # 🔁
        self._btn_repeat.setToolTip("Repeat: Off")
        self._btn_repeat.setFixedSize(42, 42)
        self._btn_repeat.setStyleSheet(btn_style)
        transport.addWidget(self._btn_repeat)

        transport.addSpacing(20)

        # Volume
        self._btn_mute = QPushButton("\U0001f50a")  # 🔊
        self._btn_mute.setToolTip("Mute (M)")
        self._btn_mute.setFixedSize(36, 36)
        self._btn_mute.setStyleSheet(btn_style)
        transport.addWidget(self._btn_mute)

        self._volume_slider = ClickSlider(Qt.Orientation.Horizontal)
        self._volume_slider.setRange(0, 100)
        self._volume_slider.setValue(80)
        self._volume_slider.setFixedWidth(120)
        self._volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px; background: #444; border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ccc; width: 12px; height: 12px;
                margin: -4px 0; border-radius: 6px;
            }
            QSlider::sub-page:horizontal {
                background: #888; border-radius: 2px;
            }
        """)
        transport.addWidget(self._volume_slider)

        self._volume_label = QLabel("80%")
        self._volume_label.setFixedWidth(35)
        self._volume_label.setStyleSheet("color: #aaa; font-size: 11px;")
        transport.addWidget(self._volume_label)

        transport.addStretch()
        main_layout.addLayout(transport)

        # Store btn_style references for toggle updates
        self._btn_style = btn_style
        self._btn_style_active = btn_style_active

        # --- Search bar ---
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("\U0001f50d"))  # 🔍
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("Search playlist... (Ctrl+F)")
        self._search_edit.setClearButtonEnabled(True)
        self._search_edit.setStyleSheet("""
            QLineEdit {
                background-color: #383838; color: #ddd; border: 1px solid #555;
                border-radius: 4px; padding: 4px 8px;
            }
            QLineEdit:focus { border-color: #0078d7; }
        """)
        search_layout.addWidget(self._search_edit, stretch=1)
        main_layout.addLayout(search_layout)

        # --- Playlist table ---
        self._table = PlaylistTable()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["#", "Title", "Artist", "Album", "Duration"])
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self._table.setColumnWidth(0, 40)
        self._table.setColumnWidth(4, 60)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.verticalHeader().setVisible(False)
        self._table.setShowGrid(False)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.setStyleSheet("""
            QTableWidget {
                background-color: #2a2a2a; alternate-background-color: #323232;
                color: #ddd; border: none; font-size: 12px;
            }
            QTableWidget::item:selected {
                background-color: #0078d7;
            }
            QHeaderView::section {
                background-color: #383838; color: #aaa; border: none;
                padding: 4px; font-weight: bold;
            }
        """)
        main_layout.addWidget(self._table, stretch=1)

        # --- Status bar ---
        self._status = QStatusBar()
        self._status.setStyleSheet("color: #888;")
        self.setStatusBar(self._status)
        self._status.showMessage("Ready")

    def _build_menu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar { background-color: #2a2a2a; color: #ccc; }
            QMenuBar::item:selected { background-color: #0078d7; }
            QMenu { background-color: #2a2a2a; color: #ccc; border: 1px solid #444; }
            QMenu::item:selected { background-color: #0078d7; }
        """)

        # File menu
        file_menu = menubar.addMenu("&File")
        act_add_files = QAction("Add &Files...", self)
        act_add_files.setShortcut("Ctrl+O")
        act_add_files.triggered.connect(self.add_files)
        file_menu.addAction(act_add_files)

        act_add_folder = QAction("Add F&older...", self)
        act_add_folder.setShortcut("Ctrl+Shift+O")
        act_add_folder.triggered.connect(self.add_folder)
        file_menu.addAction(act_add_folder)

        file_menu.addSeparator()

        act_clear = QAction("&Clear Playlist", self)
        act_clear.triggered.connect(self.clear_playlist)
        file_menu.addAction(act_clear)

        file_menu.addSeparator()

        act_quit = QAction("&Quit", self)
        act_quit.setShortcut("Ctrl+Q")
        act_quit.triggered.connect(self._quit_app)
        file_menu.addAction(act_quit)

        # Playback menu
        play_menu = menubar.addMenu("&Playback")
        act_play = QAction("Play/&Pause", self)
        act_play.setShortcut("Space")
        act_play.triggered.connect(self.toggle_play_pause)
        play_menu.addAction(act_play)

        act_stop = QAction("&Stop", self)
        act_stop.triggered.connect(self.stop)
        play_menu.addAction(act_stop)

        act_next = QAction("&Next", self)
        act_next.triggered.connect(self.play_next)
        play_menu.addAction(act_next)

        act_prev = QAction("P&revious", self)
        act_prev.triggered.connect(self.play_previous)
        play_menu.addAction(act_prev)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        act_about = QAction("&About", self)
        act_about.triggered.connect(self._show_about)
        help_menu.addAction(act_about)

    def _build_tray(self):
        self._tray = QSystemTrayIcon(self)
        self._tray.setIcon(_make_app_icon())
        self._tray.setToolTip(APP_NAME)

        tray_menu = QMenu()
        tray_menu.setStyleSheet("""
            QMenu { background-color: #2a2a2a; color: #ccc; border: 1px solid #444; }
            QMenu::item:selected { background-color: #0078d7; }
        """)
        act_show = tray_menu.addAction("Show")
        act_show.triggered.connect(self._show_window)
        act_pp = tray_menu.addAction("Play/Pause")
        act_pp.triggered.connect(self.toggle_play_pause)
        act_n = tray_menu.addAction("Next")
        act_n.triggered.connect(self.play_next)
        act_p = tray_menu.addAction("Previous")
        act_p.triggered.connect(self.play_previous)
        tray_menu.addSeparator()
        act_q = tray_menu.addAction("Quit")
        act_q.triggered.connect(self._quit_app)

        self._tray.setContextMenu(tray_menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def _connect_signals(self):
        # Transport buttons
        self._btn_play.clicked.connect(self.toggle_play_pause)
        self._btn_stop.clicked.connect(self.stop)
        self._btn_next.clicked.connect(self.play_next)
        self._btn_prev.clicked.connect(self.play_previous)
        self._btn_shuffle.clicked.connect(self._toggle_shuffle)
        self._btn_repeat.clicked.connect(self._cycle_repeat)
        self._btn_mute.clicked.connect(self._toggle_mute)

        # Sliders
        self._seek_slider.sliderPressed.connect(lambda: setattr(self, "_is_user_seeking", True))
        self._seek_slider.sliderReleased.connect(self._on_seek_released)
        self._seek_slider.sliderMoved.connect(self._on_seek_moved)
        self._volume_slider.valueChanged.connect(self._on_volume_changed)

        # Player signals
        self._player.positionChanged.connect(self._on_position_changed)
        self._player.durationChanged.connect(self._on_duration_changed)
        self._player.mediaStatusChanged.connect(self._on_media_status_changed)
        self._player.playbackStateChanged.connect(self._on_playback_state_changed)

        # Playlist
        self._table.doubleClicked.connect(self._on_table_double_click)
        self._table.customContextMenuRequested.connect(self._on_table_context_menu)
        self._table.order_changed.connect(self._on_playlist_reordered)

        # Search
        self._search_edit.textChanged.connect(self._filter_playlist)

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("N"), self).activated.connect(self.play_next)
        QShortcut(QKeySequence("P"), self).activated.connect(self.play_previous)
        QShortcut(QKeySequence("Right"), self).activated.connect(self.play_next)
        QShortcut(QKeySequence("Left"), self).activated.connect(self.play_previous)
        QShortcut(QKeySequence("Up"), self).activated.connect(self._volume_up)
        QShortcut(QKeySequence("Down"), self).activated.connect(self._volume_down)
        QShortcut(QKeySequence("M"), self).activated.connect(self._toggle_mute)
        QShortcut(QKeySequence("S"), self).activated.connect(self.stop)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self._focus_search)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.remove_selected)

    # -----------------------------------------------------------------------
    # Playback
    # -----------------------------------------------------------------------

    def play_track(self, index: int):
        if index < 0 or index >= len(self._playlist):
            return
        self._current_index = index
        track = self._playlist[index]
        filepath = track["path"]
        if not os.path.isfile(filepath):
            self._status.showMessage(f"File not found: {filepath}")
            return

        self._player.setSource(QUrl.fromLocalFile(filepath))
        self._player.play()

        # Update display
        self._update_track_display(track)
        self._highlight_current_row()
        self._status.showMessage(f"Playing: {track['title']}")
        self._tray.setToolTip(f"{APP_NAME} — {track['title']}")

    def toggle_play_pause(self):
        state = self._player.playbackState()
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self._player.play()
        else:
            # Stopped — play current or first track
            if self._current_index >= 0:
                self.play_track(self._current_index)
            elif self._playlist:
                self.play_track(0)

    def stop(self):
        self._player.stop()
        self._seek_slider.setValue(0)
        self._time_current.setText("0:00")
        self._status.showMessage("Stopped")

    def play_next(self):
        if not self._playlist:
            return
        if self._repeat_mode == "one":
            self.play_track(self._current_index)
            return
        if self._shuffle:
            self._shuffle_pos += 1
            if self._shuffle_pos >= len(self._shuffle_order):
                self._generate_shuffle_order()
                self._shuffle_pos = 0
                if self._repeat_mode == "off":
                    self.stop()
                    return
            self.play_track(self._shuffle_order[self._shuffle_pos])
        else:
            next_idx = self._current_index + 1
            if next_idx >= len(self._playlist):
                if self._repeat_mode == "all":
                    next_idx = 0
                else:
                    self.stop()
                    return
            self.play_track(next_idx)

    def play_previous(self):
        if not self._playlist:
            return
        # If more than 3 seconds in, restart current track
        if self._player.position() > 3000:
            self._player.setPosition(0)
            return
        if self._shuffle and self._shuffle_pos > 0:
            self._shuffle_pos -= 1
            self.play_track(self._shuffle_order[self._shuffle_pos])
        else:
            prev_idx = self._current_index - 1
            if prev_idx < 0:
                prev_idx = len(self._playlist) - 1 if self._repeat_mode == "all" else 0
            self.play_track(prev_idx)

    # -----------------------------------------------------------------------
    # Playlist management
    # -----------------------------------------------------------------------

    def add_files(self):
        filter_str = "Audio Files (" + " ".join(SUPPORTED_FORMATS) + ")"
        files, _ = QFileDialog.getOpenFileNames(
            self, "Add Audio Files", DEFAULT_MUSIC_DIR, filter_str,
        )
        if files:
            self._add_paths(files)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Add Folder", DEFAULT_MUSIC_DIR,
        )
        if folder:
            files = []
            for root, dirs, filenames in os.walk(folder):
                for fn in sorted(filenames):
                    if Path(fn).suffix.lower() in SUPPORTED_EXTENSIONS:
                        files.append(os.path.join(root, fn))
            if files:
                self._add_paths(files)
            else:
                self._status.showMessage("No audio files found in folder")

    def _add_paths(self, filepaths: list[str]):
        start_index = len(self._playlist)
        # Add placeholder entries
        for fp in filepaths:
            entry = {
                "path": fp,
                "title": Path(fp).stem,
                "artist": "",
                "album": "",
                "duration_ms": 0,
                "cover_data": None,
            }
            self._playlist.append(entry)
            self._add_table_row(entry, len(self._playlist) - 1)

        # Load metadata in background
        self._loader_thread = MetadataLoaderThread(filepaths, start_index)
        self._loader_thread.loaded.connect(self._on_metadata_loaded)
        self._loader_thread.finished_all.connect(
            lambda: self._status.showMessage(f"Loaded {len(filepaths)} tracks")
        )
        self._loader_thread.start()
        self._status.showMessage(f"Loading metadata for {len(filepaths)} files...")

    def _add_table_row(self, entry: dict, index: int):
        row = self._table.rowCount()
        self._table.insertRow(row)
        num_item = QTableWidgetItem(str(index + 1))
        num_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self._table.setItem(row, 0, num_item)
        self._table.setItem(row, 1, QTableWidgetItem(entry["title"]))
        self._table.setItem(row, 2, QTableWidgetItem(entry["artist"]))
        self._table.setItem(row, 3, QTableWidgetItem(entry["album"]))
        dur = _format_ms(entry["duration_ms"]) if entry["duration_ms"] else ""
        dur_item = QTableWidgetItem(dur)
        dur_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self._table.setItem(row, 4, dur_item)

    def _on_metadata_loaded(self, index: int, meta: dict):
        if index < len(self._playlist):
            self._playlist[index] = meta
            row = index
            if row < self._table.rowCount():
                self._table.item(row, 1).setText(meta["title"])
                self._table.item(row, 2).setText(meta["artist"])
                self._table.item(row, 3).setText(meta["album"])
                if meta["duration_ms"]:
                    self._table.item(row, 4).setText(_format_ms(meta["duration_ms"]))

    def remove_selected(self):
        rows = sorted(set(idx.row() for idx in self._table.selectedIndexes()), reverse=True)
        if not rows:
            return
        for row in rows:
            if row < len(self._playlist):
                self._playlist.pop(row)
            self._table.removeRow(row)
        # Fix numbering and current index
        self._renumber_table()
        if self._current_index in rows:
            self.stop()
            self._current_index = -1
        elif self._current_index >= len(self._playlist):
            self._current_index = len(self._playlist) - 1

    def clear_playlist(self):
        self.stop()
        self._playlist.clear()
        self._table.setRowCount(0)
        self._current_index = -1
        self._art_label.setPixmap(self._default_art)
        self._title_label.setText("No track loaded")
        self._artist_label.setText("")
        self._album_label.setText("")
        self._status.showMessage("Playlist cleared")

    def _renumber_table(self):
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            if item:
                item.setText(str(row + 1))

    def _on_playlist_reordered(self):
        """Sync internal playlist with table visual order after drag-drop."""
        new_playlist = []
        for row in range(self._table.rowCount()):
            title_item = self._table.item(row, 1)
            if title_item:
                # Find matching entry by title and path
                title = title_item.text()
                for entry in self._playlist:
                    if entry["title"] == title and entry not in new_playlist:
                        new_playlist.append(entry)
                        break
        if len(new_playlist) == len(self._playlist):
            self._playlist = new_playlist
        self._renumber_table()

    # -----------------------------------------------------------------------
    # Track display
    # -----------------------------------------------------------------------

    def _update_track_display(self, track: dict):
        self._title_label.setText(track["title"])
        self._artist_label.setText(track.get("artist", ""))
        self._album_label.setText(track.get("album", ""))
        cover = _cover_to_pixmap(track.get("cover_data"))
        self._art_label.setPixmap(cover if cover else self._default_art)

    def _highlight_current_row(self):
        if 0 <= self._current_index < self._table.rowCount():
            self._table.selectRow(self._current_index)

    # -----------------------------------------------------------------------
    # Shuffle / Repeat
    # -----------------------------------------------------------------------

    def _toggle_shuffle(self):
        self._shuffle = not self._shuffle
        if self._shuffle:
            self._btn_shuffle.setStyleSheet(self._btn_style_active)
            self._generate_shuffle_order()
            self._status.showMessage("Shuffle: On")
        else:
            self._btn_shuffle.setStyleSheet(self._btn_style)
            self._status.showMessage("Shuffle: Off")

    def _generate_shuffle_order(self):
        self._shuffle_order = list(range(len(self._playlist)))
        random.shuffle(self._shuffle_order)
        # Put current track first if playing
        if self._current_index >= 0 and self._current_index in self._shuffle_order:
            self._shuffle_order.remove(self._current_index)
            self._shuffle_order.insert(0, self._current_index)
        self._shuffle_pos = 0

    def _cycle_repeat(self):
        modes = ["off", "one", "all"]
        icons = ["\U0001f501", "\U0001f502", "\U0001f501"]  # 🔁 🔂 🔁
        labels = ["Off", "One", "All"]
        current = modes.index(self._repeat_mode)
        next_mode = (current + 1) % len(modes)
        self._repeat_mode = modes[next_mode]
        self._btn_repeat.setText(icons[next_mode])
        self._btn_repeat.setToolTip(f"Repeat: {labels[next_mode]}")
        if self._repeat_mode == "off":
            self._btn_repeat.setStyleSheet(self._btn_style)
        else:
            self._btn_repeat.setStyleSheet(self._btn_style_active)
        self._status.showMessage(f"Repeat: {labels[next_mode]}")

    # -----------------------------------------------------------------------
    # Volume
    # -----------------------------------------------------------------------

    def _on_volume_changed(self, value: int):
        self._audio_output.setVolume(value / 100.0)
        self._volume_label.setText(f"{value}%")
        if value == 0:
            self._btn_mute.setText("\U0001f507")  # 🔇
        elif value < 50:
            self._btn_mute.setText("\U0001f509")  # 🔉
        else:
            self._btn_mute.setText("\U0001f50a")  # 🔊

    def _toggle_mute(self):
        if self._muted:
            self._volume_slider.setValue(self._pre_mute_volume)
            self._muted = False
        else:
            self._pre_mute_volume = self._volume_slider.value()
            self._volume_slider.setValue(0)
            self._muted = True

    def _volume_up(self):
        self._volume_slider.setValue(min(100, self._volume_slider.value() + 5))

    def _volume_down(self):
        self._volume_slider.setValue(max(0, self._volume_slider.value() - 5))

    # -----------------------------------------------------------------------
    # Seek
    # -----------------------------------------------------------------------

    def _on_seek_moved(self, position: int):
        self._time_current.setText(_format_ms(position))

    def _on_seek_released(self):
        self._is_user_seeking = False
        self._player.setPosition(self._seek_slider.value())

    def _on_position_changed(self, position: int):
        if not self._is_user_seeking:
            self._seek_slider.setValue(position)
            self._time_current.setText(_format_ms(position))

    def _on_duration_changed(self, duration: int):
        self._seek_slider.setRange(0, duration)
        self._time_total.setText(_format_ms(duration))

    # -----------------------------------------------------------------------
    # Media status
    # -----------------------------------------------------------------------

    def _on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.play_next()

    def _on_playback_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self._btn_play.setText("\u23f8")  # ⏸
        else:
            self._btn_play.setText("\u25b6")  # ▶

    # -----------------------------------------------------------------------
    # Search / filter
    # -----------------------------------------------------------------------

    def _filter_playlist(self, text: str):
        text = text.lower()
        for row in range(self._table.rowCount()):
            if not text:
                self._table.setRowHidden(row, False)
                continue
            match = False
            for col in range(1, 4):  # title, artist, album
                item = self._table.item(row, col)
                if item and text in item.text().lower():
                    match = True
                    break
            self._table.setRowHidden(row, not match)

    def _focus_search(self):
        self._search_edit.setFocus()
        self._search_edit.selectAll()

    # -----------------------------------------------------------------------
    # Table interactions
    # -----------------------------------------------------------------------

    def _on_table_double_click(self, index):
        self.play_track(index.row())

    def _on_table_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #2a2a2a; color: #ccc; border: 1px solid #444; }
            QMenu::item:selected { background-color: #0078d7; }
        """)
        act_play = menu.addAction("Play")
        act_remove = menu.addAction("Remove")
        act_clear = menu.addAction("Clear Playlist")

        action = menu.exec(self._table.mapToGlobal(pos))
        if action == act_play:
            rows = self._table.selectedIndexes()
            if rows:
                self.play_track(rows[0].row())
        elif action == act_remove:
            self.remove_selected()
        elif action == act_clear:
            self.clear_playlist()

    # -----------------------------------------------------------------------
    # System tray
    # -----------------------------------------------------------------------

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self._show_window()

    def _show_window(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def _quit_app(self):
        self._save_app_state()
        self._tray.hide()
        QApplication.quit()

    def _show_about(self):
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.about(
            self, "About MP3 Player",
            f"<h3>{APP_NAME}</h3>"
            "<p>Full-featured desktop audio player built with PyQt6.</p>"
            "<p><b>Shortcuts:</b></p>"
            "<ul>"
            "<li>Space — Play/Pause</li>"
            "<li>S — Stop</li>"
            "<li>N / Right — Next</li>"
            "<li>P / Left — Previous</li>"
            "<li>Up/Down — Volume</li>"
            "<li>M — Mute</li>"
            "<li>Ctrl+O — Add files</li>"
            "<li>Ctrl+Shift+O — Add folder</li>"
            "<li>Ctrl+F — Search</li>"
            "<li>Delete — Remove selected</li>"
            "<li>Ctrl+Q — Quit</li>"
            "</ul>"
        )

    # -----------------------------------------------------------------------
    # State persistence
    # -----------------------------------------------------------------------

    def _save_app_state(self):
        state = {
            "playlist": [t["path"] for t in self._playlist],
            "current_index": self._current_index,
            "position": self._player.position(),
            "volume": self._volume_slider.value(),
            "shuffle": self._shuffle,
            "repeat_mode": self._repeat_mode,
            "geometry": {
                "x": self.x(), "y": self.y(),
                "w": self.width(), "h": self.height(),
            },
        }
        _save_state(state)

    def _restore_state(self):
        state = _load_state()
        if not state:
            return
        # Window geometry
        geo = state.get("geometry")
        if geo:
            self.setGeometry(geo["x"], geo["y"], geo["w"], geo["h"])
        # Volume
        vol = state.get("volume", 80)
        self._volume_slider.setValue(vol)
        # Shuffle
        if state.get("shuffle", False):
            self._toggle_shuffle()
        # Repeat
        repeat = state.get("repeat_mode", "off")
        while self._repeat_mode != repeat:
            self._cycle_repeat()
        # Playlist
        paths = state.get("playlist", [])
        valid_paths = [p for p in paths if os.path.isfile(p)]
        if valid_paths:
            self._add_paths(valid_paths)
            idx = state.get("current_index", 0)
            if 0 <= idx < len(valid_paths):
                self._current_index = idx
                # Restore track display (will play on user action)
                QTimer.singleShot(500, lambda: self._restore_track(idx, state.get("position", 0)))

    def _restore_track(self, index: int, position: int):
        """Restore the track display after metadata loads, but don't auto-play."""
        if index < len(self._playlist):
            track = self._playlist[index]
            self._update_track_display(track)
            self._highlight_current_row()
            self._status.showMessage(f"Last track: {track['title']} — press Space to play")

    # -----------------------------------------------------------------------
    # Window events
    # -----------------------------------------------------------------------

    def closeEvent(self, event):
        self._save_app_state()
        self.hide()
        event.ignore()  # Minimize to tray instead of quitting


# ---------------------------------------------------------------------------
# Dark palette
# ---------------------------------------------------------------------------

def _apply_dark_theme(app: QApplication):
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Base, QColor(40, 40, 40))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(50, 50, 50))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(50, 50, 50))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.Button, QColor(50, 50, 50))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 50, 50))
    palette.setColor(QPalette.ColorRole.Link, QColor(0, 120, 215))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(120, 120, 120))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(120, 120, 120))
    app.setPalette(palette)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 9))
    app.setApplicationName(APP_NAME)
    app.setWindowIcon(_make_app_icon())
    _apply_dark_theme(app)

    # Prevent quit when closing window (tray keeps running)
    app.setQuitOnLastWindowClosed(False)

    window = MP3Player()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
