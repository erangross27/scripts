"""
This script implements convertor functionality that processes images.
"""

# Import required libraries
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog,
                            QLabel, QVBoxLayout, QHBoxLayout, QWidget)
from PyQt5.QtCore import Qt
from PIL import Image

# Main window class
class ImageConverter(QMainWindow):
    """
    Converts image.
    """
    def __init__(self):
        """
        Special method __init__.
        """
        # Initialize the main window
        super().__init__()
        self.setWindowTitle("WebP Image Converter")  # Set window title
        self.setGeometry(100, 100, 800, 400)  # Set window size and position
        
        # Create main widget and layout
        main_widget = QWidget()  # Create main widget container
        self.setCentralWidget(main_widget)  # Set it as central widget
        layout = QVBoxLayout(main_widget)  # Create vertical layout
        
        # Create source file selection layout
        source_layout = QHBoxLayout()  # Horizontal layout for source selection
        self.source_label = QLabel("No file selected")  # Label to show selected file
        self.source_button = QPushButton("Select WebP File")  # Button to trigger file selection
        self.source_button.clicked.connect(self.select_source)  # Connect button to function
        source_layout.addWidget(QLabel("Source File:"))  # Add label
        source_layout.addWidget(self.source_label)  # Add file path label
        source_layout.addWidget(self.source_button)  # Add selection button
        
        # Create destination selection layout
        dest_layout = QHBoxLayout()  # Horizontal layout for destination
        self.dest_label = QLabel("No destination selected")  # Label to show save location
        self.dest_button = QPushButton("Save As...")  # Button to select save location
        self.dest_button.clicked.connect(self.select_destination)  # Connect button to function
        dest_layout.addWidget(QLabel("Save to:"))  # Add label
        dest_layout.addWidget(self.dest_label)  # Add save path label
        dest_layout.addWidget(self.dest_button)  # Add save button
        
        # Create convert button
        self.convert_button = QPushButton("Convert")  # Create conversion button
        self.convert_button.clicked.connect(self.convert_image)  # Connect to conversion function
        self.convert_button.setEnabled(False)  # Disable initially
        
        # Create status label
        self.status_label = QLabel("")  # Label for status messages
        
        # Add all layouts to main layout
        layout.addLayout(source_layout)  # Add source selection
        layout.addLayout(dest_layout)  # Add destination selection
        layout.addWidget(self.convert_button)  # Add convert button
        layout.addWidget(self.status_label)  # Add status label
        
        # Initialize path variables
        self.source_path = None
        self.dest_path = None
        self.selected_format = None
        
    def select_source(self):
        """
        Select source.
        """
        # Open file dialog for selecting WebP file
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select WebP Image",
            "",
            "WebP Files (*.webp)"
        )
        if file_path:
            self.source_path = file_path  # Store selected path
            self.source_label.setText(file_path)  # Display path
            self.update_convert_button()  # Update convert button state
            
    def select_destination(self):
        """
        Select destination.
        """
        # Create filter string for Save As dialog
        filters = "JPEG Image (*.jpg *.jpeg);;PNG Image (*.png);;All Files (*.*)"
        
        # Open file dialog for selecting save location with format options
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Save Converted Image",
            "" if not self.source_path else self.source_path.rsplit('.', 1)[0],
            filters
        )
        
        if file_path:
            # Determine selected format from the filter
            if "JPEG" in selected_filter:
                self.selected_format = "JPEG"
                # Add .jpg extension if no extension provided
                if not file_path.lower().endswith(('.jpg', '.jpeg')):
                    file_path += '.jpg'
            elif "PNG" in selected_filter:
                self.selected_format = "PNG"
                # Add .png extension if no extension provided
                if not file_path.lower().endswith('.png'):
                    file_path += '.png'
                    
            self.dest_path = file_path  # Store selected path
            self.dest_label.setText(file_path)  # Display path
            self.update_convert_button()  # Update convert button state
            
    def update_convert_button(self):
        """
        Updates convert button.
        """
        # Enable/disable convert button based on selection state
        self.convert_button.setEnabled(bool(self.source_path and self.dest_path))
            
    def convert_image(self):
        """
        Converts image.
        """
        try:
            # Open and convert the image
            with Image.open(self.source_path) as img:
                # Convert to RGB mode if necessary
                if img.mode in ('RGBA', 'LA'):
                    img = img.convert('RGB')
                
                # Save the converted image
                img.save(self.dest_path, format=self.selected_format)
                
                # Show success message
                self.status_label.setText(f"Successfully converted and saved to {self.dest_path}")
                self.status_label.setStyleSheet("color: green")
                
        except Exception as e:
            # Show error message if conversion fails
            self.status_label.setText(f"Error: {str(e)}")
            self.status_label.setStyleSheet("color: red")

# Main entry point
if __name__ == '__main__':
    app = QApplication(sys.argv)  # Create application instance
    window = ImageConverter()  # Create main window
    window.show()  # Show the window
    sys.exit(app.exec_())  # Start the application event loop
