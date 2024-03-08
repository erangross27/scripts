import os
from PIL import Image

def compress_image(image_path, output_path, quality):
    # Open the image file.
    with Image.open(image_path) as img:
        # Save the image again with reduced quality.
        img.save(output_path, "JPEG", quality=quality)

def compress_images_in_folder(folder_path, output_folder_path, quality=90):
    # Ensure the output directory exists.
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    # Iterate over all files in the input directory.
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg") or filename.endswith(".jpeg"):
            # Construct full file path.
            file_path = os.path.join(folder_path, filename)
            # Construct output file path.
            output_path = os.path.join(output_folder_path, filename.split('.')[0] + '_compressed.jpg')
            # Compress image.
            compress_image(file_path, output_path, quality)

# Usage
compress_images_in_folder('C:\\Users\\User\\Downloads\\window_images', 'C:\\Users\\User\\Downloads\\windows_images_compressed', 90)