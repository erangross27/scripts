import os
import sys
from tkinter import ttk  # Import ttk module
import tkinter as tk
from tkinter import filedialog
from google.cloud import speech_v1p1beta1 as speech

# Check if the application is running as a PyInstaller bundle
if getattr(sys, 'frozen', False):
    # The application is running as a bundle
    bundle_dir = sys._MEIPASS
else:
    # The application is running in a normal Python environment
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the directory containing ffmpeg.exe and ffprobe.exe
ffmpeg_dir = os.path.join(bundle_dir)

# Add the directory containing ffmpeg.exe and ffprobe.exe to the PATH environment variable
os.environ['PATH'] = ffmpeg_dir + os.pathsep + os.environ['PATH']

# Now you can import pydub
from pydub import AudioSegment

credential_path = os.path.join(bundle_dir, 'vitalsignai-394916-29773eaa9905.json')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential_path

def convert_m4a_to_wav(m4a_path, wav_path):
    audio = AudioSegment.from_file(m4a_path, format="m4a")
    audio.export(wav_path, format="wav")

def transcribe_audio(wav_path, output_path):
    client = speech.SpeechClient()

    with open(wav_path, "rb") as audio_file:
        audio = speech.RecognitionAudio(content=audio_file.read())

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=32000,
        language_code="iw-IL",
    )

    try:
        response = client.recognize(config=config, audio=audio)
        print("Response received from Google Cloud Speech-to-Text API.")
        with open(output_path, "w", encoding="utf-8") as file:
            for result in response.results:
                file.write("{}\n".format(result.alternatives[0].transcript))
    except Exception as e:
        print("Error occurred while calling the Google Cloud Speech-to-Text API.")
        print(e)

def browse_audio_file():
    filename = filedialog.askopenfilename(filetypes=[("Audio files", "*.m4a;*.wav")])
    if filename:
        audio_file_entry.delete(0, tk.END)
        audio_file_entry.insert(0, filename)

def browse_output_file():
    filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if filename:
        output_file_entry.delete(0, tk.END)
        output_file_entry.insert(0, filename)

def start_transcription():
    audio_file = audio_file_entry.get()
    output_file = output_file_entry.get()
    if audio_file and output_file:
        if audio_file.lower().endswith(".m4a"):
            wav_file = audio_file.rsplit(".", 1)[0] + ".wav"
            convert_m4a_to_wav(audio_file, wav_file)
            audio_file = wav_file
            progress['value'] = 50  # Update progress bar to 50 after conversion
            root.update_idletasks()  # Force update of the GUI
        transcribe_audio(audio_file, output_file)
        progress['value'] = 100  # Update progress bar to 100 after transcription
        root.update_idletasks()  # Force update of the GUI

root = tk.Tk()
root.title("Audio Transcription")
root.geometry("800x600")  # Increase the size of the window

# Set a dark blue theme
root.configure(bg='grey')

# Create a progress bar and place it at the bottom
progress = ttk.Progressbar(root, length=100, mode='determinate')
progress.pack(side=tk.BOTTOM, pady=20)

# Create entry and button for audio file with white text color
audio_file_entry = tk.Entry(root, fg='black', bg='white')
audio_file_entry.pack(pady=10)
audio_file_button = tk.Button(root, text="Browse Audio File", command=browse_audio_file, fg='black', bg='white')
audio_file_button.pack(pady=10)

# Create entry and button for output file with white text color
output_file_entry = tk.Entry(root, fg='black', bg='white')
output_file_entry.pack(pady=10)
output_file_button = tk.Button(root, text="Browse Output File", command=browse_output_file, fg='black', bg='white')
output_file_button.pack(pady=10)

# Create a button for starting the transcription with white text color
transcribe_button = tk.Button(root, text="Start Transcription", command=start_transcription, fg='black', bg='white')
transcribe_button.pack(pady=10)

root.mainloop()