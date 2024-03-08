import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import re
import time
import threading
import os
import os
import sys

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


# Rest of your code...
process = None

def select_source_file():
    source_file_path.set(filedialog.askopenfilename())

def select_destination_folder():
    destination_folder_path.set(filedialog.askdirectory())

def get_duration(file_path):
    output = subprocess.check_output(('ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path)).decode('utf-8')
    return float(output)

def update_progress_bar(value):
    progress_bar['value'] = value
    root.update_idletasks()

def convert_video():
    global process
    try:
        output_file_path = f"{destination_folder_path.get()}/output.mp4"
        if os.path.exists(output_file_path):
            if not messagebox.askokcancel("File exists", "The output file already exists. Do you want to overwrite it?"):
                return
        duration = get_duration(source_file_path.get())
        process = subprocess.Popen(['ffmpeg', '-i', source_file_path.get(), '-vcodec', codec.get(), '-s', f'hd{resolution.get()}', '-progress', 'pipe:1', output_file_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        pattern = re.compile(r"time=(\d+:\d+:\d+\.\d+)")
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

def start_conversion():
    threading.Thread(target=convert_video).start()

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        if process:
            process.terminate()
        root.destroy()

root = tk.Tk()
root.title("Video Converter")
root.geometry("800x600")

source_file_path = tk.StringVar()
destination_folder_path = tk.StringVar()
codec = tk.StringVar(value="libx264")
resolution = tk.IntVar(value=720)

tk.Button(root, text="Select Source File", command=select_source_file).pack(fill='x', padx=10, pady=10)
tk.Label(root, textvariable=source_file_path, bg="white", fg="black").pack(fill='x', padx=10, pady=10)

tk.Button(root, text="Select Destination Folder", command=select_destination_folder).pack(fill='x', padx=10, pady=10)
tk.Label(root, textvariable=destination_folder_path, bg="white", fg="black").pack(fill='x', padx=10, pady=10)

tk.OptionMenu(root, codec, "libx264", "mpeg4").pack(fill='x', padx=10, pady=10)
tk.OptionMenu(root, resolution, 480, 720, 1080).pack(fill='x', padx=10, pady=10)

tk.Button(root, text="Convert", command=start_conversion).pack(fill='x', padx=10, pady=10)

progress_bar = ttk.Progressbar(root, length=200, mode='determinate')
progress_bar.pack(fill='x', padx=10, pady=10)

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()