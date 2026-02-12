"""
PDF Page Numberer

This script provides a graphical user interface for adding page numbers to PDF documents.
It allows users to open a PDF file, customize the appearance and position of page numbers,
preview the changes, and save the numbered PDF.

Features:
- Open and preview PDF files
- Customize page number position (left, center, right)
- Set page number color
- Adjust footer offset
- Set starting page number
- Change font size
- Adjust horizontal and vertical offsets
- Preview changes in real-time
- Process and save the numbered PDF

Dependencies:
- PyQt5: For creating the graphical user interface
- PyMuPDF (fitz): For PDF manipulation

Usage:
Run the script and use the GUI to open a PDF, adjust settings, and save the numbered PDF.

Note: This script requires PyQt5 and PyMuPDF to be installed.
"""

import sys
import fitz
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QScrollArea, QComboBox, QColorDialog, QSpinBox, QFrame, QFormLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QColor, QPainter, QFont, QPen

# Custom widget to display the selected color
class ColorIndicator(QFrame):
    """
    Represents a color indicator.
    """
    def __init__(self, color=Qt.GlobalColor.black):
        """
        Special method __init__.
        """
        super().__init__()
        self.color = color
        self.setFixedSize(20, 20)

    def setColor(self, color):
        """
        Setcolor based on color.
        """
        self.color = color
        self.update()

    def paintEvent(self, event):
        """
        Paintevent based on event.
        """
        painter = QPainter(self)
        painter.fillRect(self.rect(), self.color)

