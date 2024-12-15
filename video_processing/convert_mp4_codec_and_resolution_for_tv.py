"""
Video Converter Application

This script creates a GUI application for converting video files using FFmpeg.
It allows users to select a source video file, choose a destination folder,
and set conversion parameters such as codec and resolution. The application
shows a progress bar during the conversion process.

Features:
- Select source video file and destination folder
- Choose video codec (libx264 or mpeg4)
- Select output resolution (480p, 720p, or 1080p)
- Display conversion progress
- Handle FFmpeg processes and update GUI asynchronously

Dependencies:
- tkinter
- subprocess
- re
- time
- threading
- os
- sys
- FFmpeg (must be accessible in the system PATH or bundled with the application)

Note: This script is designed to work both as a standalone Python script and
when bundled with PyInstaller.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import re
import sys
import threading
import os
# Check if the application is running as a PyInstaller bundle
if getattr(sys, 'frozen', False):
    # The application is running as a bundle
    bundle_dir = sys._MEIPASS
else:
    # The application is running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the directory containing ffmpeg.exe and ffprobe.exe
ffmpeg_dir = os.path.join(bundle_dir)

# Add the directory containing the ffmpeg binaries to the system's PATH
os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ['PATH']

# Global variable to store the ffmpeg subprocess
process = None

# Function to open a file dialog and set the source file path
def select_source_file():
    source_file_path.set(filedialog.askopenfilename())

# Function to open a folder dialog and set the destination folder path
def select_destination_folder():
    destination_folder_path.set(filedialog.askdirectory())

# Function to get the duration of a video file using ffprobe
def get_duration(file_path):
    output = subprocess.check_output(('ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path)).decode('utf-8')
    return float(output)

# Function to update the progress bar
def update_progress_bar(value):
    progress_bar['value'] = value
    root.update_idletasks()

# Function to perform the video conversion
def convert_video():
    global process
    try:
        output_file_path = f"{destination_folder_path.get()}/output.mp4"
        # Check if the output file already exists
        if os.path.exists(output_file_path):
            if not messagebox.askokcancel("File exists", "The output file already exists. Do you want to overwrite it?"):
                return
        # Get the duration of the input video
        duration = get_duration(source_file_path.get())
        # Start the ffmpeg process
        process = subprocess.Popen(['ffmpeg', '-i', source_file_path.get(), '-vcodec', codec.get(), '-s', f'hd{resolution.get()}', '-progress', 'pipe:1', output_file_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # Regular expression to extract time information from ffmpeg output
        pattern = re.compile(r"time=(\d+:\d+:\d+\.\d+)")
        # Process ffmpeg output and update progress bar
        for line in iter(process.stdout.readline, b''):
            match = pattern.search(line.decode('utf-8'))
            if match:
                time_parts = match.group(1).split(':')
                elapsed_time = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + float(time_parts[2])
                progress = elapsed_time / duration * 100
                root.after(1, update_progress_bar, progress)
        messagebox.showinfo("Success", "Video conversion completed successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to start the conversion process in a separate thread
def start_conversion():
    threading.Thread(target=convert_video).start()

# Function to handle the window closing event
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        if process:
            process.terminate()
        root.destroy()

# Create the main window
root = tk.Tk()
root.title("Video Converter")
root.geometry("800x600")

# Create StringVar and IntVar to store user input
source_file_path = tk.StringVar()
destination_folder_path = tk.StringVar()
codec = tk.StringVar(value="libx264")
resolution = tk.IntVar(value=720)

# Create and pack GUI elements
tk.Button(root, text="Select Source File", command=select_source_file).pack(fill='x', padx=10, pady=10)
tk.Label(root, textvariable=source_file_path, bg="white", fg="black").pack(fill='x', padx=10, pady=10)

tk.Button(root, text="Select Destination Folder", command=select_destination_folder).pack(fill='x', padx=10, pady=10)
tk.Label(root, textvariable=destination_folder_path, bg="white", fg="black").pack(fill='x', padx=10, pady=10)

tk.OptionMenu(root, codec, "libx264", "mpeg4").pack(fill='x', padx=10, pady=10)
tk.OptionMenu(root, resolution, 480, 720, 1080).pack(fill='x', padx=10, pady=10)

tk.Button(root, text="Convert", command=start_conversion).pack(fill='x', padx=10, pady=10)

# Create and pack the progress bar
progress_bar = ttk.Progressbar(root, length=200, mode='determinate')
progress_bar.pack(fill='x', padx=10, pady=10)

# Set up the window closing protocol
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the main event loop
root.mainloop()