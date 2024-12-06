import os
import sys
import re
from anthropic import Anthropic
from PIL import Image
import piexif
import piexif.helper
import base64
from io import BytesIO
import time
import logging
import json
from datetime import datetime
from typing import Dict, List, Any
from PyQt5.QtWidgets import (QApplication, QMainWindow, QProgressBar, 
                           QTextEdit, QVBoxLayout, QPushButton, QWidget,
                           QFileDialog, QLabel, QHBoxLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
import subprocess
import shlex
# Add at the top of your file with other imports
HAS_WIN32 = False
try:
    from win32file import SetFileAttributes
    HAS_WIN32 = True
except ImportError:
    pass

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('metadata_updater.log'),
        logging.StreamHandler()
    ]
)

class MetadataWorker(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, folder_path, parent=None):
        super().__init__(parent)
        self.folder_path = folder_path
        self.is_running = True

    def run(self):
        try:
            updater = LocalMetadataUpdater(self.folder_path, self.progress, self.log, self)
            updater.process_folder()
        except Exception as e:
            self.log.emit(f"Error: {str(e)}")
        finally:
            self.finished.emit()
        
    def stop(self):
        self.is_running = False
        self.log.emit("Stopping process...")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.folder_path = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Metadata Updater')
        self.setGeometry(100, 100, 900, 700)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Folder selection area
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel('No folder selected')
        self.folder_button = QPushButton('Select Folder')
        self.folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_button)
        layout.addLayout(folder_layout)

        # Add progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # Add log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)

        # Add buttons
        button_layout = QHBoxLayout()
        self.start_button = QPushButton('Start Processing')
        self.start_button.clicked.connect(self.start_processing)
        self.start_button.setEnabled(False)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_processing)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)

        layout.addLayout(button_layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
        if folder:
            self.folder_path = folder
            self.folder_label.setText(f'Selected: {folder}')
            self.start_button.setEnabled(True)
            self.log_display.append(f"Selected folder: {folder}")

    def start_processing(self):
        if not self.folder_path:
            self.log_display.append("Please select a folder first")
            return

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.folder_button.setEnabled(False)
        self.worker = MetadataWorker(self.folder_path)
        self.worker.progress.connect(self.update_progress)
        self.worker.log.connect(self.update_log)
        self.worker.finished.connect(self.processing_finished)
        self.worker.start()

    def stop_processing(self):
        if hasattr(self, 'worker'):
            self.worker.stop()
            self.worker.wait()
            self.processing_finished()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_log(self, message):
        self.log_display.append(message)
        # Auto-scroll to bottom
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_display.setTextCursor(cursor)

    def processing_finished(self):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.folder_button.setEnabled(True)
        self.update_log("Processing completed!")

class LocalMetadataUpdater:
    def __init__(self, folder_path, progress_signal, log_signal, worker):
        self.folder_path = folder_path
        self.progress_signal = progress_signal
        self.log_signal = log_signal
        self.worker = worker
        self._setup_apis()
        self.cache_folder = os.path.join(folder_path, '.cache')
        os.makedirs(self.cache_folder, exist_ok=True)

    def _setup_apis(self):
        """Set up API clients."""
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.anthropic_key:
            raise ValueError("Missing Anthropic API key")
        self.anthropic = Anthropic(api_key=self.anthropic_key)

    def process_folder(self):
        """Process all images in the folder."""
        image_files = [f for f in os.listdir(self.folder_path) 
                      if f.lower().endswith(('.jpg', '.jpeg'))]
        
        total_files = len(image_files)
        self.log_signal.emit(f"Found {total_files} images to process")
        
        for i, image_file in enumerate(image_files):
            if not self.worker.is_running:
                self.log_signal.emit("Process stopped by user")
                break
                
            try:
                self.process_single_image(image_file)
                progress = int((i + 1) / total_files * 100)
                self.progress_signal.emit(progress)
            except Exception as e:
                self.log_signal.emit(f"Error processing {image_file}: {str(e)}")
                continue

    def process_single_image(self, image_file):
        """Process a single image."""
        if not self.worker.is_running:
            return
        try:
            image_path = os.path.join(self.folder_path, image_file)
            cache_file = os.path.join(self.cache_folder, f"{image_file}.json")

            # Check cache
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    self.log_signal.emit(f"Using cached analysis for {image_file}")
                except json.JSONDecodeError:
                    self.log_signal.emit(f"Invalid cache file for {image_file}, reanalyzing...")
                    metadata = None
            else:
                metadata = None

            if not metadata:
                # Get AI analysis
                metadata = self._analyze_image(image_path)
                # Cache the results
                if metadata:
                    try:
                        with open(cache_file, 'w', encoding='utf-8') as f:
                            json.dump(metadata, f, ensure_ascii=False, indent=2)
                    except Exception as e:
                        self.log_signal.emit(f"Failed to cache results for {image_file}: {str(e)}")

            if metadata:
                # Update local image metadata
                self._update_local_metadata(image_path, metadata)
            
            self.log_signal.emit(f"Processed {image_file}")
        except Exception as e:
            self.log_signal.emit(f"Error processing {image_file}: {str(e)}")



    def _resize_image_for_api(self, image_path):
        """Resize image to meet API requirements while maintaining aspect ratio."""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if needed
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Initial resize if image is very large
                width, height = img.size
                max_dimension = 2000  # Reduced from 5000 to ensure smaller file size
                if width > max_dimension or height > max_dimension:
                    ratio = min(max_dimension/width, max_dimension/height)
                    new_size = (int(width * ratio), int(height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                # Start with high quality and gradually reduce until under 5MB
                quality = 95
                while True:
                    buffered = BytesIO()
                    img.save(buffered, format="JPEG", quality=quality, optimize=True)
                    file_size = buffered.tell()
                    
                    if file_size <= 5 * 1024 * 1024:  # 5MB in bytes
                        self.log_signal.emit(f"Successfully resized image to {file_size/1024/1024:.2f}MB with quality {quality}")
                        buffered.seek(0)
                        return base64.b64encode(buffered.getvalue()).decode()
                    
                    quality -= 5
                    if quality < 30:  # If quality gets too low, reduce size further
                        width, height = img.size
                        ratio = 0.8  # Reduce dimensions by 20%
                        new_size = (int(width * ratio), int(height * ratio))
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                        quality = 95  # Reset quality and try again
                    
                    if width < 800 or height < 800:  # Prevent images from becoming too small
                        self.log_signal.emit("Warning: Could not reduce image size enough while maintaining quality")
                        return None

        except Exception as e:
            self.log_signal.emit(f"Error resizing image: {str(e)}")
            return None

    def _analyze_image(self, image_path):
        """Analyze image using Anthropic API without modifying the original image."""
        if not self.worker.is_running:
            return None
            
        try:
            # Use the existing resize function to get base64 string under 5MB
            img_str = self._resize_image_for_api(image_path)
            
            if not img_str:
                self.log_signal.emit(f"Failed to process image - could not resize properly")
                return None

            message = self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0,
                system="""You are a professional image analyst providing metadata for stock photos from the Golan Heights region. 
                        CRITICAL: Headlines must be EXACTLY 6 words.
                        Consider both secular and Christian religious significance when relevant.""",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": img_str
                                }
                            },
                            {
                                "type": "text",
                                "text": """Analyze this image and provide exactly in this format:
    1. Headline: [EXACTLY 6 words. Example: "Beautiful Sunset Illuminates Ancient Golan Heights Path"]
    2. Keywords: [provide 10-15 relevant comma-separated keywords, include relevant biblical/Christian terms if applicable]
    3. Category 1: [select one category from this list:
    - Backgrounds/Textures
    - Beauty/Fashion
    - Buildings/Landmarks
    - Business/Finance  
    - Celebrities
    - Education
    - Food and drink
    - Healthcare/Medical
    - Holidays
    - Industrial
    - Interiors
    - Miscellaneous
    - Nature
    - Objects
    - Parks/Outdoor
    - People
    - Religion
    - Science
    - Signs/Symbols
    - Sports/Recreation
    - Technology
    - Transportation]
    4. Category 2: [select one different category from the same list above]
    5. Biblical Reference: [if applicable, provide relevant biblical location or story connection]"""
                            }
                        ]
                    }
                ]
            )

            self.log_signal.emit(f"Successfully received AI analysis")
            return self._parse_analysis_response(message.content[0].text)

        except Exception as e:
            self.log_signal.emit(f"Error analyzing image: {str(e)}")
            import traceback
            self.log_signal.emit(f"Detailed error: {traceback.format_exc()}")
            return None

    
    def _parse_analysis_response(self, response_text):
        """Parse the AI response into structured metadata."""
        try:
            # Extract headline and ensure it's exactly 6 words
            headline_match = re.search(r'Headline:\s*(.+?)(?:\n|$)', response_text)
            headline = headline_match.group(1).strip() if headline_match else ''
            words = headline.split()
            headline = ' '.join(words[:6])  # Always take exactly 6 words

            # Extract keywords and ensure they're comma-separated
            keywords_match = re.search(r'Keywords:\s*(.+?)(?:\n|$)', response_text)
            if keywords_match:
                keywords_text = keywords_match.group(1)
                if ';' in keywords_text:
                    keywords = [k.strip() for k in keywords_text.split(';')]
                else:
                    keywords = [k.strip() for k in keywords_text.split(',')]
                keywords = [k.strip('., ') for k in keywords if k.strip()]
            else:
                keywords = []

            # Extract categories
            cat1_match = re.search(r'Category 1:\s*(.+?)(?:\n|$)', response_text)
            cat2_match = re.search(r'Category 2:\s*(.+?)(?:\n|$)', response_text)
            categories = []
            if cat1_match: categories.append(cat1_match.group(1).strip())
            if cat2_match: categories.append(cat2_match.group(1).strip())

            # Extract biblical reference
            bible_match = re.search(r'Biblical Reference:\s*(.+?)(?:\n|$)', response_text)
            biblical_ref = bible_match.group(1).strip() if bible_match else ''

            metadata = {
                'headline': headline,
                'keywords': keywords[:15],
                'categories': categories[:2],
                'location': 'Golan Heights',
                'type': 'Photo',
                'biblical_reference': biblical_ref,
                'creator': 'Eran Gross',
                'copyright': '© Eran Gross'
            }

            self.log_signal.emit(f"Parsed metadata:")
            self.log_signal.emit(f"Headline: {metadata['headline']}")
            self.log_signal.emit(f"Keywords: {', '.join(metadata['keywords'])}")
            self.log_signal.emit(f"Categories: {', '.join(metadata['categories'])}")
            self.log_signal.emit(f"Biblical Reference: {metadata['biblical_reference']}")
            self.log_signal.emit(f"Creator: {metadata['creator']}")
            self.log_signal.emit(f"Copyright: {metadata['copyright']}")

            return metadata
        except Exception as e:
            self.log_signal.emit(f"Error parsing AI response: {str(e)}")
            return None

    def _update_local_metadata(self, image_path, metadata):
        """Update local image EXIF metadata."""
        if not self.worker.is_running:
            return
            
        try:
            # Read existing EXIF data
            try:
                exif_dict = piexif.load(image_path)
            except:
                exif_dict = {'0th': {}, 'Exif': {}, 'GPS': {}, '1st': {}, 'thumbnail': None}

            # Ensure all required dictionaries exist
            for ifd in ('0th', 'Exif', 'GPS', '1st'):
                if ifd not in exif_dict:
                    exif_dict[ifd] = {}

            # Remove problematic tags if they exist
            if 'Exif' in exif_dict and 41729 in exif_dict['Exif']:
                del exif_dict['Exif'][41729]

            # Convert metadata to Windows-compatible format (UTF-16LE)
            title = metadata['headline']
            keywords = ', '.join(metadata['keywords'])
            categories = ', '.join(metadata['categories'])
            location = f"{metadata['location']} - {metadata.get('biblical_reference', '')}"
            creator = metadata['creator']
            copyright_notice = metadata['copyright']

            # Update Windows XP tags (UTF-16LE encoding)
            exif_dict['0th'][piexif.ImageIFD.XPTitle] = title.encode('utf-16le')
            exif_dict['0th'][piexif.ImageIFD.XPKeywords] = keywords.encode('utf-16le')
            exif_dict['0th'][piexif.ImageIFD.XPSubject] = categories.encode('utf-16le')
            exif_dict['0th'][piexif.ImageIFD.XPComment] = location.encode('utf-16le')
            exif_dict['0th'][piexif.ImageIFD.XPAuthor] = creator.encode('utf-16le')

            # Update standard IPTC tags (UTF-8 encoding)
            exif_dict['0th'][piexif.ImageIFD.ImageDescription] = title.encode('utf-8')
            exif_dict['0th'][piexif.ImageIFD.Artist] = creator.encode('utf-8')
            exif_dict['0th'][piexif.ImageIFD.Copyright] = copyright_notice.encode('utf-8')

            # Convert EXIF dict to bytes
            exif_bytes = piexif.dump(exif_dict)

            # Save metadata using PIL
            with Image.open(image_path) as img:
                # Create new image with metadata
                new_image = Image.new(img.mode, img.size)
                new_image.putdata(list(img.getdata()))
                new_image.save(image_path, 'JPEG', 
                            quality=100,  # Preserve quality
                            exif=exif_bytes,
                            optimize=False)  # Don't compress

            # Log success
            self.log_signal.emit(f"Updated metadata for {os.path.basename(image_path)}")
            self.log_signal.emit(f"Written metadata:")
            self.log_signal.emit(f"Title: {title}")
            self.log_signal.emit(f"Keywords: {keywords}")
            self.log_signal.emit(f"Categories: {categories}")
            self.log_signal.emit(f"Location: {location}")
            self.log_signal.emit(f"Creator: {creator}")
            self.log_signal.emit(f"Copyright: {copyright_notice}")

            # Force Windows to refresh the file
            try:
                # Update file timestamp to force refresh
                os.utime(image_path, None)
                
                # Force a final read to verify metadata
                with Image.open(image_path) as img:
                    img.load()
                    
            except Exception as e:
                self.log_signal.emit(f"Warning: File refresh error: {str(e)}")
                
        except Exception as e:
            self.log_signal.emit(f"Error updating metadata: {str(e)}")
            import traceback
            self.log_signal.emit(f"Detailed error: {traceback.format_exc()}")

    
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()