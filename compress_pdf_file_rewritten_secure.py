
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

def compress_pdf(input_file_path, output_file_path, power=3):
    # Quality settings for different compression levels
    quality = {
        0: '/default',
        1: '/prepress',
        2: '/printer',
        3: '/ebook',
        4: '/screen'
    }

    try:
        # Using subprocess.run for better error handling
        result = subprocess.run(
            ['gswin64c', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
             '-dPDFSETTINGS={}'.format(quality[power]), '-dNOPAUSE', '-dQUIET', '-dBATCH',
             '-sOutputFile={}'.format(output_file_path), input_file_path],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except Exception as e:
        messagebox.showerror("Error", f"PDF compression failed: {e}")
        return False

def select_file(file_type):
    if file_type == 'input':
        return filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    elif file_type == 'output':
        return filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])

def compress_file(input_file, output_file, power=3):
    if not input_file or not output_file:
        messagebox.showwarning("Warning", "Please select both input and output files.")
        return

    if compress_pdf(input_file, output_file, power):
        messagebox.showinfo("Success", "PDF compression completed successfully.")
    else:
        messagebox.showerror("Error", "PDF compression failed.")

def main():
    window = tk.Tk()
    window.title("PDF Compressor")

    tk.Label(window, text="Select Input PDF:").pack()
    input_file_entry = tk.Entry(window, width=50)
    input_file_entry.pack()
    tk.Button(window, text="Browse", command=lambda: input_file_entry.insert(0, select_file('input'))).pack()

    tk.Label(window, text="Select Output PDF:").pack()
    output_file_entry = tk.Entry(window, width=50)
    output_file_entry.pack()
    tk.Button(window, text="Browse", command=lambda: output_file_entry.insert(0, select_file('output'))).pack()

    tk.Button(window, text="Compress PDF", command=lambda: compress_file(input_file_entry.get(), output_file_entry.get())).pack()

    window.mainloop()

if __name__ == "__main__":
    main()
