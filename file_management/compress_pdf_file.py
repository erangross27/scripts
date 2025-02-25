"""
PDF Compressor

This script provides a graphical user interface for compressing PDF files using Ghostscript.
It allows users to select input and output files, and displays a progress bar during compression.

Features:
- File selection for input and output PDFs
- Progress bar to show compression status
- Multithreaded compression to keep the GUI responsive
- Estimated time calculation based on file size
- Error handling for common issues (e.g., missing Ghostscript)

Dependencies:
- subprocess
- tkinter
- os
- threading
- time

Note: This script requires Ghostscript to be installed and accessible in the system PATH.
"""

import subprocess
from subprocess import CREATE_NO_WINDOW
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import threading
import time
# Function to compress the PDF
def compress_pdf(input_file_path, output_file_path, power=3):
    """
    Compress pdf based on input file path, output file path, power.
    """
    quality = ['/default', '/prepress', '/printer', '/ebook', '/screen']
    return subprocess.Popen([
        'gswin64c', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
        f'-dPDFSETTINGS={quality[power]}', '-dNOPAUSE', '-dQUIET',
        '-dBATCH', f'-sOutputFile={output_file_path}', input_file_path
    ], creationflags=CREATE_NO_WINDOW)
# Function to estimate the time required for compression based on file size
def estimate_time(file_size):
    """
    Estimate time based on file size.
    """
    return max(5, min(file_size / (1024 * 1024) * 0.5, 300))

# Function to update the progress bar during compression
def update_progress(process, input_file, output_file, progress_bar, compress_button):
    """
    Updates progress based on process, input file, output file, progress bar, compress button.
    """
    input_size = os.path.getsize(input_file)
    estimated_time = estimate_time(input_size)
    start_time = time.time()
    while process.poll() is None:
        elapsed_time = time.time() - start_time
        progress_bar['value'] = min(elapsed_time / estimated_time * 100, 99)
        time.sleep(0.1)

    while not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
        time.sleep(0.1)
    progress_bar['value'] = 100
    compress_button['state'] = 'normal'
    messagebox.showinfo("Success", "File compression completed successfully!")

# Function to handle file selection
def select_file(entry, save=False):
    """
    Select file based on entry, save.
    """
    if save:
        filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    else:
        filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    entry.delete(0, tk.END)
    entry.insert(0, filename)

# Function to handle the compression process
def compress_file():
    """
    Compress file.
    """
    input_file = input_file_entry.get()
    output_file = output_file_entry.get()
    
    if not input_file or not output_file:
        messagebox.showerror("Error", "Please select both input and output files.")
        return

    if not os.path.exists(input_file):
        messagebox.showerror("Error", "Input file does not exist.")
        return

    compress_button['state'] = 'disabled'
    progress_bar['value'] = 0

    try:
        process = compress_pdf(input_file, output_file)
        threading.Thread(target=update_progress, args=(process, input_file, output_file, progress_bar, compress_button), daemon=True).start()
    except FileNotFoundError:
        messagebox.showerror("Error", "Ghostscript not found. Please install Ghostscript or add it to your PATH.")
        compress_button['state'] = 'normal'
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        compress_button['state'] = 'normal'

# Main function to create and run the GUI
def main():
    """
    Main.
    """
    global input_file_entry, output_file_entry, progress_bar, compress_button
    root = tk.Tk()
    root.title("PDF Compressor")

    tk.Label(root, text="Input File").grid(row=0, padx=20, pady=10)
    input_file_entry = tk.Entry(root, width=50)
    input_file_entry.grid(row=0, column=1, padx=20)
    tk.Button(root, text="Select Input File", command=lambda: select_file(input_file_entry)).grid(row=0, column=2, padx=20, pady=10)

    tk.Label(root, text="Output File").grid(row=1, padx=20, pady=10)
    output_file_entry = tk.Entry(root, width=50)
    output_file_entry.grid(row=1, column=1, padx=20)
    tk.Button(root, text="Select Output File", command=lambda: select_file(output_file_entry, save=True)).grid(row=1, column=2, padx=20, pady=10)

    progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progress_bar.grid(row=2, column=0, columnspan=3, pady=20, padx=20)

    compress_button = tk.Button(root, text="Compress File", command=compress_file)
    compress_button.grid(row=3, column=1, pady=20)
    root.mainloop()

# Entry point of the script
if __name__ == "__main__":
    main()
