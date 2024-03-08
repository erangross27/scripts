import subprocess
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


def compress_pdf(input_file_path, output_file_path, power=3):
    quality = {
        0: '/default',
        1: '/prepress',
        2: '/printer',
        3: '/ebook',
        4: '/screen'
    }

    subprocess.call(['gswin64c', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
                    '-dPDFSETTINGS={}'.format(quality[power]),
                    '-dNOPAUSE', '-dQUIET', '-dBATCH',
                    '-sOutputFile={}'.format(output_file_path),
                     input_file_path]
    )

def select_input_file():
    filename = filedialog.askopenfilename()
    input_file_entry.delete(0, tk.END)
    input_file_entry.insert(0, filename)

def select_output_file():
    filename = filedialog.asksaveasfilename(defaultextension=".pdf")
    output_file_entry.delete(0, tk.END)
    output_file_entry.insert(0, filename)

def compress_file():
    input_file = input_file_entry.get()
    output_file = output_file_entry.get()
    compress_pdf(input_file, output_file)
    messagebox.showinfo("Success", "File compression completed successfully!")

root = tk.Tk()
root.title("PDF Compressor")

tk.Label(root, text="Input File").grid(row=0, padx=20, pady=10)
input_file_entry = tk.Entry(root)
input_file_entry.grid(row=0, column=1, padx=20)
tk.Button(root, text="Select Input File", command=select_input_file).grid(row=0, column=2, padx=20, pady=10)

tk.Label(root, text="Output File").grid(row=1, padx=20, pady=10)
output_file_entry = tk.Entry(root)
output_file_entry.grid(row=1, column=1, padx=20)
tk.Button(root, text="Select Output File", command=select_output_file).grid(row=1, column=2, padx=20, pady=10)

tk.Button(root, text="Compress File", command=compress_file).grid(row=2, column=1, pady=20)

root.mainloop()