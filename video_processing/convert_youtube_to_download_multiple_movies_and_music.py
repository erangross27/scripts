"""
YouTube Video Converter

This script provides a graphical user interface (GUI) for downloading and converting YouTube videos to either MP3 or MP4 format.

Features:
- Multiple URL input for batch processing
- Option to choose between MP3 and MP4 output formats
- Custom save location selection
- Multithreaded download and conversion process
- Progress updates and error handling

Dependencies:
- os
- tkinter
- pytube
- moviepy
- threading
- queue

Usage:
Run the script to open the GUI. Enter YouTube URLs, select the desired output format and save location, then click "Download" to start the conversion process.

Note: This script requires an active internet connection to download videos from YouTube.
"""

import os
import tkinter as tk
from tkinter import filedialog, ttk
from pytube import YouTube
from moviepy.editor import *
import threading
import queue

# Function to open a file dialog and set the chosen directory as the save location
def browse_location():
    directory = filedialog.askdirectory()
    location_entry.delete(0, tk.END)
    location_entry.insert(tk.END, directory)

# Function to add a new URL entry field to the GUI
def add_url_entry():
    url_entry = tk.Entry(url_frame, width=50)
    url_entry.pack(side=tk.TOP, padx=5, pady=5, before=add_url_button)
    url_entries.append(url_entry)

# Function to initiate the video conversion process
def convert_videos():
    # Get all non-empty URLs from the entry fields
    urls = [entry.get().strip() for entry in url_entries if entry.get().strip()]
    format = format_var.get()
    save_location = location_entry.get()

    # Create a queue for download tasks
    download_queue = queue.Queue()
    for url in urls:
        download_queue.put((url, format, save_location))

    # Start a new thread to process downloads
    thread = threading.Thread(target=process_downloads, args=(download_queue,))
    thread.start()

# Function to process downloads from the queue
def process_downloads(download_queue):
    while not download_queue.empty():
        url, format, save_location = download_queue.get()
        try:
            download_and_convert(url, format, save_location)
        except Exception as e:
            status_label.config(text=f"Error: {str(e)}")
        download_queue.task_done()

    status_label.config(text="All conversions complete!")

# Function to download and convert a single video
def download_and_convert(url, format, save_location):
    try:
        # Create a YouTube object
        yt = YouTube(url)

        # Get the video stream based on the chosen format
        if format == 'mp3':
            stream = yt.streams.filter(only_audio=True).first()
        elif format == 'mp4':
            stream = yt.streams.get_highest_resolution()
        else:
            raise ValueError("Invalid format. Please choose 'mp3' or 'mp4'.")

        # Create a popup window to show conversion progress
        popup_window = tk.Toplevel(window)
        popup_window.title(f"Converting: {yt.title}")
        popup_label = tk.Label(popup_window, text=f"Converting: {yt.title}", font=("Arial", 12))
        popup_label.pack(padx=20, pady=20)
        center_window(popup_window)

        # Update status label
        status_label.config(text=f"Downloading: {yt.title}")

        # Download the video
        output_file = stream.download(output_path=save_location, timeout=600)  # Timeout after 10 minutes

        if format == 'mp3':
            # Update popup label
            popup_label.config(text=f"Converting: {yt.title}")

            # Convert video to audio
            audio = AudioFileClip(output_file)
            output_file = os.path.splitext(output_file)[0] + ".mp3"
            audio.write_audiofile(output_file)
            audio.close()
            os.remove(output_file[:-4] + ".mp4")  # Remove the downloaded video file

        status_label.config(text=f"Conversion complete: {yt.title}")
        file_location_label.config(text=f"File saved as: {output_file}")

        # Close the popup window
        popup_window.destroy()

    except Exception as e:
        status_label.config(text=f"Error: {str(e)}")

# Function to center a window on the screen
def center_window(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

# Create the main window
window = tk.Tk()
window.title("YouTube Video Converter")

# YouTube URL frame
url_frame = tk.Frame(window)
url_frame.pack(padx=10, pady=10)

# YouTube URL label and entry
url_label = tk.Label(url_frame, text="YouTube URLs:")
url_label.pack(side=tk.TOP, anchor=tk.W)
url_entries = []
url_entry = tk.Entry(url_frame, width=50)
url_entry.pack(side=tk.TOP, padx=5, pady=5)
url_entries.append(url_entry)

# Add URL button
add_url_button = tk.Button(url_frame, text="Add New URL", command=add_url_entry)
add_url_button.pack(side=tk.TOP, padx=5, pady=5)

# Output format label and dropdown
format_label = tk.Label(window, text="Output Format:")
format_label.pack()
format_var = tk.StringVar(window)
format_var.set("mp3")  # Default value
format_dropdown = tk.OptionMenu(window, format_var, "mp3", "mp4")
format_dropdown.pack()

# Save location label, entry, and browse button
location_label = tk.Label(window, text="Save Location:")
location_label.pack()
location_entry = tk.Entry(window, width=50)
location_entry.pack()
browse_button = tk.Button(window, text="Browse", command=browse_location)
browse_button.pack()

# Download button
download_button = tk.Button(window, text="Download", command=convert_videos)
download_button.pack(pady=10)

# Status label
status_label = tk.Label(window, text="")
status_label.pack()

# File location label
file_location_label = tk.Label(window, text="")
file_location_label.pack()

# Run the GUI
window.mainloop()