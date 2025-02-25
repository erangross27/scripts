"""
SVG Converter

This script provides a graphical user interface (GUI) for converting SVG files to raster image formats
(PNG, JPG, BMP) using PyQt5. The application allows users to select an input SVG file, choose an output
format and location, set the desired resolution, and perform the conversion.

Key features:
- Select input SVG file
- Choose output format (PNG, JPG, BMP)
- Set custom resolution
- Automatically detect and set resolution from input SVG
- Convert SVG to selected raster format

Dependencies:
- PyQt5
- sys
- os

Usage:
Run the script to launch the GUI application. Select an input SVG file, choose the output format and
location, adjust the resolution if needed, and click the "Convert" button to perform the conversion.

Classes:
- SVGConverter: Main application window class that handles the UI and conversion process.

Note: This script must be run in an environment with PyQt5 installed.
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFileDialog, QComboBox, QSpinBox, 
                             QMessageBox)
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import QRectF, Qt

class SVGConverter(QMainWindow):
    """
    Converts s v g.
    """
    def __init__(self):
        """
        Special method __init__.
        """
        super().__init__()
        self.initUI()

    def initUI(self):
        """
        Initui.
        """
        # Set up the main window
        self.setWindowTitle('SVG Converter')
        self.setGeometry(100, 100, 400, 250)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Input file selection
        self.input_line = QLineEdit()
        input_button = QPushButton('Select SVG', clicked=self.select_input)
        layout.addLayout(self.create_input_layout("Input SVG:", self.input_line, input_button))
        # Output file selection
        self.output_line = QLineEdit()
        output_button = QPushButton('Select Output', clicked=self.select_output)
        layout.addLayout(self.create_input_layout("Output File:", self.output_line, output_button))
        # Format selection
        self.format_combo = QComboBox()
        self.format_combo.addItems(['PNG', 'JPG', 'BMP'])
        self.format_combo.currentIndexChanged.connect(self.update_output_suffix)
        layout.addLayout(self.create_input_layout("Output Format:", self.format_combo))
        # Resolution selection
        self.width_spin = QSpinBox(minimum=1, maximum=10000)
        self.height_spin = QSpinBox(minimum=1, maximum=10000)
        layout.addLayout(self.create_resolution_layout())

        # Convert button
        convert_button = QPushButton('Convert', clicked=self.convert_svg)
        layout.addWidget(convert_button)

    def create_input_layout(self, label_text, *widgets):
        """
        Creates input layout based on label text.
        """
        # Create a horizontal layout for input fields
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label_text))
        for widget in widgets:
            layout.addWidget(widget)
        return layout

    def create_resolution_layout(self):
        """
        Creates resolution layout.
        """
        # Create a horizontal layout for resolution input
        layout = QHBoxLayout()
        layout.addWidget(QLabel('Resolution:'))
        layout.addWidget(self.width_spin)
        layout.addWidget(QLabel('x'))
        layout.addWidget(self.height_spin)
        return layout
    def select_input(self):
        """
        Select input.
        """
        # Open file dialog to select input SVG file
        file_name, _ = QFileDialog.getOpenFileName(self, 'Select SVG File', '', 'SVG Files (*.svg)')
        if file_name:
            self.input_line.setText(file_name)
            self.update_resolution_from_svg(file_name)

    def select_output(self):
        """
        Select output.
        """
        # Open file dialog to select output file location and name
        output_format = self.format_combo.currentText().lower()
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save Output File', '', 
                                                   f'{output_format.upper()} Files (*.{output_format});;All Files (*)')
        if file_name:
            self.output_line.setText(file_name)

    def update_resolution_from_svg(self, file_name):
        """
        Updates resolution from svg based on file name.
        """
        # Update resolution spinboxes based on the input SVG file
        renderer = QSvgRenderer(file_name)
        default_size = renderer.defaultSize()
        self.width_spin.setValue(default_size.width())
        self.height_spin.setValue(default_size.height())

    def update_output_suffix(self):
        """
        Updates output suffix.
        """
        # Update the output file suffix when the format is changed
        current_output = self.output_line.text()
        if current_output:
            base, _ = os.path.splitext(current_output)
            new_suffix = self.format_combo.currentText().lower()
            self.output_line.setText(f"{base}.{new_suffix}")

    def convert_svg(self):
        """
        Converts svg.
        """
        # Convert the SVG file to the selected format
        input_file = self.input_line.text()
        output_file = self.output_line.text()
        if not input_file or not output_file:
            QMessageBox.warning(self, "Input Error", "Please select both input and output files.")
            return

        output_format = self.format_combo.currentText().lower()
        width, height = self.width_spin.value(), self.height_spin.value()
        
        # Render SVG to image
        renderer = QSvgRenderer(input_file)
        image = QImage(width, height, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        with QPainter(image) as painter:
            renderer.render(painter, QRectF(0, 0, width, height))
        
        # Save the image
        if image.save(output_file, output_format):
            QMessageBox.information(self, "Success", f"Conversion successful. File saved as {output_file}")
        else:
            QMessageBox.critical(self, "Error", "Conversion failed.")

if __name__ == '__main__':
    # Create and run the application
    app = QApplication(sys.argv)
    converter = SVGConverter()
    converter.show()
    sys.exit(app.exec_())
