import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QFileDialog, QComboBox, QSpinBox, 
                             QMessageBox)
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtCore import QRectF

class SVGConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('SVG Converter')
        self.setGeometry(100, 100, 400, 250)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # Input file selection
        input_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        input_button = QPushButton('Select SVG')
        input_button.clicked.connect(self.select_input)
        input_layout.addWidget(QLabel('Input SVG:'))
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(input_button)
        layout.addLayout(input_layout)

        # Output file selection
        output_layout = QHBoxLayout()
        self.output_line = QLineEdit()
        output_button = QPushButton('Select Output')
        output_button.clicked.connect(self.select_output)
        output_layout.addWidget(QLabel('Output File:'))
        output_layout.addWidget(self.output_line)
        output_layout.addWidget(output_button)
        layout.addLayout(output_layout)

        # Format selection
        format_layout = QHBoxLayout()
        self.format_combo = QComboBox()
        self.format_combo.addItems(['PNG', 'JPG', 'BMP'])
        self.format_combo.currentIndexChanged.connect(self.update_output_suffix)
        format_layout.addWidget(QLabel('Output Format:'))
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)

        # Resolution selection
        resolution_layout = QHBoxLayout()
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 10000)
        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 10000)
        resolution_layout.addWidget(QLabel('Resolution:'))
        resolution_layout.addWidget(self.width_spin)
        resolution_layout.addWidget(QLabel('x'))
        resolution_layout.addWidget(self.height_spin)
        layout.addLayout(resolution_layout)

        # Convert button
        convert_button = QPushButton('Convert')
        convert_button.clicked.connect(self.convert_svg)
        layout.addWidget(convert_button)

        central_widget.setLayout(layout)

    def select_input(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Select SVG File', '', 'SVG Files (*.svg)')
        if file_name:
            self.input_line.setText(file_name)
            self.update_resolution_from_svg(file_name)

    def select_output(self):
        output_format = self.format_combo.currentText().lower()
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save Output File', '', 
                                                   f'{output_format.upper()} Files (*.{output_format});;All Files (*)')
        if file_name:
            self.output_line.setText(file_name)

    def update_resolution_from_svg(self, file_name):
        renderer = QSvgRenderer(file_name)
        default_size = renderer.defaultSize()
        self.width_spin.setValue(default_size.width())
        self.height_spin.setValue(default_size.height())

    def update_output_suffix(self):
        current_output = self.output_line.text()
        if current_output:
            base, _ = os.path.splitext(current_output)
            new_suffix = self.format_combo.currentText().lower()
            self.output_line.setText(f"{base}.{new_suffix}")

    def convert_svg(self):
        input_file = self.input_line.text()
        output_file = self.output_line.text()
        output_format = self.format_combo.currentText().lower()
        width = self.width_spin.value()
        height = self.height_spin.value()

        if not input_file or not output_file:
            QMessageBox.warning(self, "Input Error", "Please select both input and output files.")
            return

        renderer = QSvgRenderer(input_file)
        image = QImage(width, height, QImage.Format_ARGB32)
        image.fill(0x00000000)
        painter = QPainter(image)
        renderer.render(painter, QRectF(0, 0, width, height))
        painter.end()

        if image.save(output_file, output_format):
            QMessageBox.information(self, "Success", f"Conversion successful. File saved as {output_file}")
        else:
            QMessageBox.critical(self, "Error", "Conversion failed.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    converter = SVGConverter()
    converter.show()
    sys.exit(app.exec_())
