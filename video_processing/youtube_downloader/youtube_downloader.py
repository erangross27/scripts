"""
This script downloads content related to youtube.
"""

import sys
import os
import shutil
import tempfile
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                           QHBoxLayout, QLabel, QLineEdit, QPushButton,
                           QComboBox, QFileDialog, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from yt_dlp import YoutubeDL


def _find_ffmpeg():
    """Find ffmpeg location. Check common install paths on Windows."""
    # Check if ffmpeg is already in PATH
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return os.path.dirname(ffmpeg_path)

    # Check bundled (same directory as this script / exe)
    app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    if os.path.isfile(os.path.join(app_dir, 'ffmpeg.exe')):
        return app_dir

    # Check common Windows install paths
    for path in [
        os.path.join(os.environ.get('ProgramFiles', r'C:\Program Files'), 'ffmpeg', 'bin'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Links'),
        r'C:\ffmpeg\bin',
    ]:
        if os.path.isfile(os.path.join(path, 'ffmpeg.exe')):
            return path

    return None


class DownloaderThread(QThread):
    """
    Represents a downloader thread.
    """
    progress = pyqtSignal(float, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, url, save_path, format_type, browser_for_cookies):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.format_type = format_type
        self.browser_for_cookies = browser_for_cookies

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                if d.get('total_bytes'):
                    percentage = (d['downloaded_bytes'] / d['total_bytes']) * 100
                elif d.get('total_bytes_estimate'):
                    percentage = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                else:
                    percentage = float(d.get('downloaded_percent', 0))

                if d.get('speed'):
                    speed = d['speed'] / 1024 / 1024
                    speed_text = f"{speed:.1f} MB/s"
                else:
                    speed_text = "-- MB/s"

                if d.get('eta'):
                    eta_text = f"ETA: {d['eta']}s"
                else:
                    eta_text = "ETA: --"

                self.progress.emit(percentage, f"Downloading... {speed_text} {eta_text}")
            except:
                pass
        elif d['status'] == 'finished':
            self.progress.emit(95, "Converting...")

    def _build_opts(self):
        cache_dir = os.path.join(tempfile.gettempdir(), 'yt_dlp_cache')
        os.makedirs(cache_dir, exist_ok=True)

        output_template = os.path.join(self.save_path, '%(title)s.%(ext)s')

        if self.format_type == "MP3":
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'progress_hooks': [self.progress_hook],
                'outtmpl': output_template,
                'cachedir': cache_dir,
            }
        else:  # MP4
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'merge_output_format': 'mp4',
                'progress_hooks': [self.progress_hook],
                'outtmpl': output_template,
                'cachedir': cache_dir,
            }

        # Only download the single video, not the whole playlist
        ydl_opts['noplaylist'] = True

        # Set ffmpeg location
        ffmpeg_dir = _find_ffmpeg()
        if ffmpeg_dir:
            ydl_opts['ffmpeg_location'] = ffmpeg_dir

        return ydl_opts

    def run(self):
        try:
            ydl_opts = self._build_opts()

            # Try with browser cookies if selected
            if self.browser_for_cookies and self.browser_for_cookies != "None":
                ydl_opts['cookiesfrombrowser'] = (self.browser_for_cookies.lower(),)
                try:
                    self.progress.emit(0, "Starting download (with cookies)...")
                    with YoutubeDL(ydl_opts) as ydl:
                        ydl.download([self.url])
                    self.progress.emit(100, "Completed!")
                    self.finished.emit(True, "Download completed successfully!")
                    return
                except Exception as cookie_err:
                    cookie_msg = str(cookie_err)
                    if 'cookie' in cookie_msg.lower():
                        # Cookie access failed, retry without cookies
                        self.progress.emit(0, "Cookie access failed, retrying without...")
                        ydl_opts.pop('cookiesfrombrowser', None)
                    else:
                        raise

            self.progress.emit(0, "Starting download...")
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])

            self.progress.emit(100, "Completed!")
            self.finished.emit(True, "Download completed successfully!")
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")


class YouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('YouTube Downloader')
        self.setMinimumSize(800, 300)

        app = QApplication.instance()
        app.setFont(QFont('Segoe UI', 9))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # URL input
        url_layout = QHBoxLayout()
        url_label = QLabel('YouTube URL:')
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('Paste YouTube URL here...')
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Save location
        save_layout = QHBoxLayout()
        save_label = QLabel('Save Location:')
        self.save_input = QLineEdit()
        self.save_input.setText(os.path.join(os.path.expanduser('~'), 'Downloads'))
        browse_btn = QPushButton('Browse')
        browse_btn.clicked.connect(self.browse_location)
        save_layout.addWidget(save_label)
        save_layout.addWidget(self.save_input)
        save_layout.addWidget(browse_btn)
        layout.addLayout(save_layout)

        # Format and Browser selection row
        options_layout = QHBoxLayout()

        format_label = QLabel('Format:')
        self.format_combo = QComboBox()
        self.format_combo.addItems(['MP3', 'MP4'])
        options_layout.addWidget(format_label)
        options_layout.addWidget(self.format_combo)

        options_layout.addSpacing(20)

        browser_label = QLabel('Use cookies from:')
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(['None', 'Chrome', 'Edge', 'Firefox'])
        self.browser_combo.setToolTip(
            'For age-restricted or member-only videos,\n'
            'select a browser where you are logged into YouTube.\n'
            'Close the browser first for best results.\n'
            'Most videos work fine without cookies.'
        )
        options_layout.addWidget(browser_label)
        options_layout.addWidget(self.browser_combo)

        options_layout.addStretch()
        layout.addLayout(options_layout)

        # Status label
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
            }
        """)
        self.progress_bar.setFormat('%p%')
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.progress_bar)

        # Download button
        self.download_btn = QPushButton('Download')
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        layout.addStretch()

    def browse_location(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Location")
        if folder:
            self.save_input.setText(folder)

    def start_download(self):
        url = self.url_input.text().strip()
        save_path = self.save_input.text().strip()
        format_type = self.format_combo.currentText()
        browser_for_cookies = self.browser_combo.currentText()

        if not url:
            QMessageBox.warning(self, "Error", "Please enter a YouTube URL")
            return

        if not save_path:
            QMessageBox.warning(self, "Error", "Please select a save location")
            return

        self.download_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Initializing...")

        self.downloader = DownloaderThread(url, save_path, format_type, browser_for_cookies)
        self.downloader.progress.connect(self.update_progress)
        self.downloader.finished.connect(self.download_finished)
        self.downloader.start()

    def update_progress(self, percentage, status_text):
        percentage = max(0, min(100, percentage))
        self.progress_bar.setValue(int(percentage))
        self.status_label.setText(status_text)

    def download_finished(self, success, message):
        self.download_btn.setEnabled(True)
        if success:
            self.status_label.setText("Completed!")
            QMessageBox.information(self, "Success", message)
            self.url_input.clear()
        else:
            self.status_label.setText("Error occurred!")
            QMessageBox.warning(self, "Error", message)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
