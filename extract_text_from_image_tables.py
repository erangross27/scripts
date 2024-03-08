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
        return texts[0].description.split(delimiter)

    return []

def save_to_file(data, file_path, file_type):
    if file_type == 'txt':
        with open(file_path, 'w', encoding='utf-8') as f:
            for name, id in data:
                f.write(f'{name} {id}\n')
    elif file_type == 'csv':
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            for name, id in data:
                writer.writerow([name, id])

def select_image_path(entry):
    image_path = filedialog.askopenfilename(title='Select image file')
    entry.delete(0, tk.END)
    entry.insert(0, image_path)

def convert_and_save(entry, file_type_var):
    extracted_text = extract_text_from_image(entry.get())

    # Separate the lines into IDs and names
    ids = [line for line in extracted_text if line.isdigit()]
    names = [line for line in extracted_text if not line.isdigit()]

    # Remove the first three lines which are headers
    names = names[3:]

    # Pair each ID with its corresponding name
    data = list(zip(names, ids))

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