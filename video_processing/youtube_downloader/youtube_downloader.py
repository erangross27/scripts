import sys
import os
import tempfile
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                           QComboBox, QFileDialog, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from yt_dlp import YoutubeDL

class DownloaderThread(QThread):
    progress = pyqtSignal(float, str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, url, save_path, format_type):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.format_type = format_type
        
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                if d.get('total_bytes'):
                    # Total size is known
                    percentage = (d['downloaded_bytes'] / d['total_bytes']) * 100
                elif d.get('total_bytes_estimate'):
                    # Total size is estimated
                    percentage = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                else:
                    # Fall back to downloaded percentage if available
                    percentage = float(d.get('downloaded_percent', 0))
                
                # Get download speed and ETA
                if d.get('speed'):
                    speed = d['speed'] / 1024 / 1024  # Convert to MB/s
                    speed_text = f"{speed:.1f} MB/s"
                else:
                    speed_text = "-- MB/s"
                
                if d.get('eta'):
                    eta = d['eta']
                    eta_text = f"ETA: {eta}s"
                else:
                    eta_text = "ETA: --"

                status_text = f"Downloading... {speed_text} {eta_text}"
                self.progress.emit(percentage, status_text)
            except:
                pass
                
        elif d['status'] == 'finished':
            self.progress.emit(95, "Converting...")  # Show converting status
                
    def run(self):
        try:
            # Create a temporary directory for cache
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
                    'format': 'best[ext=mp4]',
                    'progress_hooks': [self.progress_hook],
                    'outtmpl': output_template,
                    'cachedir': cache_dir,
                }
                
            with YoutubeDL(ydl_opts) as ydl:
                self.progress.emit(0, "Starting download...")
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
        self.setMinimumSize(800, 250)
        
        # Set Windows-style font
        app = QApplication.instance()
        app.setFont(QFont('Segoe UI', 9))
        
        # Create central widget and layout
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
        
        # Format selection
        format_layout = QHBoxLayout()
        format_label = QLabel('Format:')
        self.format_combo = QComboBox()
        self.format_combo.addItems(['MP3', 'MP4'])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        layout.addLayout(format_layout)
        
        # Status label
        self.status_label = QLabel('')
        self.status_label.setAlignment(Qt.AlignCenter)
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
        self.progress_bar.setAlignment(Qt.AlignCenter)
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
        
        # Add some stretch at the bottom
        layout.addStretch()
        
    def browse_location(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Save Location")
        if folder:
            self.save_input.setText(folder)
            
    def start_download(self):
        url = self.url_input.text().strip()
        save_path = self.save_input.text().strip()
        format_type = self.format_combo.currentText()
        
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a YouTube URL")
            return
            
        if not save_path:
            QMessageBox.warning(self, "Error", "Please select a save location")
            return
            
        self.download_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Initializing...")
        
        # Create and start the downloader thread
        self.downloader = DownloaderThread(url, save_path, format_type)
        self.downloader.progress.connect(self.update_progress)
        self.downloader.finished.connect(self.download_finished)
        self.downloader.start()
        
    def update_progress(self, percentage, status_text):
        # Ensure percentage is between 0 and 100
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
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()