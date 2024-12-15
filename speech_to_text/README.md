# Speech to Text Transcription Tool

Desktop application for transcribing audio and video files to text with Hebrew interface.

## Overview
This desktop application provides an easy-to-use interface for transcribing audio and video files to text using OpenAI's Whisper model. The application features a Hebrew interface and RTL text support.

## Features
- Automatic transcription with OpenAI's Whisper API
- Hebrew interface and RTL text support
- Support for multiple audio/video formats (mp3, m4a, wav, mp4, avi, mov, mkv, wmv, flv, webm)
- Auto-splitting of large files (over 25MB)
- Copy and save transcription functionality
- Progress tracking and status updates
- Custom frameless window with drag support

## Installation
1. Ensure you have Python 3.7+ installed
2. Install required dependencies:
```pip install PyQt5 openai pydub```
3. Set your OpenAI API key as environment variable OPENAI_API_KEY
4. Run the application:
```python transcription_app.py```

## Usage
1. Click "בחר קובץ אודיו/וידאו" to select an audio/video file
2. Click "תמלל" to start transcription
3. Once complete, you can:
   - Copy the text using "העתק טקסט" button
   - Save to file using "שמור קובץ" button

## Key Components
- Modern PyQt5 interface with custom styling
- Real-time progress updates
- Automatic file size handling
- RTL text formatting and Hebrew font support
- Error handling with Hebrew messages

## Technical Requirements
- Python 3.7+
- PyQt5
- OpenAI API access
- pydub for audio processing
- Internet connection for API access

## Notes
- Files larger than 25MB are automatically split into chunks
- Transcription files are saved with RTL support
- Status updates provided throughout the process
- Error messages displayed in Hebrew

// ... existing code ...
```