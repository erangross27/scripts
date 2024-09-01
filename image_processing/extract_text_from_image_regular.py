"""
This script provides a GUI application for extracting text from images using Google Cloud Vision API.

The application allows users to:
1. Select an image file
2. Extract text from the selected image
3. Save the extracted text as either a TXT or CSV file

Key components:
- extract_text_from_image: Extracts text from an image using Google Cloud Vision API
- save_to_file: Saves extracted text to a file (TXT or CSV)
- select_image_path: Opens a file dialog for selecting an image
- convert_and_save: Extracts text from the selected image and saves it to a file
- main: Sets up the GUI and runs the application

Requirements:
- Google Cloud Vision API credentials (google.json file in the same directory as the script)
- google-cloud-vision library
- tkinter library

Usage:
Run the script to open the GUI. Select an image, choose the output file type (TXT or CSV),
and click 'Convert' to extract and save the text.
"""

from google.cloud import vision
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import csv

def extract_text_from_image(image_path, delimiter='\n'):
    # Get the directory of the executable
    exe_dir = os.path.dirname(os.path.abspath(__file__))

    # Build the path to google.json
    google_json_path = os.path.join(exe_dir, 'google.json')

    # Set the credentials using the environment variable
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = google_json_path

    # Create a client
    client = vision.ImageAnnotatorClient()

    # Open the image file
    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    # Perform text detection
    response = client.text_detection(image=image)
    texts = response.text_annotations

    # If texts were found, return the first one (the entire text)
    if texts:
        extracted_text = [(line, '') for line in texts[0].description.split(delimiter)]
        print(extracted_text)  # Print the extracted text
        return extracted_text
    return []

def save_to_file(data, file_path, file_type):
    with open(file_path, 'w', encoding='utf-8') as f:
        if file_type == 'csv':
            writer = csv.writer(f)
            for line in data:
                writer.writerow(line)  # Write the entire string
        else:  # file_type == 'txt'
            for line in data:
                f.write(f"{line}\n")  # Write the entire string

def select_image_path(entry):
    image_path = filedialog.askopenfilename(title='Select image file')
    entry.delete(0, tk.END)
    entry.insert(0, image_path)

def convert_and_save(entry, file_type_var):
    extracted_text = extract_text_from_image(entry.get())

    # Flatten the list of tuples into a list of strings
    extracted_text = [line for line, _ in extracted_text]

    # Save all the extracted text
    data = extracted_text

    file_path = filedialog.asksaveasfilename(defaultextension=f".{file_type_var.get()}", filetypes=((f"{file_type_var.get().upper()} file", f"*.{file_type_var.get()}"),))
    if not file_path:
        return

    save_to_file(data, file_path, file_type_var.get())

    messagebox.showinfo('Success', 'Data has been successfully saved!')
def main():
    root = tk.Tk()
    root.title('Extract Text from Image')
    root.geometry('800x300')

    entry = tk.Entry(root, width=70)
    entry.pack(pady=10)

    select_image_button = tk.Button(root, text='Select Image', command=lambda: select_image_path(entry))
    select_image_button.pack(pady=10)

    file_type_var = tk.StringVar(root)
    file_type_var.set('txt')  # set the default option
    file_type_menu = tk.OptionMenu(root, file_type_var, 'txt', 'csv')
    file_type_menu.pack(pady=10)

    convert_button = tk.Button(root, text='Convert', command=lambda: convert_and_save(entry, file_type_var))
    convert_button.pack(pady=10)

    root.mainloop()

if __name__ == '__main__':
    main()