"""
This script handles update meta data pro.
"""

import os
import subprocess
import sys

# Optional: If using Anthropic's Claude API for AI assistance
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Import PyQt5 for GUI functionality
try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, 
                                QFileDialog, QCheckBox, QMessageBox, QGroupBox, QListWidget)
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QIcon, QPixmap
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False


def write_metadata_with_exiftool(image_path: str, title: str = "", description: str = "",
                                 keywords: list = None, categories: list = None) -> bool:
    """
    Writes metadata to image file using ExifTool, targeting IPTC and XMP fields for stock agencies.

    :param image_path: Path to the image file
    :param title: Title or headline for the image
    :param description: Description/caption for the image
    :param keywords: List of keyword strings
    :param categories: List of category strings
    :return: True if metadata writing succeeded, False otherwise
    """
    if keywords is None:
        keywords = []
    if categories is None:
        categories = []

    # Build the exiftool command arguments
    cmd = ["exiftool", "-overwrite_original", "-charset", "iptc=utf8"]

    # Title fields
    if title:
        cmd.extend([
            f"-IPTC:ObjectName={title}",
            f"-IPTC:Headline={title}",
            f"-XMP-dc:Title={title}"
        ])

    # Description field
    if description:
        cmd.extend([
            f"-IPTC:Caption-Abstract={description}",
            f"-XMP-dc:Description={description}"
        ])
    # Keywords fields
    if keywords:
        # Clear existing keywords first
        cmd.extend(["-IPTC:Keywords=", "-XMP-dc:Subject="])
        # Add each keyword
        for kw in keywords:
            if kw:  # skip empty strings
                cmd.extend([
                    f"-IPTC:Keywords+={kw}",
                    f"-XMP-dc:Subject+={kw}"
                ])

    # Categories fields
    if categories:
        # Clear existing categories
        cmd.extend(["-IPTC:Category=", "-IPTC:SupplementalCategories="])
        for i, cat in enumerate(categories):
            if not cat:
                continue
                cmd.append(f"-IPTC:SupplementalCategories+={cat}")

            # Set the first category as the main Category (limited to 3 chars)
            if i == 0:
                    cmd.append(f"-IPTC:Category={cat[:3]}")

    # Add the target file path
    cmd.append(image_path)

    # Run the ExifTool command
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               check=False, text=True, encoding='utf-8', errors='replace')
    except FileNotFoundError:
        print("Error: ExifTool is not installed or not found in PATH. Please install ExifTool and try again.")
        return False

    # Check result
    if result.returncode != 0:
        error_msg = result.stderr.strip()
        print(f"ExifTool error (return code {result.returncode}): {error_msg}")
        return False
    else:
        output_msg = result.stdout.strip()
        print(output_msg if output_msg else "Metadata written successfully.")
        return True

def refine_description_with_ai(description: str, keywords: list = None, categories: list = None) -> str:
    """
    Uses Anthropic's Claude to refine or generate a description for the image.
    """
    if not ANTHROPIC_AVAILABLE:
        print("Anthropic SDK not available. Skipping AI refinement.")
        return description
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("No ANTHROPIC_API_KEY found in environment variables. Skipping AI refinement.")
        return description
    
    try:
        client = Anthropic(api_key=api_key)
        
        if description.strip():
            # If a description exists, ask Claude to polish it
            message = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=300,
                temperature=0.7,
                system="You are a helpful assistant that improves stock photo descriptions.",
                messages=[
                    {
                        "role": "user",
                        "content": f"Please improve the following photo description for a stock image, making it concise, clear, and appealing to potential buyers. Preserve important details.\n\nCurrent description: \"{description.strip()}\""
                    }
                ]
            )
        else:
            # Use keywords/categories to generate a description
            kw_list = ", ".join(keywords) if keywords else ""
            cat_list = ", ".join(categories) if categories else ""
            message = client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=300,
                temperature=0.7,
                system="You are a helpful assistant that writes stock photo descriptions.",
                messages=[
                    {
                        "role": "user",
                        "content": f"Write a professional description for a stock photo with the following context.\n\nKeywords: {kw_list}\nCategories: {cat_list}\n\nThe description should be 1-3 sentences, engaging, and accurately describe the image."
                    }
                ]
            )
        
        # Access content correctly
        ai_text = message.content[0].text.strip()
        if ai_text:
            return ai_text
    except Exception as e:
        print(f"AI refinement failed: {e}")
    
    return description

