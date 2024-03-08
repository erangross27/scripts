import requests
import os
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import requests

# Step 1: Get access token
def get_access_token(client_id, client_secret):
    url = "https://pdf-services.adobe.io/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret
    }
    response = requests.post(url, data=data)
    return response.json()['access_token']

def upload_asset(access_token, client_id, file_path, media_type="application/pdf"):
    # Step 1: Get an upload pre-signed URI
    url = "https://pdf-services.adobe.io/assets"
    headers = {
        "X-API-Key": client_id,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "mediaType": media_type
    }
    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()

    # Step 2: Upload the file to the uploadUri
    upload_url = response_data['uploadUri']
    with open(file_path, 'rb') as file:
        response = requests.put(upload_url, headers={"Content-Type": media_type}, data=file)

    # Step 3: Return the assetId
    return response_data['assetID']

def create_job(access_token, client_id, asset_id):
    url = "https://pdf-services.adobe.io/api/job"
    headers = {
        "X-API-Key": client_id,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "jobType": "compress-pdf",
        "sourceFile": {
            "assetID": asset_id
        }
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("Job created successfully.")
        return response.headers['Location']
    else:
        print(f"Job creation failed with status code: {response.status_code}")
        return None

# Step 4: Fetch the status
def fetch_status(access_token, client_id, location):
    url = location
    headers = {
        "Authorization": f"Bearer {access_token}",
        "x-api-key": client_id
    }
    while True:
        response = requests.get(url, headers=headers)
        status = response.json()['status']
        if status == 'done':
            return response.json()['downloadUri']
        elif status == 'failed':
            raise Exception("Job failed")
        time.sleep(5)  # wait for 5 seconds before polling again


# Step 5: Download the asset
def download_asset(download_url, save_path):
    response = requests.get(download_url)
    with open(save_path, 'wb') as f:
        f.write(response.content)

def browse_file():
    filename = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    return filename

def browse_save_location():
    filename = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    return filename

def compress_pdf(client_id, client_secret):
    try:
        access_token = get_access_token(client_id, client_secret)
        asset_id = upload_asset(access_token, client_id, file_path.get())
        location = create_job(access_token, client_id, asset_id)
        download_url = fetch_status(access_token, client_id, location)
        download_asset(download_url, save_path.get())
        messagebox.showinfo("Success", "PDF compressed successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.geometry("500x200")  # Set the size of the window
root.title("PDF Compressor")

client_id = os.getenv('ADOBE_CLIENT_ID')
client_secret = os.getenv('ADOBE_CLIENT_SECRET')

file_path = tk.StringVar()
save_path = tk.StringVar()

title = tk.Label(root, text="PDF Compressor", font=("Arial", 24))
title.pack()

select_file_button = tk.Button(root, text="Select PDF", command=lambda: file_path.set(browse_file()))
select_file_button.pack()

select_save_location_button = tk.Button(root, text="Select Save Location", command=lambda: save_path.set(browse_save_location()))
select_save_location_button.pack()

compress_button = tk.Button(root, text="Compress PDF", command=lambda: compress_pdf(client_id, client_secret))
compress_button.pack()

root.mainloop()