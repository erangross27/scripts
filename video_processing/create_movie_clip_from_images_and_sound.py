"""
This script creates a video slideshow from a directory of images with a repeating background sound.

The script performs the following steps:
1. Loads images from a specified directory.
2. Creates a video clip from the images, displaying each for a set duration.
3. Loads a background sound file.
4. Repeats the background sound to match the length of the video.
5. Combines the image sequence with the repeated background sound.
6. Outputs the final video file.

Required libraries:
- os: For file and directory operations.
- cv2: For image loading and processing.
- moviepy.editor: For video and audio manipulation.

Usage:
- Set the 'image_directory' variable to the path of your image folder.
- Set the 'output_video' variable to your desired output video filename.
- Set the 'image_duration' variable to the number of seconds each image should be displayed.
- Set the 'background_sound' variable to the path of your MP3 background sound file.
- Run the script to generate the video.

Note: Ensure all required libraries are installed before running the script.
"""

import os
import cv2
from moviepy.editor import ImageSequenceClip, AudioFileClip, concatenate_audioclips

# Set the path to the directory containing the images
image_directory = "path/to/your/image/directory"

# Set the output video file name
output_video = "output_video.mp4"

# Set the duration for each image (in seconds)
image_duration = 3

# Set the path to the MP3 background sound file
background_sound = "path/to/your/background/sound.mp3"

# Get a list of image file names in the directory
image_files = [f for f in os.listdir(image_directory) if f.endswith((".jpg", ".jpeg", ".png"))]

# Sort the image files alphabetically
image_files.sort()

# Create a list to store the loaded images
images = []

# Load the images using OpenCV
for image_file in image_files:
    image_path = os.path.join(image_directory, image_file)
    image = cv2.imread(image_path)
    images.append(image)

# Create an ImageSequenceClip from the loaded images
clip = ImageSequenceClip(images, durations=[image_duration] * len(images))

# Load the background sound
audio = AudioFileClip(background_sound)

# Calculate the number of times the audio needs to be repeated
repeat_times = int(clip.duration / audio.duration) + 1

# Create a list of audio clips
audio_clips = [audio] * repeat_times

# Concatenate the audio clips to create a repeated audio clip
repeated_audio = concatenate_audioclips(audio_clips)

# Trim the repeated audio to match the length of the image sequence
repeated_audio = repeated_audio.subclip(0, clip.duration)

# Set the repeated audio as the background sound for the clip
clip = clip.set_audio(repeated_audio)

# Write the clip to the output video file
clip.write_videofile(output_video, fps=24)