def suggest_keywords_with_ai(description: str) -> list:
    """
    Uses Anthropic's Claude to suggest additional relevant keywords based on the description.
    """
    if not ANTHROPIC_AVAILABLE:
        return []

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return []

    try:
        client = Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=100,
            temperature=0.5,
            system="You are a helpful assistant that suggests relevant keywords for stock photos.",
            messages=[
                {
                    "role": "user",
                    "content": f"Given the following image description, suggest up to 10 relevant keywords for stock photo search.\n\nDescription: \"{description.strip()}\"\n\nProvide a comma-separated list of keywords without explanations."
                }
            ]
        )

        ai_keywords = message.content[0].text.strip()
        # Split the response by commas and strip whitespace
        suggested = [kw.strip() for kw in ai_keywords.split(',') if kw.strip()]
        return suggested
    except Exception as e:
        print(f"AI keyword suggestion failed: {e}")
        return []

class MetadataEditorGUI(QMainWindow):
    """
    Represents a metadata editor g u i.
    """
    def __init__(self):
        """
        Special method __init__.
        """
        super().__init__()
        self.setWindowTitle("Stock Photo Metadata Editor")
        self.setMinimumSize(800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Image selection area
        image_group = QGroupBox("Image Selection")
        image_layout = QHBoxLayout()
        
        self.image_path_edit = QLineEdit()
        self.image_path_edit.setPlaceholderText("Select an image file...")
        self.image_path_edit.setReadOnly(True)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_image)
        
        image_layout.addWidget(self.image_path_edit)
        image_layout.addWidget(browse_button)
        image_group.setLayout(image_layout)
        
        # Image preview area
        self.preview_label = QLabel("No image selected")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(200)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ddd;")
        
        # Metadata input area
        metadata_group = QGroupBox("Image Metadata")
        metadata_layout = QVBoxLayout()
        
        # Title
        title_layout = QHBoxLayout()
        title_label = QLabel("Title:")
        self.title_edit = QLineEdit()
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_edit)
        
        # Description
        desc_layout = QVBoxLayout()
        desc_label = QLabel("Description:")
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(100)
        desc_layout.addWidget(desc_label)
        desc_layout.addWidget(self.desc_edit)
        
        # Keywords
        keywords_layout = QVBoxLayout()
        keywords_label = QLabel("Keywords (comma-separated):")
        self.keywords_edit = QTextEdit()
        self.keywords_edit.setMaximumHeight(80)
        keywords_layout.addWidget(keywords_label)
        keywords_layout.addWidget(self.keywords_edit)
        
        # Categories
        categories_layout = QVBoxLayout()
        categories_label = QLabel("Categories (comma-separated):")
        self.categories_edit = QLineEdit()
        categories_layout.addWidget(categories_label)
        categories_layout.addWidget(self.categories_edit)
        
        # Add all metadata inputs to layout
        metadata_layout.addLayout(title_layout)
        metadata_layout.addLayout(desc_layout)
        metadata_layout.addLayout(keywords_layout)
        metadata_layout.addLayout(categories_layout)
        metadata_group.setLayout(metadata_layout)
        
        # AI options
        ai_group = QGroupBox("AI Assistance")
        ai_layout = QVBoxLayout()
        
        self.ai_checkbox = QCheckBox("Use Claude AI to improve metadata")
        self.ai_checkbox.setEnabled(ANTHROPIC_AVAILABLE and bool(os.environ.get("ANTHROPIC_API_KEY")))
        
        ai_buttons_layout = QHBoxLayout()
        self.refine_desc_button = QPushButton("Refine Description")
        self.refine_desc_button.clicked.connect(self.refine_description)
        self.refine_desc_button.setEnabled(False)
        
        self.suggest_keywords_button = QPushButton("Suggest Keywords")
        self.suggest_keywords_button.clicked.connect(self.suggest_keywords)
        self.suggest_keywords_button.setEnabled(False)
        
        ai_buttons_layout.addWidget(self.refine_desc_button)
        ai_buttons_layout.addWidget(self.suggest_keywords_button)
        
        ai_layout.addWidget(self.ai_checkbox)
        ai_layout.addLayout(ai_buttons_layout)
        ai_group.setLayout(ai_layout)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Save Metadata")
        self.save_button.clicked.connect(self.save_metadata)
        self.save_button.setEnabled(False)
        
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.close)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(exit_button)
        
        # Add all components to main layout
        main_layout.addWidget(image_group)
        main_layout.addWidget(self.preview_label)
        main_layout.addWidget(metadata_group)
        main_layout.addWidget(ai_group)
        main_layout.addLayout(buttons_layout)
        
        # Set the main layout
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Connect signals
        self.ai_checkbox.toggled.connect(self.toggle_ai_buttons)
        self.image_path_edit.textChanged.connect(self.check_input_validity)
        self.title_edit.textChanged.connect(self.check_input_validity)
        
    def browse_image(self):
        """
        Browse image.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.jpg *.jpeg *.png *.tif *.tiff)"
        )
        if file_path:
            self.image_path_edit.setText(file_path)
            self.load_image_preview(file_path)
            self.load_existing_metadata(file_path)
    
    def load_image_preview(self, image_path):
        """
        Load image preview based on image path.
        """
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(400, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(pixmap)
        else:
            self.preview_label.setText("Unable to load image preview")
    
    def load_existing_metadata(self, image_path):
        """
        Load existing metadata based on image path.
        """
        # Use exiftool to get existing metadata
        try:
            cmd = ["exiftool", "-j", image_path]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  check=False, text=True, encoding='utf-8', errors='replace')
            
            if result.returncode == 0 and result.stdout:
                import json
                metadata = json.loads(result.stdout)[0]
                
                # Set title from metadata if available
                if "Title" in metadata:
                    self.title_edit.setText(metadata["Title"])
                elif "Headline" in metadata:
                    self.title_edit.setText(metadata["Headline"])
                elif "ObjectName" in metadata:
                    self.title_edit.setText(metadata["ObjectName"])
                
                # Set description
                if "Description" in metadata:
                    self.desc_edit.setText(metadata["Description"])
                elif "Caption-Abstract" in metadata:
                    self.desc_edit.setText(metadata["Caption-Abstract"])
                
                # Set keywords
                keywords = []
                if "Keywords" in metadata:
                    if isinstance(metadata["Keywords"], list):
                        keywords = metadata["Keywords"]
                    else:
                        keywords = [metadata["Keywords"]]
                elif "Subject" in metadata:
                    if isinstance(metadata["Subject"], list):
                        keywords = metadata["Subject"]
                    else:
                        keywords = [metadata["Subject"]]
                
                self.keywords_edit.setText(", ".join(keywords))
                
                # Set categories
                categories = []
                if "Category" in metadata and metadata["Category"]:
                    categories.append(metadata["Category"])
                if "SupplementalCategories" in metadata:
                    if isinstance(metadata["SupplementalCategories"], list):
                        categories.extend(metadata["SupplementalCategories"])
                    else:
                        categories.append(metadata["SupplementalCategories"])
                
                self.categories_edit.setText(", ".join(categories))
                
        except Exception as e:
            print(f"Error loading existing metadata: {e}")
    
    def toggle_ai_buttons(self, checked):
        """
        Toggle ai buttons based on checked.
        """
        self.refine_desc_button.setEnabled(checked)
        self.suggest_keywords_button.setEnabled(checked)
    
    def refine_description(self):
        """
        Refine description.
        """
        current_desc = self.desc_edit.toPlainText().strip()
        keywords = [k.strip() for k in self.keywords_edit.toPlainText().split(',') if k.strip()]
        categories = [c.strip() for c in self.categories_edit.text().split(',') if c.strip()]
        
        if not current_desc and not keywords and not categories:
            QMessageBox.warning(self, "Input Needed", 
                              "Please provide a description or keywords to generate content.")
            return
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            refined_desc = refine_description_with_ai(current_desc, keywords, categories)
            QApplication.restoreOverrideCursor()
            
            if refined_desc and refined_desc != current_desc:
                reply = QMessageBox.question(self, "AI Suggestion", 
                                           f"Use this refined description?\n\n{refined_desc}",
                                           QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    self.desc_edit.setText(refined_desc)
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "AI Error", f"Error refining description: {str(e)}")
    
    def suggest_keywords(self):
        """
        Suggest keywords.
        """
        description = self.desc_edit.toPlainText().strip()
        if not description:
            QMessageBox.warning(self, "Input Needed", 
                              "Please provide a description to generate keywords.")
            return
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            suggested_keywords = suggest_keywords_with_ai(description)
            QApplication.restoreOverrideCursor()
            
            if suggested_keywords:
                current_keywords = [k.strip() for k in self.keywords_edit.toPlainText().split(',') if k.strip()]
                new_keywords = []
                
                for kw in suggested_keywords:
                    if kw.lower() not in [k.lower() for k in current_keywords]:
                        new_keywords.append(kw)
                
                if new_keywords:
                    keywords_text = ", ".join(new_keywords)
                    reply = QMessageBox.question(self, "AI Keyword Suggestions", 
                                               f"Add these keywords?\n\n{keywords_text}",
                                               QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        all_keywords = current_keywords + new_keywords
                        if len(all_keywords) > 50:
                            QMessageBox.information(self, "Keyword Limit", 
                                                 "Trimmed to 50 keywords (Shutterstock's limit)")
                            all_keywords = all_keywords[:50]
                        
                        self.keywords_edit.setText(", ".join(all_keywords))
                else:
                    QMessageBox.information(self, "No New Keywords", 
                                          "All suggested keywords are already in your list.")
            else:
                QMessageBox.information(self, "No Suggestions", 
                                      "AI couldn't generate keyword suggestions.")
        except Exception as e:
            QApplication.restoreOverrideCursor()
            QMessageBox.critical(self, "AI Error", f"Error suggesting keywords: {str(e)}")
    
    def check_input_validity(self):
        """
        Check input validity.
        """
        has_image = bool(self.image_path_edit.text().strip())
        self.save_button.setEnabled(has_image)
    
    def save_metadata(self):
        """
        Save metadata.
        """
        image_path = self.image_path_edit.text().strip()
        title = self.title_edit.text().strip()
        description = self.desc_edit.toPlainText().strip()
        keywords = [k.strip() for k in self.keywords_edit.toPlainText().split(',') if k.strip()]
        categories = [c.strip() for c in self.categories_edit.text().split(',') if c.strip()]
        
        if not image_path:
            QMessageBox.warning(self, "Missing Image", "Please select an image file.")
            return
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        success = write_metadata_with_exiftool(image_path, title, description, keywords, categories)
        QApplication.restoreOverrideCursor()
        
        if success:
            QMessageBox.information(self, "Success", "Metadata successfully saved to image.")
        else:
            QMessageBox.critical(self, "Error", "Failed to save metadata. Check console for details.")

def main():
    """
    Main.
    """
    if QT_AVAILABLE:
        app = QApplication(sys.argv)
        window = MetadataEditorGUI()
        window.show()
        sys.exit(app.exec_())
    else:
        print("PyQt5 is not installed. Running command-line version instead.")
        run_cli_version()

def run_cli_version():
    """
    Run cli version.
    """
    print("=== Shutterstock Metadata Embedding Script ===")

    # Get user inputs
    image_path = input("Enter the path to the image file (e.g., photo.jpg): ").strip()
    if not os.path.isfile(image_path):
        print(f"Error: File '{image_path}' not found.")
        sys.exit(1)

    # ... existing CLI code ...
    title = input("Title (short title or headline for the image): ").strip()
    description = input("Description (a sentence or two describing the image): ").strip()
    keywords_input = input("Keywords (comma-separated list of keywords): ").strip()
    categories_input = input("Categories (comma-separated, for your reference): ").strip()

    # Split keywords and categories by comma
    keywords = [kw.strip() for kw in keywords_input.split(',') if kw.strip()]
    categories = [cat.strip() for cat in categories_input.split(',') if cat.strip()]

    # Ask if user wants AI assistance
    use_ai = False
    if ANTHROPIC_AVAILABLE:
        ai_choice = input("Use AI to refine/generate description and suggest extra keywords? [y/N]: ").strip().lower()
        if ai_choice in ('y', 'yes'):
            if not os.environ.get("ANTHROPIC_API_KEY"):
                print("Warning: Anthropic API key not found. Set ANTHROPIC_API_KEY env variable to enable AI features.")
            else:
                use_ai = True

    # If using AI, refine description and/or keywords
    if use_ai:
        # ... existing AI processing code ...
        # Refine or generate description
        new_description = refine_description_with_ai(description, keywords, categories)
        if new_description and new_description != description:
            print("\nAI-refined description:")
            print(new_description)
            use_refined = input("Use this refined description? [Y/n]: ").strip().lower()
            if use_refined not in ('n', 'no'):
                description = new_description

        # Suggest additional keywords if description is available
        if description:
            extra_keywords = suggest_keywords_with_ai(description)
            if extra_keywords:
                print("\nAI suggested keywords:", ", ".join(extra_keywords))
                use_suggested = input("Add these keywords? [Y/n]: ").strip().lower()
                if use_suggested not in ('n', 'no'):
                    # Add AI suggestions (avoiding duplicates)
                    original_count = len(keywords)
                    for kw in extra_keywords:
                        if kw.lower() not in [k.lower() for k in keywords]:
                            keywords.append(kw)

                    # Trim to max 50 keywords for Shutterstock
                    if len(keywords) > 50:
                        print(f"Warning: Trimming to 50 keywords (Shutterstock's limit)")
                        keywords = keywords[:50]

                    print(f"Added {len(keywords) - original_count} new keywords. Total: {len(keywords)}")

    # Write metadata to the image using ExifTool
    print("\nWriting metadata to image...")
    success = write_metadata_with_exiftool(image_path, title, description, keywords, categories)

    if success:
        print("\nMetadata embedding completed successfully.")
        print("You can verify by uploading the image to Shutterstock to see if the fields auto-populate.")
    else:
        print("\nMetadata embedding failed. Please check the errors above.")

if __name__ == "__main__":
    main()