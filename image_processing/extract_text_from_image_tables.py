"""
This script provides a GUI application for extracting text from images using Google Cloud Vision API.

The application allows users to:
1. Select an image file
2. Extract text from the image using Google Cloud Vision API
3. Process the extracted text to separate names and IDs
4. Save the processed data as either a TXT or CSV file

Key components:
- extract_text_from_image: Uses Google Cloud Vision API to extract text from an image
- save_to_file: Saves processed data to either a TXT or CSV file
- select_image_path: Opens a file dialog for image selection
- convert_and_save: Extracts text, processes it, and saves to a file
- main: Sets up the GUI using tkinter

Requirements:
- Google Cloud Vision API credentials (google.json file in the same directory as the script)
- Required Python packages: google-cloud-vision, tkinter

Usage:
Run the script and use the GUI to select an image, choose the output file type,
and convert the image text to a structured format.
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

    # Create an Image object from the content
    image = vision.Image(content=content)

    # Perform text detection
    response = client.text_detection(image=image)
    texts = response.text_annotations

    # If texts were found, return the first one (the entire text) split by delimiter
    if texts:
        return texts[0].description.split(delimiter)

    # Return an empty list if no text was found
    return []

def save_to_file(data, file_path, file_type):
    # Save data to a text file
    if file_type == 'txt':
        with open(file_path, 'w', encoding='utf-8') as f:
            for name, id in data:
                f.write(f'{name} {id}\n')
    # Save data to a CSV file
    elif file_type == 'csv':
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            for name, id in data:
                writer.writerow([name, id])

def select_image_path(entry):
    # Open file dialog to select an image file
    image_path = filedialog.askopenfilename(title='Select image file')
    # Clear the entry widget and insert the selected file path
    entry.delete(0, tk.END)
    entry.insert(0, image_path)

def convert_and_save(entry, file_type_var):
    # Extract text from the image
    extracted_text = extract_text_from_image(entry.get())

    # Separate the lines into IDs and names
    ids = [line for line in extracted_text if line.isdigit()]
    names = [line for line in extracted_text if not line.isdigit()]

    # Remove the first three lines which are headers
    names = names[3:]

    # Pair each ID with its corresponding name
    data = list(zip(names, ids))

    # Open file dialog to select save location and file name
    file_path = filedialog.asksaveasfilename(defaultextension=f".{file_type_var.get()}", filetypes=((f"{file_type_var.get().upper()} file", f"*.{file_type_var.get()}"),))
    if not file_path:
        return

    # Save the data to the selected file
    save_to_file(data, file_path, file_type_var.get())

    # Show success message
    messagebox.showinfo('Success', 'Data has been successfully saved!')

def main():
    # Create the main window
    root = tk.Tk()
    root.title('Extract Text from Image')
    root.geometry('800x300')

    # Create and pack the entry widget for the image path
    entry = tk.Entry(root, width=70)
    entry.pack(pady=10)

    # Create and pack the button to select an image
    select_image_button = tk.Button(root, text='Select Image', command=lambda: select_image_path(entry))
    select_image_button.pack(pady=10)

    # Create and pack the dropdown menu for file type selection
    file_type_var = tk.StringVar(root)
    file_type_var.set('txt')  # set the default option
    file_type_menu = tk.OptionMenu(root, file_type_var, 'txt', 'csv')
    file_type_menu.pack(pady=10)

    # Create and pack the convert button
    convert_button = tk.Button(root, text='Convert', command=lambda: convert_and_save(entry, file_type_var))
    convert_button.pack(pady=10)

    # Start the main event loop
    root.mainloop()

if __name__ == '__main__':
    main()