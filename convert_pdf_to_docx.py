from docx import Document
from pdf2docx import Converter
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QProgressBar, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal

class ConversionThread(QThread):
    progress_updated = pyqtSignal(int)
    conversion_completed = pyqtSignal(bool, str)

    def __init__(self, pdf_path, output_path):
        super().__init__()
        self.pdf_path = pdf_path
        self.output_path = output_path

    def run(self):
        try:
            # Create a converter object
            converter = Converter(self.pdf_path)

            # Convert the PDF to Word document
            converter.convert(self.output_path, start=0, end=None)
            converter.close()

            self.conversion_completed.emit(True, "")
        except Exception as e:
            error_message = f"Error occurred during conversion: {str(e)}"
            print(error_message)
            self.conversion_completed.emit(False, error_message)

class PDFToWordConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF to Word Converter")
        self.setGeometry(100, 100, 400, 200)
        
        # Create labels and line edits for file paths
        self.pdf_label = QLabel("PDF File:")
        self.pdf_path = QLineEdit()
        self.pdf_browse = QPushButton("Browse")
        self.pdf_browse.clicked.connect(self.browse_pdf)
        
        self.output_label = QLabel("Output File:")
        self.output_path = QLineEdit()
        self.output_browse = QPushButton("Browse")
        self.output_browse.clicked.connect(self.browse_output)
        
        # Create convert button and progress bar
        self.convert_button = QPushButton("Convert")
        self.convert_button.clicked.connect(self.convert_pdf_to_word)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Create layout
        layout = QVBoxLayout()
        
        pdf_layout = QHBoxLayout()
        pdf_layout.addWidget(self.pdf_label)
        pdf_layout.addWidget(self.pdf_path)
        pdf_layout.addWidget(self.pdf_browse)
        
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(self.output_browse)
        
        layout.addLayout(pdf_layout)
        layout.addLayout(output_layout)
        layout.addWidget(self.convert_button)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
    
    def browse_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF File", "", "PDF Files (*.pdf)")
        if file_path:
            self.pdf_path.setText(file_path)
    
    def browse_output(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Word Document", "", "Word Documents (*.docx)")
        if file_path:
            self.output_path.setText(file_path)
    
    def convert_pdf_to_word(self):
        pdf_path = self.pdf_path.text()
        output_path = self.output_path.text()
        
        if not pdf_path or not output_path:
            QMessageBox.warning(self, "Error", "Please provide both PDF and output file paths.")
            return
        
        self.convert_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        
        self.conversion_thread = ConversionThread(pdf_path, output_path)
        self.conversion_thread.progress_updated.connect(self.update_progress)
        self.conversion_thread.conversion_completed.connect(self.conversion_finished)
        self.conversion_thread.start()
    
    def update_progress(self, progress):
        self.progress_bar.setValue(progress)
    
    def conversion_finished(self, success, error_message):
        self.convert_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            QMessageBox.information(self, "Success", "PDF converted to Word document successfully!")
        else:
            QMessageBox.critical(self, "Error", error_message)

if __name__ == "__main__":
    app = QApplication([])
    converter = PDFToWordConverter()
    converter.show()
    app.exec_()
