import os
import shutil
import random

def organize_dataset(source_dir, destination_dir, split_ratio=0.8):
    # Create necessary directories
    for dir in ['images/train', 'images/val', 'labels/train', 'labels/val']:
        os.makedirs(os.path.join(destination_dir, dir), exist_ok=True)

    # Get list of image files
    image_files = [f for f in os.listdir(os.path.join(source_dir, 'images')) if f.endswith(('.jpg', '.jpeg', '.png'))]

    # Shuffle the list
    random.shuffle(image_files)

    # Split into train and validation
    split_index = int(len(image_files) * split_ratio)
    train_files = image_files[:split_index]
    val_files = image_files[split_index:]

    # Move files
    for file_list, img_dir, label_dir in [(train_files, 'images/train', 'labels/train'), 
                                          (val_files, 'images/val', 'labels/val')]:
        for img_file in file_list:
            # Move image
            shutil.copy(os.path.join(source_dir, 'images', img_file), 
                        os.path.join(destination_dir, img_dir, img_file))
            
            # Move corresponding label file
            label_file = os.path.splitext(img_file)[0] + '.txt'
            if os.path.exists(os.path.join(source_dir, 'labels', label_file)):
                shutil.copy(os.path.join(source_dir, 'labels', label_file), 
                            os.path.join(destination_dir, label_dir, label_file))

    # Copy classes.txt
    shutil.copy(os.path.join(source_dir, 'classes.txt'), destination_dir)

    print(f"Dataset organized. {len(train_files)} training samples, {len(val_files)} validation samples.")

# Usage
source_directory = r"C:\Users\User\Downloads\project-1-at-2024-07-29-15-07-ff1c0872"
destination_directory = r"C:\Users\User\Downloads\watermark_dataset"
organize_dataset(source_directory, destination_directory)
