#!/usr/bin/env python3
# shutterstock_gui.py

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, 
                            QProgressBar, QLabel, QVBoxLayout, QWidget, QTextEdit,
                            QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from shutterstock_uploader import ShutterstockAutoUploader  # Import from second file

class UploaderWorker(QThread):
    progress_updated = pyqtSignal(int, str)
    status_updated = pyqtSignal(str, str, str, str)
    finished = pyqtSignal(dict)
    log_message = pyqtSignal(str)

    def __init__(self, directory_path):
        super().__init__()
        self.directory_path = directory_path
        self.uploader = ShutterstockAutoUploader()
        self.upload_ids = []

    def process_image(self, filename, image_path):
        """Process a single image with error handling"""
        try:
            # Step 1: Analyze image
            self.log_message.emit(f"Analyzing {filename}...")
            metadata = self.uploader.analyze_image_with_claude(image_path)
            
            if not metadata:
                return False, "Failed to analyze image"

            # Step 2: Validate metadata
            validation_result = self.uploader.validate_metadata(metadata)
            if not validation_result['success']:
                return False, validation_result['error']

            # Step 3: Submit to Shutterstock
            self.log_message.emit(f"Submitting {filename} to Shutterstock...")
            result = self.uploader.submit_to_shutterstock(image_path, metadata)
            
            if not result['success']:
                error_type = result.get('error_type', 'unknown')
                error_msg = result.get('error', 'Unknown error')
                return False, f"{error_type}: {error_msg}"

            return True, result.get('upload_id', '')

        except Exception as e:
            return False, str(e)

    def run(self):
        """Main worker thread execution"""
        image_files = [f for f in os.listdir(self.directory_path) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        total_files = len(image_files)
        successful = 0
        failed = 0

        for index, filename in enumerate(image_files, 1):
            image_path = os.path.join(self.directory_path, filename)
            progress = int((index / total_files) * 100)
            self.progress_updated.emit(progress, f"Processing {filename}...")
            
            success, result = self.process_image(filename, image_path)
            
            if success:
                successful += 1
                self.upload_ids.append(result)
                self.status_updated.emit(
                    filename,
                    result,
                    "Submitted",
                    "Successfully processed"
                )
            else:
                failed += 1
                self.status_updated.emit(
                    filename,
                    "",
                    "Failed",
                    result  # This contains the error message
                )

            self.log_message.emit(f"Completed processing {filename}")
            self.uploader.add_delay()  # Rate limiting

        self.finished.emit({"successful": successful, "failed": failed})

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shutterstock Auto Uploader")
        self.setMinimumSize(800, 600)
        self.initUI()

    def initUI(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create all widgets
        self.create_widgets()
        
        # Add widgets to layout
        self.add_widgets_to_layout(layout)

        self.selected_directory = None

    def create_widgets(self):
        """Create all UI widgets"""
        self.folder_label = QLabel("No folder selected")
        self.browse_button = QPushButton("Browse Folder")
        self.browse_button.clicked.connect(self.browse_folder)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)

        self.status_label = QLabel("Ready")
        
        self.status_table = QTableWidget()
        self.setup_status_table()

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)

        self.submit_button = QPushButton("Start Upload")
        self.submit_button.clicked.connect(self.start_upload)
        self.submit_button.setEnabled(False)

        self.refresh_button = QPushButton("Refresh Status")
        self.refresh_button.clicked.connect(self.refresh_status)
        self.refresh_button.setEnabled(False)

    def setup_status_table(self):
        """Setup the status table configuration"""
        self.status_table.setColumnCount(4)
        self.status_table.setHorizontalHeaderLabels([
            'Image', 'Upload ID', 'Status', 'Message'
        ])
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def add_widgets_to_layout(self, layout):
        """Add all widgets to the main layout"""
        widgets = [
            self.folder_label,
            self.browse_button,
            self.progress_bar,
            self.status_label,
            self.status_table,
            self.log_display,
            self.submit_button,
            self.refresh_button
        ]
        for widget in widgets:
            layout.addWidget(widget)

    def browse_folder(self):
        """Handle folder selection"""
        directory = QFileDialog.getExistingDirectory(self, "Select Images Directory")
        if directory:
            self.selected_directory = directory
            self.folder_label.setText(f"Selected: {directory}")
            self.submit_button.setEnabled(True)

    def start_upload(self):
        """Start the upload process"""
        if not self.selected_directory:
            return

        self.status_table.setRowCount(0)
        self.toggle_buttons(False)
        
        self.worker = UploaderWorker(self.selected_directory)
        self.connect_worker_signals()
        self.worker.start()

    def connect_worker_signals(self):
        """Connect all worker signals to their handlers"""
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.status_updated.connect(self.update_status_table)
        self.worker.finished.connect(self.upload_finished)
        self.worker.log_message.connect(self.log_message)

    def toggle_buttons(self, enabled):
        """Toggle button states"""
        self.browse_button.setEnabled(enabled)
        self.submit_button.setEnabled(enabled)
        self.refresh_button.setEnabled(not enabled)

    def update_progress(self, value, message):
        """Update progress bar and status message"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)

    def update_status_table(self, filename, upload_id, status, message):
        """Update the status table with new information"""
        row = self.status_table.rowCount()
        self.status_table.insertRow(row)
        self.status_table.setItem(row, 0, QTableWidgetItem(filename))
        self.status_table.setItem(row, 1, QTableWidgetItem(upload_id))
        self.status_table.setItem(row, 2, QTableWidgetItem(status))
        self.status_table.setItem(row, 3, QTableWidgetItem(message))

    def refresh_status(self):
        """Refresh the status of all uploads"""
        if hasattr(self, 'worker') and hasattr(self.worker, 'upload_ids'):
            for upload_id in self.worker.upload_ids:
                status = self.worker.uploader.check_submission_status(upload_id)
                if status:
                    self.update_status_in_table(upload_id, status)

    def update_status_in_table(self, upload_id, status_info):
        """Update a specific row in the status table"""
        for row in range(self.status_table.rowCount()):
            if self.status_table.item(row, 1).text() == upload_id:
                self.status_table.setItem(row, 2, QTableWidgetItem(status_info['status']))
                self.status_table.setItem(row, 3, QTableWidgetItem(status_info.get('message', '')))
                break

    def log_message(self, message):
        """Add a message to the log display"""
        self.log_display.append(message)

    def upload_finished(self, results):
        """Handle upload completion"""
        self.toggle_buttons(True)
        message = f"Upload completed. Successful: {results['successful']}, Failed: {results['failed']}"
        self.status_label.setText(message)
        QMessageBox.information(self, "Upload Complete", message)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
    