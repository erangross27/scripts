from moviepy.editor import VideoFileClip

clip = VideoFileClip("output2.mp4")

print(f"The resolution of the video is: {clip.size}")