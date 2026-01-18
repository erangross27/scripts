import sys
import os
import subprocess
import platform
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QProgressBar, QFileDialog, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

class CompressorThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, input_file, output_file, power):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.power = power

    def run(self):
        try:
            # Determine Ghostscript command
            gs_command = None
            startupinfo = None
            
            if platform.system() == 'Windows':
                # Check for bundled Ghostscript (PyInstaller)
                if getattr(sys, 'frozen', False):
                    # Check internal temp dir (if bundled as --onefile)
                    bundled_gs = os.path.join(sys._MEIPASS, 'ghostscript', 'bin', 'gswin64c.exe')
                    if os.path.exists(bundled_gs):
                        gs_command = bundled_gs
                    else:
                        # Check next to the exe
                        local_gs = os.path.join(os.path.dirname(sys.executable), 'ghostscript', 'bin', 'gswin64c.exe')
                        if os.path.exists(local_gs):
                            gs_command = local_gs

                if not gs_command:
                    # Default to system PATH
                    gs_command = 'gswin64c'
                
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            else:
                gs_command = 'gs'
                startupinfo = None

            quality_settings = {
                0: '/default',
                1: '/prepress',
                2: '/printer',
                3: '/ebook',
                4: '/screen'
            }
            
            # Basic validation
            if not os.path.exists(self.input_file):
                self.finished_signal.emit(False, "Input file not found.")
                return

            # Construct command
            cmd = [
                gs_command, '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                f'-dPDFSETTINGS={quality_settings.get(self.power, "/ebook")}',
                '-dNOPAUSE', '-dQUIET', '-dBATCH',
                f'-sOutputFile={self.output_file}',
                self.input_file
            ]

            # Start process
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=startupinfo)
            
            # Simulate progress (since gs doesn't give percentage easily without parsing stdout/stderr elaborately)
            # We estimate based on file size (heuristic from original script)
            input_size = os.path.getsize(self.input_file)
            estimated_time = max(2, min(input_size / (1024 * 1024) * 0.5, 60)) # Cap at 60s for estimation
            
            start_time = time.time()
            while process.poll() is None:
                elapsed = time.time() - start_time
                progress = min(int((elapsed / estimated_time) * 100), 95)
                self.progress_signal.emit(progress)
                time.sleep(0.1)

            # Wait for file to be written
            wait_time = 0
            while (not os.path.exists(self.output_file) or os.path.getsize(self.output_file) == 0) and wait_time < 5:
                time.sleep(0.1)
                wait_time += 0.1

            if process.returncode == 0:
                self.progress_signal.emit(100)
                self.finished_signal.emit(True, "Compression successful!")
            else:
                stderr = process.stderr.read().decode('utf-8')
                self.finished_signal.emit(False, f"Ghostscript error: {stderr}")

        except FileNotFoundError:
            self.finished_signal.emit(False, f"Ghostscript executable '{gs_command}' not found. Please install Ghostscript.")
        except Exception as e:
            self.finished_signal.emit(False, str(e))

class PDFCompressorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Compressor (Qt)")
        self.setGeometry(100, 100, 600, 250)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Input File Selection
        input_layout = QHBoxLayout()
        input_label = QLabel("Input File:")
        self.input_entry = QLineEdit()
        input_btn = QPushButton("Select")
        input_btn.clicked.connect(self.select_input_file)
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_entry)
        input_layout.addWidget(input_btn)
        layout.addLayout(input_layout)

        # Output File Selection
        output_layout = QHBoxLayout()
        output_label = QLabel("Output File:")
        self.output_entry = QLineEdit()
        output_btn = QPushButton("Select")
        output_btn.clicked.connect(self.select_output_file)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_entry)
        output_layout.addWidget(output_btn)
        layout.addLayout(output_layout)

        # Quality Selection
        quality_layout = QHBoxLayout()
        quality_label = QLabel("Compression Level:")
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Default", "Prepress (High Quality)", "Printer", "Ebook (Medium)", "Screen (Low Quality)"])
        self.quality_combo.setCurrentIndex(3) # Default to Ebook
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_combo)
        layout.addLayout(quality_layout)

        # Progress Bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Compress Button
        self.compress_btn = QPushButton("Compress PDF")
        self.compress_btn.clicked.connect(self.start_compression)
        layout.addWidget(self.compress_btn)

    def select_input_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if filename:
            self.input_entry.setText(filename)
            # Auto-suggest output name
            base, ext = os.path.splitext(filename)
            self.output_entry.setText(f"{base}_compressed{ext}")

    def select_output_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Compressed PDF", self.output_entry.text(), "PDF Files (*.pdf)")
        if filename:
            self.output_entry.setText(filename)

    def start_compression(self):
        input_path = self.input_entry.text()
        output_path = self.output_entry.text()
        
        if not input_path or not output_path:
            QMessageBox.warning(self, "Warning", "Please select both input and output files.")
            return

        self.compress_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        power = self.quality_combo.currentIndex()
        
        self.thread = CompressorThread(input_path, output_path, power)
        self.thread.progress_signal.connect(self.update_progress)
        self.thread.finished_signal.connect(self.compression_finished)
        self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def compression_finished(self, success, message):
        self.compress_btn.setEnabled(True)
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PDFCompressorApp()
    window.show()
    sys.exit(app.exec())
