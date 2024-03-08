import os
import tkinter as tk
from tkinter import filedialog
from pytube import YouTube
from moviepy.editor import *
import threading

def browse_location():
    directory = filedialog.askdirectory()
    location_entry.delete(0, tk.END)
    location_entry.insert(tk.END, directory)

def convert_video():
    url = url_entry.get()
    format = format_var.get()
    save_location = location_entry.get()

    threading.Thread(target=download_and_convert, args=(url, format, save_location)).start()

def download_and_convert(url, format, save_location):
    try:
        # Create a YouTube object
        yt = YouTube(url)

        # Get the video stream
        if format == 'mp3':
            stream = yt.streams.filter(only_audio=True).first()
        elif format == 'mp4':
            stream = yt.streams.get_highest_resolution()
        else:
            status_label.config(text="Invalid format. Please choose 'mp3' or 'mp4'.")
            return

        # Show downloading message
        downloading_window = tk.Toplevel(window)
        downloading_window.title("Downloading")
        downloading_label = tk.Label(downloading_window, text=f"Downloading {yt.title}...", font=("Arial", 12))
        downloading_label.pack(padx=20, pady=20)
        center_window(downloading_window)

        # Download the video
        output_file = stream.download(output_path=save_location)

        # Close the downloading message window
        downloading_window.destroy()

        if format == 'mp3':
            # Show converting message
            converting_window = tk.Toplevel(window)
            converting_window.title("Converting")
            converting_label = tk.Label(converting_window, text="Converting to MP3...", font=("Arial", 12))
            converting_label.pack(padx=20, pady=20)
            center_window(converting_window)

            # Convert video to audio
            audio = AudioFileClip(output_file)
            output_file = os.path.splitext(output_file)[0] + ".mp3"
            audio.write_audiofile(output_file)
            audio.close()
            os.remove(output_file[:-4] + ".mp4")  # Remove the downloaded video file

            # Close the converting message window
            converting_window.destroy()

        status_label.config(text="Conversion complete!")
        file_location_label.config(text=f"File saved as: {output_file}")

    except Exception as e:
        status_label.config(text=f"An error occurred: {str(e)}")

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

# YouTube URL label and entry
url_label = tk.Label(window, text="YouTube URL:")
url_label.pack()
url_entry = tk.Entry(window, width=50)
url_entry.pack()

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
download_button = tk.Button(window, text="Download", command=convert_video)
download_button.pack()

# Status label
status_label = tk.Label(window, text="")
status_label.pack()

# File location label
file_location_label = tk.Label(window, text="")
file_location_label.pack()

# Run the GUI
window.mainloop()