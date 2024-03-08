import subprocess
import tkinter as tk
from tkinter import filedialog

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

root = tk.Tk()

input_file_entry = tk.Entry(root)
input_file_entry.pack()
tk.Button(root, text="Select Input File", command=select_input_file).pack()

output_file_entry = tk.Entry(root)
output_file_entry.pack()
tk.Button(root, text="Select Output File", command=select_output_file).pack()

tk.Button(root, text="Compress File", command=compress_file).pack()

root.mainloop()