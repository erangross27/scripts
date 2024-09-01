"""
Audio to Text Converter

This script provides a graphical user interface for converting audio files to text using Google Cloud Speech-to-Text API.

Features:
- Browse and select audio files (supports .m4a format)
- Choose save location for the output text file
- Convert audio to text with automatic punctuation and profanity filtering
- Supports Hebrew language (iw-IL)

Dependencies:
- os
- tkinter
- google.cloud.speech
- wave
- audioop
- pydub

Note: Requires a valid Google Cloud credentials file.

Usage:
1. Run the script
2. Use the GUI to select an audio file and save location
3. Enter a filename for the output
4. Click "Convert" to process the audio and generate text

The script handles audio format conversion (m4a to wav) and channel conversion (stereo to mono) automatically.
"""

import os
import tkinter as tk
from tkinter import filedialog
from google.cloud import speech
import wave
import audioop
from pydub import AudioSegment

# Set the Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./vitalsignai-394916-29773eaa9905.json"

def browse_audio_file(label):
    # Open a file dialog to select an audio file and update the label
    filename = filedialog.askopenfilename(filetypes=(("Audio Files", "*.m4a"), ("All Files", "*.*")))
    label.config(text=filename)
    return filename

def browse_save_location(label):
    # Open a directory dialog to select a save location and update the label
    foldername = filedialog.askdirectory()
    label.config(text=foldername)
    return foldername

def convert_m4a_to_wav(audio_file_path):
    # Convert m4a audio file to wav format
    audio = AudioSegment.from_file(audio_file_path, format="m4a")
    audio.export("temp.wav", format="wav")

def convert_stereo_to_mono(audio_file_path):
    # Convert stereo audio to mono
    with wave.open(audio_file_path, 'rb') as sound_file:
        params = sound_file.getparams()
        frames = sound_file.readframes(params.nframes)

    mono_frames = audioop.tomono(frames, params.sampwidth, 1, 1)
    
    with wave.open('temp_mono.wav', 'wb') as mono_sound_file:
        mono_sound_file.setparams(params)
        mono_sound_file.writeframes(mono_frames)

def convert_audio_to_text(audio_file_path, save_location, filename):
    # Convert audio to text using Google Cloud Speech-to-Text API
    convert_m4a_to_wav(audio_file_path)
    convert_stereo_to_mono("temp.wav")
    
    client = speech.SpeechClient()

    with open("temp_mono.wav", "rb") as audio_file:
        audio = speech.RecognitionAudio(content=audio_file.read())

    # Configure the recognition settings
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=32000,
        language_code="iw-IL",
        model="default",
        enable_automatic_punctuation=True,
        enable_word_confidence=True,
        profanity_filter=True,
    )
    
    # Perform the speech recognition
    response = client.recognize(config=config, audio=audio)

    # Print the transcript
    for result in response.results:
        print("Transcript: {}".format(result.alternatives[0].transcript))

    # Combine all results into a single text
    text = ""
    for result in response.results:
        text += result.alternatives[0].transcript

    # Save the transcribed text to a file
    with open(f"{save_location}/{filename}.txt", "w") as file:
        file.write(text)

def main():
    # Create the main window
    window = tk.Tk()
    window.title("Audio to Text Converter")
    window.geometry('800x600')
    window.configure(bg='white')

    # Create and pack UI elements
    audio_file_label = tk.Label(window, text="", bg='white')
    audio_file_label.pack(pady=10)

    browse_audio_button = tk.Button(window, text="Browse Audio File", command=lambda: audio_file_label.config(text=browse_audio_file(audio_file_label)))
    browse_audio_button.pack(pady=10)

    save_location_label = tk.Label(window, text="", bg='white')
    save_location_label.pack(pady=10)

    browse_save_button = tk.Button(window, text="Browse Save Location", command=lambda: save_location_label.config(text=browse_save_location(save_location_label)))
    browse_save_button.pack(pady=10)

    filename_entry = tk.Entry(window)
    filename_entry.pack(pady=10)

    convert_button = tk.Button(window, text="Convert", command=lambda: convert_audio_to_text(audio_file_label.cget("text"), save_location_label.cget("text"), filename_entry.get()))
    convert_button.pack(pady=10)

    # Start the main event loop
    window.mainloop()

if __name__ == "__main__":
    main()