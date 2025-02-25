"""
This script handles organize scripts.
"""

import os
import shutil

# Define the base directory
base_dir = r"C:\Users\EranGross\scripts"

# Define categories and their corresponding folders
categories = {
    "Image Processing": "image_processing",
    "Video Processing": "video_processing",
    "System Utilities": "system_utilities",
    "Network": "network",
    "Quantum Computing": "quantum_computing",
    "Calendar": "calendar",
    "Machine Learning": "machine_learning",
    "File Management": "file_management",
    "Miscellaneous": "miscellaneous"
}

# Create folders
for folder in categories.values():
    folder_path = os.path.join(base_dir, folder)
    os.makedirs(folder_path, exist_ok=True)

# Define file mappings based on the README.md content
file_mappings = {
    "Image Processing": [
        "captureImage.py", "compress_image_to_small_size.py", "convert_image_to_doc.py",
        "convert_svg_to_diffrent_images_format.py", "extract_text_from_image_regular.py",
        "extract_text_from_image_tables.py", "watermar_detection.py", "inpainting.py",
        "image_mover.py", "organize_dataset.py"
    ],
    "Video Processing": [
        "convert_mp4_codec_and_resolution_for_tv.py",
        "convert_youtube_to_download_multiple_movies_and_music.py",
        "create_movie_clip_from_images_and_sound.py", "extract_frames_from_video.py",
        "get_clip_resolution.py", "video_encoding_comparison.py"
    ],
    "System Utilities": [
        "anthropic_claude_chat.py", "anthropic_claude_chat_for_linux.py",
        "disk-space-alert-service.py", "disksizeinfo.py", "convert_audio_to_text.py",
        "system_discovery.py"
    ],
    "Network": [
        "get_hostname_nbtstat.py", "network_analyzer.py", "network_monitor.py"
    ],
    "Quantum Computing": [
        "deutsch_jozsa_algorithm.py", "quantum_key_cracking.py", "quantum_rng.py"
    ],
    "Calendar": [
        "get_calendar_events.py", "get_calendar_events_for_everyone.py",
        "get_calendar_permissions.py", "GraphServiceClient.py"
    ],
    "Machine Learning": [
        "train_watermark_yolov5.py", "mnist_cuda.py", "mnist_gpu_comparison.py"
    ],
    "File Management": [
        "compress_pdf_file.py", "numbering_pdf.py"
    ]
}

# Move files to their respective folders
for category, files in file_mappings.items():
    for file in files:
        source = os.path.join(base_dir, file)
        destination = os.path.join(base_dir, categories[category], file)
        if os.path.exists(source):
            shutil.move(source, destination)
            print(f"Moved {file} to {categories[category]}")
        else:
            print(f"File not found: {file}")

# Move remaining Python files to Miscellaneous
for file in os.listdir(base_dir):
    if file.endswith('.py') and os.path.isfile(os.path.join(base_dir, file)):
        source = os.path.join(base_dir, file)
        destination = os.path.join(base_dir, "miscellaneous", file)
        shutil.move(source, destination)
        print(f"Moved {file} to miscellaneous")

print("File organization complete.")
