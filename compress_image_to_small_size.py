"""
Image Compressor GUI Application

This script provides a graphical user interface for compressing JPEG images.
It allows users to compress either a single image file or all images in a folder.
The application uses PyQt5 for the GUI and Pillow for image processing.

Features:
- Compress single JPEG image or all JPEG images in a folder
- Adjustable compression quality (1-100)
- Input and output path selection via file dialogs
- Real-time quality adjustment display
- Compression progress and results displayed in the GUI

Usage:
Run the script to launch the GUI application. Select the input (file or folder),
choose the output location, adjust the quality as needed, and click "Compress"
to start the compression process.

Dependencies:
- os
- sys
- PIL (Pillow)
- PyQt5

Classes:
- ImageCompressorGUI: Main application window and logic

Functions:
- compress_image: Compresses a single image file
- compress_images_in_folder: Compresses all JPEG images in a folder
"""

import os
import sys
from PIL import Image
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QSlider, QTextEdit, QFileDialog, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt

# Function to compress a single image
def compress_image(image_path, output_path, quality):
    with Image.open(image_path) as img:
        img.save(output_path, "JPEG", quality=quality, optimize=True)

# Function to compress all images in a folder
def compress_images_in_folder(folder_path, output_folder_path, quality=90):
    os.makedirs(output_folder_path, exist_ok=True)
    compressed_files = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg")):
            input_path = os.path.join(folder_path, filename)
            output_filename = f"{os.path.splitext(filename)[0]}_compressed.jpg"
            output_path = os.path.join(output_folder_path, output_filename)
            compress_image(input_path, output_path, quality)
            compressed_files.append(filename)

    return compressed_files

# Main GUI class for the Image Compressor
class ImageCompressorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    # Initialize the user interface
    def initUI(self):
        layout = QVBoxLayout()

        self.setup_radio_buttons(layout)
        self.setup_input_output(layout)
        self.setup_quality_slider(layout)
        self.setup_compress_button(layout)
        self.setup_output_text(layout)
        self.setLayout(layout)
        self.setWindowTitle('Image Compressor')
        self.setGeometry(300, 300, 400, 400)
        self.single_file_radio.setChecked(True)

    # Set up radio buttons for single file or folder selection
    def setup_radio_buttons(self, layout):
        radio_layout = QHBoxLayout()
        self.single_file_radio = QRadioButton("Single File")
        self.folder_radio = QRadioButton("Folder")
        button_group = QButtonGroup()
        button_group.addButton(self.single_file_radio)
        button_group.addButton(self.folder_radio)
        radio_layout.addWidget(self.single_file_radio)
        radio_layout.addWidget(self.folder_radio)
        layout.addLayout(radio_layout)

        self.single_file_radio.toggled.connect(self.clear_paths)
        self.folder_radio.toggled.connect(self.clear_paths)

    # Set up input and output fields with browse buttons
    def setup_input_output(self, layout):
        for label_text, attr_name in [("Input:", "input_edit"), ("Output:", "output_edit")]:
            io_layout = QHBoxLayout()
            io_layout.addWidget(QLabel(label_text))
            setattr(self, attr_name, QLineEdit())
            io_layout.addWidget(getattr(self, attr_name))
            browse_button = QPushButton("Browse")
            browse_button.clicked.connect(getattr(self, f"browse_{attr_name.split('_')[0]}"))
            io_layout.addWidget(browse_button)
            layout.addLayout(io_layout)

    # Set up quality slider
    def setup_quality_slider(self, layout):
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 100)
        self.quality_slider.setValue(90)
        quality_layout.addWidget(self.quality_slider)
        self.quality_label = QLabel("90")
        quality_layout.addWidget(self.quality_label)
        self.quality_slider.valueChanged.connect(self.update_quality_label)
        layout.addLayout(quality_layout)

    # Set up compress button
    def setup_compress_button(self, layout):
        self.compress_button = QPushButton("Compress")
        self.compress_button.clicked.connect(self.compress_images)
        layout.addWidget(self.compress_button)

    # Set up output text area
    def setup_output_text(self, layout):
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

    # Clear input and output paths when radio button selection changes
    def clear_paths(self):
        self.input_edit.clear()
        self.output_edit.clear()

    # Open file dialog for input selection
    def browse_input(self):
        if self.single_file_radio.isChecked():
            file, _ = QFileDialog.getOpenFileName(self, "Select Input File", "", "Image files (*.jpg *.jpeg)")
            if file:
                self.input_edit.setText(file)
        else:
            folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
            if folder:
                self.input_edit.setText(folder)

    # Open file dialog for output selection
    def browse_output(self):
        if self.single_file_radio.isChecked():
            file, _ = QFileDialog.getSaveFileName(self, "Save Output File", "", "JPEG (*.jpg)")
            if file:
                self.output_edit.setText(file)
        else:
            folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
            if folder:
                self.output_edit.setText(folder)

    # Update quality label when slider value changes
    def update_quality_label(self, value):
        self.quality_label.setText(str(value))

    # Compress images based on user input
    def compress_images(self):
        input_path = self.input_edit.text()
        output_path = self.output_edit.text()
        quality = self.quality_slider.value()

        if not input_path or not output_path:
            self.output_text.setText("Please select both input and output.")
            return

        try:
            if self.single_file_radio.isChecked():
                compress_image(input_path, output_path, quality)
                self.output_text.setText(f"Compressed image saved to {output_path}")
            else:
                compressed_files = compress_images_in_folder(input_path, output_path, quality)
                output = f"Compressed {len(compressed_files)} images:\n"
                output += "\n".join(f"- {file}" for file in compressed_files)
                output += "\nCompression completed!"
                self.output_text.setText(output)
        except Exception as e:
            self.output_text.setText(f"Error compressing: {str(e)}")

# Main entry point of the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageCompressorGUI()
    ex.show()
    sys.exit(app.exec_())