import cv2
import numpy as np
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                            QPushButton, QVBoxLayout, QHBoxLayout, QSlider,
                            QFileDialog, QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage

class ImageBrightener(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Brightener")
        self.setMinimumSize(600, 400)
        
        # Initialize variables
        self.input_path = ""
        self.output_path = ""
        self.brightness_factor = 1.5
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create input file selection
        input_layout = QHBoxLayout()
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("Input image path...")
        input_browse = QPushButton("Browse Input")
        input_browse.clicked.connect(self.browse_input)
        input_layout.addWidget(self.input_edit)
        input_layout.addWidget(input_browse)
        layout.addLayout(input_layout)
        
        # Create output file selection
        output_layout = QHBoxLayout()
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Output image path...")
        output_browse = QPushButton("Browse Output")
        output_browse.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_browse)
        layout.addLayout(output_layout)
        
        # Create brightness slider
        slider_layout = QHBoxLayout()
        slider_label = QLabel("Brightness:")
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(300)
        self.slider.setValue(150)
        self.slider.valueChanged.connect(self.update_brightness)
        self.brightness_label = QLabel("1.5x")
        slider_layout.addWidget(slider_label)
        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.brightness_label)
        layout.addLayout(slider_layout)
        
        # Create image preview
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)
        
        # Create process button
        process_btn = QPushButton("Process Image")
        process_btn.clicked.connect(self.process_image)
        layout.addWidget(process_btn)
        
    def browse_input(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Input Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*.*)"
        )
        if file_name:
            self.input_path = file_name
            self.input_edit.setText(file_name)
            self.update_preview()
            
            # Auto-generate output path if not set
            if not self.output_edit.text():
                import os
                path, ext = os.path.splitext(file_name)
                self.output_path = f"{path}_brightened{ext}"
                self.output_edit.setText(self.output_path)
    
    def browse_output(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Select Output Location",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*.*)"
        )
        if file_name:
            self.output_path = file_name
            self.output_edit.setText(file_name)
    
    def update_brightness(self):
        self.brightness_factor = self.slider.value() / 100
        self.brightness_label.setText(f"{self.brightness_factor:.1f}x")
        self.update_preview()
    
    def update_preview(self):
        if not self.input_path:
            return
            
        # Read and process image
        img = cv2.imread(self.input_path)
        if img is None:
            return
            
        # Create preview of brightened image
        preview = self.brighten_image(img.copy())
        
        # Convert to Qt format for display
        height, width = preview.shape[:2]
        scale = min(400/width, 300/height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        preview = cv2.resize(preview, (new_width, new_height))
        
        bytes_per_line = 3 * new_width
        qt_image = QImage(
            preview.data,
            new_width,
            new_height,
            bytes_per_line,
            QImage.Format_RGB888
        ).rgbSwapped()
        
        self.image_label.setPixmap(QPixmap.fromImage(qt_image))
    
    def brighten_image(self, img):
        # Convert to HSV color space
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Scale the V (brightness) channel
        hsv[:,:,2] = cv2.multiply(hsv[:,:,2], self.brightness_factor)
        
        # Make sure values stay within valid range
        hsv[:,:,2] = np.clip(hsv[:,:,2], 0, 255)
        
        # Convert back to BGR
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    def process_image(self):
        if not self.input_path or not self.output_path:
            return
            
        # Read input image
        img = cv2.imread(self.input_path)
        if img is None:
            return
            
        # Process and save image
        brightened = self.brighten_image(img)
        cv2.imwrite(self.output_path, brightened)

def main():
    app = QApplication(sys.argv)
    window = ImageBrightener()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()