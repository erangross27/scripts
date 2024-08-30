"""
This script demonstrates how to load a video file and retrieve its resolution using the moviepy library.

The script performs the following steps:
1. Imports the VideoFileClip class from moviepy.editor.
2. Loads a video file named "output2.mp4".
3. Prints the resolution (width and height) of the loaded video.

Usage:
    Ensure that the moviepy library is installed and that the video file "output2.mp4" 
    exists in the same directory as this script.

Note:
    This script requires the moviepy library to be installed. You can install it using pip:
    pip install moviepy
"""

# Import the VideoFileClip class from the moviepy.editor module
from moviepy.editor import VideoFileClip

# Create a VideoFileClip object by loading the video file "output2.mp4"
clip = VideoFileClip("output2.mp4")

# Print the resolution (size) of the video
# clip.size returns a tuple containing the width and height of the video in pixels
print(f"The resolution of the video is: {clip.size}")