"""
Image Mover Application

This script creates a PyQt5-based GUI application for moving image files from a source directory
to a destination directory. The application allows users to select source and destination 
directories through a graphical interface and then move all image files (with extensions
.jpg, .jpeg, .png, .gif, .bmp) from the source to the destination.

Features:
- Select source and destination directories via GUI
- Move image files between directories
- Handle filename conflicts in the destination directory
- Simple and intuitive user interface

Usage:
Run this script to launch the Image Mover application. Use the buttons to select directories
and initiate the image moving process.

Dependencies:
- PyQt5
- os
- shutil

"""

import os
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QLabel

class ImageMover(QWidget):
    """
    Represents a image mover.
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
        self.setWindowTitle('Image Mover')
        self.setGeometry(300, 300, 300, 150)
        
        # Create a vertical layout
        layout = QVBoxLayout()
        
        # Create labels to display selected directories
        self.sourceLabel = QLabel('Source Directory: Not Selected')
        self.destLabel = QLabel('Destination Directory: Not Selected')
        
        # Create buttons for selecting directories and moving images
        sourceButton = QPushButton('Select Source Directory', self)
        sourceButton.clicked.connect(self.selectSourceDir)
        
        destButton = QPushButton('Select Destination Directory', self)
        destButton.clicked.connect(self.selectDestDir)
        
        moveButton = QPushButton('Move Images', self)
        moveButton.clicked.connect(self.moveImages)
        
        # Add widgets to the layout
        layout.addWidget(self.sourceLabel)
        layout.addWidget(sourceButton)
        layout.addWidget(self.destLabel)
        layout.addWidget(destButton)
        layout.addWidget(moveButton)
        
        # Set the layout for the main window
        self.setLayout(layout)
        
    def selectSourceDir(self):
        """
        Selectsourcedir.
        """
        # Open a dialog to select the source directory
        self.sourceDir = QFileDialog.getExistingDirectory(self, "Select Source Directory")
        self.sourceLabel.setText(f'Source Directory: {self.sourceDir}')
        
    def selectDestDir(self):
        """
        Selectdestdir.
        """
        # Open a dialog to select the destination directory
        self.destDir = QFileDialog.getExistingDirectory(self, "Select Destination Directory")
        self.destLabel.setText(f'Destination Directory: {self.destDir}')
        
    def moveImages(self):
        """
        Moveimages.
        """
        # Check if both source and destination directories are selected
        if not hasattr(self, 'sourceDir') or not hasattr(self, 'destDir'):
            print("Please select both source and destination directories.")
            return
        
        # Define supported image file extensions
        image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
        
        # Walk through the source directory
        for root, dirs, files in os.walk(self.sourceDir):
            for file in files:
                # Check if the file is an image
                if file.lower().endswith(image_extensions):
                    source_path = os.path.join(root, file)
                    dest_path = os.path.join(self.destDir, file)
                    
                    # Handle filename conflicts in the destination directory
                    counter = 1
                    while os.path.exists(dest_path):
                        name, ext = os.path.splitext(file)
                        dest_path = os.path.join(self.destDir, f"{name}_{counter}{ext}")
                        counter += 1
                    
                    # Move the image file
                    shutil.move(source_path, dest_path)
        
        print("All images have been moved successfully!")

if __name__ == '__main__':
    # Create and run the application
    app = QApplication([])
    ex = ImageMover()
    ex.show()
    app.exec_()
