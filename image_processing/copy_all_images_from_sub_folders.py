"""
This script handles copy all images from sub folders.
"""

import os
import shutil
from pathlib import Path

def main():
    """
    Main.
    """
    # Define the source directory (with Hebrew characters)
    source_dir = Path(r"C:\Users\EranGross\OneDrive - Gross\תמונות")
    target_dir = source_dir / "AllImages"

    # Create target directory if it doesn't exist
    target_dir.mkdir(exist_ok=True)

    # Supported image extensions
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')

    # Counter for duplicate filenames
    file_counters = {}

    # Walk through all directories
    for root, dirs, files in os.walk(source_dir):
        # Skip the target directory itself
        if root == str(target_dir):
            continue
            
        for file in files:
            if file.lower().endswith(image_extensions):
                # Get full path of source file
                source_file = Path(root) / file
                
                # Handle duplicate filenames
                if file in file_counters:
                    file_counters[file] += 1
                    name, ext = os.path.splitext(file)
                    new_filename = f"{name}_{file_counters[file]}{ext}"
                else:
                    file_counters[file] = 0
                    new_filename = file

                # Create target path
                target_file = target_dir / new_filename
                
                try:
                    shutil.copy2(source_file, target_file)
                    print(f"Copied: {file} -> {new_filename}")
                except Exception as e:
                    print(f"Error copying {file}: {e}")

if __name__ == "__main__":
    main()