# Main application window
class PDFNumberer(QMainWindow):
    """
    Represents a p d f numberer.
    """
    def __init__(self):
        """
        Special method __init__.
        """
        super().__init__()
        self.pdf_document = None
        self.number_position = 'right'
        self.number_color = QColor(0, 0, 0)  # Default black
        self.footer_offset = 20
        self.start_number = 1
        self.font_size = 12
        self.is_preview_mode = True
        self.initUI()
        self.showMaximized()

    def initUI(self):
        """
        Initui.
        """
        # Set up the main window and layout
        self.setWindowTitle('PDF Page Numberer')
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Create left sidebar for buttons and controls
        sidebar_layout = QVBoxLayout()
        sidebar_widget = QWidget()
        sidebar_widget.setLayout(sidebar_layout)
        sidebar_widget.setFixedWidth(250)  # Set a fixed width for the sidebar
        main_layout.addWidget(sidebar_widget)

        # Add buttons to sidebar
        open_button = QPushButton('Open PDF')
        open_button.clicked.connect(self.open_pdf)
        sidebar_layout.addWidget(open_button)

        process_button = QPushButton('Process PDF')
        process_button.clicked.connect(self.process_pdf)
        sidebar_layout.addWidget(process_button)

        sidebar_layout.addSpacing(20)  # Add some space between buttons and controls

        # Add controls to sidebar
        controls_layout = QFormLayout()  # Use QFormLayout for label-widget pairs
        sidebar_layout.addLayout(controls_layout)

        # Number position dropdown
        self.position_combo = QComboBox()
        self.position_combo.addItems(['Left', 'Center', 'Right'])
        self.position_combo.setCurrentText('Right')
        self.position_combo.currentTextChanged.connect(self.update_preview)
        controls_layout.addRow("Number Position:", self.position_combo)

        # Color selection button and indicator
        color_layout = QHBoxLayout()
        color_button = QPushButton('Color')
        color_button.clicked.connect(self.select_color)
        color_button.setFixedWidth(60)  # Make the color button smaller
        color_layout.addWidget(color_button)
        self.color_indicator = ColorIndicator(self.number_color)
        color_layout.addWidget(self.color_indicator)
        controls_layout.addRow("Number Color:", color_layout)

        # Footer offset control
        self.footer_offset_spin = QSpinBox()
        self.footer_offset_spin.setRange(0, 100)
        self.footer_offset_spin.setValue(20)
        self.footer_offset_spin.valueChanged.connect(self.update_preview)
        controls_layout.addRow("Footer Offset:", self.footer_offset_spin)

        # Start number control
        self.start_number_spin = QSpinBox()
        self.start_number_spin.setRange(1, 9999)
        self.start_number_spin.setValue(1)
        self.start_number_spin.valueChanged.connect(self.update_preview)
        controls_layout.addRow("Start Number:", self.start_number_spin)

        # Font size control
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(6, 72)
        self.font_size_spin.setValue(12)
        self.font_size_spin.valueChanged.connect(self.update_preview)
        controls_layout.addRow("Font Size:", self.font_size_spin)

        # Horizontal offset control
        self.horizontal_offset_spin = QSpinBox()
        self.horizontal_offset_spin.setRange(-500, 500)
        self.horizontal_offset_spin.setValue(50)
        self.horizontal_offset_spin.valueChanged.connect(self.update_preview)
        controls_layout.addRow("Horizontal Offset:", self.horizontal_offset_spin)

        # Vertical offset control
        self.vertical_offset_spin = QSpinBox()
        self.vertical_offset_spin.setRange(-500, 500)
        self.vertical_offset_spin.setValue(20)
        self.vertical_offset_spin.valueChanged.connect(self.update_preview)
        controls_layout.addRow("Vertical Offset:", self.vertical_offset_spin)

        sidebar_layout.addStretch()  # Push everything to the top

        # Create scroll area for PDF content
        self.scroll_area = QScrollArea()
        main_layout.addWidget(self.scroll_area)
        self.scroll_area.setWidgetResizable(True)

        self.content_widget = QWidget()
        self.scroll_area.setWidget(self.content_widget)
        self.content_layout = QVBoxLayout(self.content_widget)

        # Add a placeholder message
        self.placeholder_label = QLabel("No PDF opened. Please open a PDF file.")
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.placeholder_label)

    # Method to handle color selection
    def select_color(self):
        """
        Select color.
        """
        color = QColorDialog.getColor()
        if color.isValid():
            self.number_color = color
            self.color_indicator.setColor(color)
            self.update_preview()

    # Method to open a PDF file
    def open_pdf(self):
        """
        Open pdf.
        """
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open PDF File', '', 'PDF Files (*.pdf)')
        if file_name:
            self.pdf_document = fitz.open(file_name)
            self.is_preview_mode = True
            self.update_preview()

    # Method to update the preview of the PDF with page numbers
    def update_preview(self):
        """
        Updates preview.
        """
        if not self.pdf_document:
            return

        # Clear previous content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Loop through each page of the PDF
        for page_num in range(len(self.pdf_document)):
            page = self.pdf_document[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Increase resolution
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(img)

            if self.is_preview_mode:
                # Create a copy of the pixmap to draw on
                preview_pixmap = pixmap.copy()
                painter = QPainter(preview_pixmap)
                
                # Set the pen color explicitly to black for preview
                painter.setPen(QPen(Qt.GlobalColor.black))
                
                font = QFont()
                font.setPointSize(self.font_size_spin.value())
                painter.setFont(font)

                number = self.start_number_spin.value() + page_num
                text = f"{number}"

                # Calculate position based on selected alignment
                if self.position_combo.currentText() == 'Left':
                    x = self.horizontal_offset_spin.value()
                elif self.position_combo.currentText() == 'Center':
                    x = preview_pixmap.width() // 2
                else:  # Right
                    x = preview_pixmap.width() - self.horizontal_offset_spin.value()

                y = preview_pixmap.height() - self.vertical_offset_spin.value()

                painter.drawText(x, y, text)
                painter.end()
            else:
                preview_pixmap = pixmap

            # Create and add image label to the layout
            image_label = QLabel()
            image_label.setPixmap(preview_pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Add page number label
            page_label = QLabel(f'Page: {page_num + 1} / {len(self.pdf_document)}')
            page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.content_layout.addWidget(page_label)
            self.content_layout.addWidget(image_label)

    # Method to process the PDF and add page numbers
    def process_pdf(self):
        """
        Process pdf.
        """
        if not self.pdf_document:
            QMessageBox.warning(self, 'Warning', 'Please open a PDF file first.')
            return

        # Create a temporary copy of the PDF to work on
        temp_pdf = fitz.open()
        temp_pdf.insert_pdf(self.pdf_document)

        # Loop through each page and add page numbers
        for page_num in range(len(temp_pdf)):
            page = temp_pdf[page_num]
            number = self.start_number_spin.value() + page_num
            text = f"{number}"

            rect = page.rect
            # Calculate position based on selected alignment
            if self.position_combo.currentText() == 'Left':
                point = fitz.Point(self.horizontal_offset_spin.value(), rect.height - self.vertical_offset_spin.value())
            elif self.position_combo.currentText() == 'Center':
                point = fitz.Point(rect.width / 2, rect.height - self.vertical_offset_spin.value())
            else:  # Right
                point = fitz.Point(rect.width - self.horizontal_offset_spin.value(), rect.height - self.vertical_offset_spin.value())

            # Convert RGB values to the range 0-1
            color = (self.number_color.red() / 255,
                     self.number_color.green() / 255,
                     self.number_color.blue() / 255)

            page.insert_text(point, text, fontsize=self.font_size_spin.value(), color=color)

        # Save the numbered PDF
        save_name, _ = QFileDialog.getSaveFileName(self, 'Save Numbered PDF', '', 'PDF Files (*.pdf)')
        if save_name:
            temp_pdf.save(save_name)
            QMessageBox.information(self, 'Success', 'PDF has been numbered and saved.')

            # Close the old document and open the new one
            self.pdf_document.close()
            self.pdf_document = fitz.open(save_name)
            self.is_preview_mode = False  # Switch off preview mode
            self.update_preview()
        else:
            # If user cancels save, discard changes
            temp_pdf.close()

# Main entry point of the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PDFNumberer()
    window.show()
    sys.exit(app.exec())
