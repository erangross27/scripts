#!/usr/bin/env python3
# shutterstock_uploader_gui.py
# GUI application for automated batch uploading of images to Shutterstock using Claude AI for image analysis

import os
import base64
import json
import requests
import time
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import datetime
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, 
                            QProgressBar, QLabel, QVBoxLayout, QWidget, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys

# Worker thread class to handle image processing and uploading
class UploaderWorker(QThread):
    # Signals for communicating with main thread
    progress_updated = pyqtSignal(int, str)
    finished = pyqtSignal(dict)
    log_message = pyqtSignal(str)

    def __init__(self, directory_path):
        super().__init__()
        self.directory_path = directory_path
        self.uploader = ShutterstockAutoUploader()

    # Main worker thread execution
    def run(self):
        # Get list of image files in directory
        image_files = [f for f in os.listdir(self.directory_path) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        total_files = len(image_files)
        successful = 0
        failed = 0

        # Process each image
        for index, filename in enumerate(image_files, 1):
            image_path = os.path.join(self.directory_path, filename)
            progress = int((index / total_files) * 100)
            self.progress_updated.emit(progress, f"Processing {filename}...")
            
            try:
                # Analyze image using Claude AI
                self.log_message.emit(f"Analyzing {filename}...")
                metadata = self.uploader.analyze_image_with_claude(image_path)
                
                if metadata:
                    # Submit image and metadata to Shutterstock
                    self.log_message.emit(f"Submitting {filename} to Shutterstock...")
                    result = self.uploader.submit_to_shutterstock(image_path, metadata)
                    
                    if result:
                        successful += 1
                        self.log_message.emit(f"Successfully processed {filename}")
                    else:
                        failed += 1
                        self.log_message.emit(f"Failed to submit {filename}")
                else:
                    failed += 1
                    self.log_message.emit(f"Failed to analyze {filename}")

                time.sleep(1)  # Rate limiting between uploads

            except Exception as e:
                failed += 1
                self.log_message.emit(f"Error processing {filename}: {str(e)}")

        self.finished.emit({"successful": successful, "failed": failed})

# Main GUI window class
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shutterstock Auto Uploader")
        self.setMinimumSize(600, 400)
        self.initUI()

    # Initialize all GUI elements
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create and configure GUI widgets
        self.folder_label = QLabel("No folder selected")
        self.browse_button = QPushButton("Browse Folder")
        self.browse_button.clicked.connect(self.browse_folder)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)

        self.status_label = QLabel("Ready")
        
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)

        self.submit_button = QPushButton("Start Upload")
        self.submit_button.clicked.connect(self.start_upload)
        self.submit_button.setEnabled(False)

        # Add widgets to layout
        layout.addWidget(self.folder_label)
        layout.addWidget(self.browse_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(self.log_display)
        layout.addWidget(self.submit_button)

        self.selected_directory = None

    # Handle folder selection via dialog
    def browse_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Images Directory")
        if directory:
            self.selected_directory = directory
            self.folder_label.setText(f"Selected: {directory}")
            self.submit_button.setEnabled(True)

    # Start the upload process in a separate thread
    def start_upload(self):
        if not self.selected_directory:
            return

        self.browse_button.setEnabled(False)
        self.submit_button.setEnabled(False)
        
        self.worker = UploaderWorker(self.selected_directory)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.upload_finished)
        self.worker.log_message.connect(self.log_message)
        self.worker.start()

    # Update progress bar and status message
    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.status_label.setText(message)

    # Add message to log display
    def log_message(self, message):
        self.log_display.append(message)

    # Handle upload completion
    def upload_finished(self, results):
        self.browse_button.setEnabled(True)
        self.submit_button.setEnabled(True)
        self.status_label.setText(
            f"Upload completed. Successful: {results['successful']}, Failed: {results['failed']}"
        )

# Main uploader class handling Shutterstock API interactions
class ShutterstockAutoUploader:
    def __init__(self):
        load_dotenv()
        self.anthropic = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.shutterstock_api_token = os.getenv('SHUTTERSTOCK_API_TOKEN')
        self.shutterstock_base_url = 'https://api.shutterstock.com/v2'
        self.setup_logging()

    # Configure logging system
    def setup_logging(self):
        logging.basicConfig(
            filename=f'shutterstock_uploader_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    # Convert image to base64 encoding
    def encode_image(self, image_path):
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Error encoding image {image_path}: {str(e)}")
            return None

    # Use Claude AI to analyze image and generate metadata
    def analyze_image_with_claude(self, image_path):
        try:
            base64_image = self.encode_image(image_path)
            if not base64_image:
                return None
            
            # Prompt for Claude AI to analyze image
            prompt = """Please analyze this image and provide the following information in JSON format:
            {
                "description": "Provide a detailed description of the image (50-200 words)",
                "keywords": "List exactly 15-25 relevant keywords, separated by commas",
                "categories": "Select exactly 2 categories from this list: Abstract, Animals/Wildlife, Arts, Backgrounds/Textures, Beauty/Fashion, Buildings/Landmarks, Business/Finance, Celebrities, Education, Food and drink, Healthcare/Medical, Holidays, Industrial, Interiors, Miscellaneous, Nature, Objects, Parks/Outdoor, People, Religion, Science, Signs/Symbols, Sports/Recreation, Technology, Transportation, Vintage",
                "image_type": "Specify if this is a photo, illustration, or vector",
                "location": "Specify location if identifiable (city, country)",
                "usage": "commercial"
            }
            
            Ensure that:
            1. Description is detailed and SEO-friendly
            2. Keywords are specific and market-relevant
            3. Exactly 2 categories are selected from the provided list
            4. Image type is correctly identified
            5. Location is as specific as possible
            
            Return in valid JSON format."""

            # Send request to Claude AI
            response = self.anthropic.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }]
            )

            metadata = json.loads(response.content)
            self.logger.info(f"Successfully analyzed image: {image_path}")
            return metadata

        except Exception as e:
            self.logger.error(f"Error analyzing image with Claude: {str(e)}")
            return None

    # Submit image and metadata to Shutterstock API
    def submit_to_shutterstock(self, image_path, metadata):
        headers = {
            'Authorization': f'Bearer {self.shutterstock_api_token}',
            'Content-Type': 'application/json'
        }

        try:
            # Upload image file
            with open(image_path, 'rb') as image_file:
                files = {'file': image_file}
                upload_response = requests.post(
                    f'{self.shutterstock_base_url}/images/uploads',
                    headers=headers,
                    files=files
                )
                upload_response.raise_for_status()
                upload_id = upload_response.json().get('upload_id')

            # Prepare metadata for submission
            submission_data = {
                "description": metadata['description'],
                "keywords": metadata['keywords'].split(','),
                "categories": metadata['categories'],
                "image_type": metadata['image_type'],
                "location": metadata.get('location', ''),
                "usage": metadata['usage']
            }

            # Submit metadata
            submission_url = f'{self.shutterstock_base_url}/images/uploads/{upload_id}'
            response = requests.post(
                submission_url,
                headers=headers,
                json=submission_data
            )
            response.raise_for_status()
            
            self.logger.info(f"Successfully submitted image {image_path} to Shutterstock")
            return response.json()

        except Exception as e:
            self.logger.error(f"Error submitting to Shutterstock: {str(e)}")
            return None

# Application entry point
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()