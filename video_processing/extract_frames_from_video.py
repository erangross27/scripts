"""
Multi-Video Frame Extractor

This script provides a graphical user interface for extracting frames from multiple video files.
It allows users to select video files, choose an output folder, and specify extraction parameters.
The application uses PyQt5 for the GUI and OpenCV for video processing.

Key features:
- Select multiple video files for frame extraction
- Choose output folder for extracted frames
- Two extraction modes: extract every N frames or extract X frames per video
- Set maximum number of frames to extract per video
- Progress bar and status updates during extraction
- Multithreaded extraction process to keep UI responsive

Classes:
- FrameExtractor: A QThread subclass that handles the frame extraction process
- App: The main application window, inheriting from QWidget

Usage:
Run this script directly to launch the graphical user interface.
Select video files, set extraction parameters, and click "Extract Frames" to begin the process.

Dependencies:
- PyQt5
- OpenCV (cv2)
- sys
- os

Author: [Eran Gross]
Date: [30/08/2024]
Version: 1.0
"""

import sys
import cv2
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QLabel, QSpinBox, QProgressBar, QListWidget, QHBoxLayout, QRadioButton, QButtonGroup
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# FrameExtractor class for extracting frames from videos
class FrameExtractor(QThread):
    progress_update = pyqtSignal(int)
    file_progress = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, video_paths, output_folder, extraction_mode, extraction_value, max_frames):
        super().__init__()
        self.video_paths = video_paths
        self.output_folder = output_folder
        self.extraction_mode = extraction_mode
        self.extraction_value = extraction_value
        self.max_frames = max_frames

    def run(self):
        total_saved_count = 0
        total_frames_to_extract = sum(min(self.get_frame_count(video_path), self.max_frames) for video_path in self.video_paths)

        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        for video_path in self.video_paths:
            self.file_progress.emit(f"Processing: {os.path.basename(video_path)}")
            
            video = cv2.VideoCapture(video_path)
            total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

            if self.extraction_mode == "interval":
                frame_indices = range(0, total_frames, self.extraction_value)
            else:  # "total_frames" mode
                frame_indices = [int(i * total_frames / self.extraction_value) for i in range(self.extraction_value)]

            frame_indices = frame_indices[:min(len(frame_indices), self.max_frames)]

            for frame_index in frame_indices:
                video.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
                ret, frame = video.read()
                if not ret:
                    break

                video_name = os.path.splitext(os.path.basename(video_path))[0]
                output_path = os.path.join(self.output_folder, f"{video_name}_frame_{total_saved_count:04d}.jpg")
                cv2.imwrite(output_path, frame)
                total_saved_count += 1

                self.progress_update.emit(int(total_saved_count / total_frames_to_extract * 100))

            video.release()

        self.finished.emit()

    def get_frame_count(self, video_path):
        video = cv2.VideoCapture(video_path)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        video.release()
        return total_frames

# Main application class
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set up the main window
        self.setWindowTitle('Multi-Video Frame Extractor')
        self.setGeometry(300, 300, 500, 500)

        layout = QVBoxLayout()

        # Button to select video files
        self.video_btn = QPushButton('Select Video Files', self)
        self.video_btn.clicked.connect(self.select_videos)
        layout.addWidget(self.video_btn)

        # List to display selected video files
        self.video_list = QListWidget(self)
        layout.addWidget(self.video_list)

        # Button to select output folder
        self.output_btn = QPushButton('Select Output Folder', self)
        self.output_btn.clicked.connect(self.select_output)
        layout.addWidget(self.output_btn)

        # Label to display selected output folder
        self.output_label = QLabel('No output folder selected', self)
        layout.addWidget(self.output_label)

        # Radio buttons for extraction mode
        extraction_layout = QHBoxLayout()
        self.interval_radio = QRadioButton("Extract every N frames")
        self.total_frames_radio = QRadioButton("Extract X frames per video")
        self.extraction_group = QButtonGroup()
        self.extraction_group.addButton(self.interval_radio)
        self.extraction_group.addButton(self.total_frames_radio)
        self.interval_radio.setChecked(True)
        extraction_layout.addWidget(self.interval_radio)
        extraction_layout.addWidget(self.total_frames_radio)
        layout.addLayout(extraction_layout)

        # Spin box for extraction value
        self.extraction_spin = QSpinBox(self)
        self.extraction_spin.setRange(1, 1000)
        self.extraction_spin.setValue(30)
        layout.addWidget(self.extraction_spin)

        # Label and spin box for max frames per video
        self.max_frames_label = QLabel('Max frames per video:', self)
        layout.addWidget(self.max_frames_label)

        self.max_frames_spin = QSpinBox(self)
        self.max_frames_spin.setRange(1, 10000)
        self.max_frames_spin.setValue(1000)
        layout.addWidget(self.max_frames_spin)

        # Button to start frame extraction
        self.extract_btn = QPushButton('Extract Frames', self)
        self.extract_btn.clicked.connect(self.extract_frames)
        layout.addWidget(self.extract_btn)

        # Progress bar for extraction progress
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # Label for status updates
        self.status_label = QLabel('', self)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def select_videos(self):
        # Open file dialog to select video files
        file_names, _ = QFileDialog.getOpenFileNames(self, "Select Video Files", "", "Video Files (*.mp4)")
        if file_names:
            self.video_list.clear()
            self.video_list.addItems(file_names)

    def select_output(self):
        # Open folder dialog to select output folder
        folder_name = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder_name:
            self.output_label.setText(folder_name)

    def extract_frames(self):
        # Gather input parameters and start frame extraction
        video_paths = [self.video_list.item(i).text() for i in range(self.video_list.count())]
        output_folder = self.output_label.text()
        extraction_value = self.extraction_spin.value()
        max_frames = self.max_frames_spin.value()

        if not video_paths or output_folder == 'No output folder selected':
            return

        extraction_mode = "interval" if self.interval_radio.isChecked() else "total_frames"
        self.extractor = FrameExtractor(video_paths, output_folder, extraction_mode, extraction_value, max_frames)
        self.extractor.progress_update.connect(self.update_progress)
        self.extractor.file_progress.connect(self.update_status)
        self.extractor.finished.connect(self.extraction_finished)
        self.extractor.start()
        self.extract_btn.setEnabled(False)

    def update_progress(self, value):
        # Update progress bar
        self.progress_bar.setValue(value)

    def update_status(self, status):
        # Update status label
        self.status_label.setText(status)
    def extraction_finished(self):
        # Handle completion of frame extraction
        self.progress_bar.setValue(100)
        self.extract_btn.setEnabled(True)
        self.status_label.setText("Extraction completed!")

# Main execution
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
