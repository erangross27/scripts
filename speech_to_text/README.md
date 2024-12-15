# Speech to Text Transcription Tool

Desktop application for transcribing audio and video files to text with Hebrew interface.

## Overview
This desktop application provides an easy-to-use interface for transcribing audio and video files to text using OpenAI's Whisper model. The application supports automatic transcription with Hebrew interface and RTL text support.

## Features
- Supports multiple audio and video formats: mp3, m4a, wav, mp4, avi, mov, mkv, wmv, flv, webm
- File size limit: 25 MB
- Drag-and-drop window interface
- Copy text functionality
- Save transcriptions as text files with RTL support
- Progress tracking during transcription
- Error handling and user notifications

## Interface Elements
- File selection button for audio/video files
- Transcription progress bar
- Text area with RTL support
- Control buttons:
  - Save file
  - Copy text
  - Transcribe
- Status indicators
- Window controls (minimize, maximize, close)

## Text Processing Features
- Automatic sentence formatting
- RTL text alignment
- Proper Hebrew font support
- Paragraph separation
- Clean text formatting

## Technical Notes
- Built with PyQt5 for the user interface
- Uses OpenAI's Whisper API for transcription
- Supports Hebrew language transcription by default
- Embedded API key support for distribution
- Custom window frame with drag support

## File Handling
- Automatic file size checking (25 MB limit)
- Support for multiple audio and video formats
- RTL-compatible text file saving
- UTF-8 encoding for Hebrew text support

## Error Handling
- File size validation
- API connection error handling
- File saving error handling
- User-friendly error messages in Hebrew

This application provides a streamlined interface for audio/video transcription needs, specifically optimized for Hebrew language support and RTL text handling.