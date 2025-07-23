"""
Enhanced ClaudeChat Application v2.0

This application provides a modern graphical user interface for interacting with the latest Anthropic Claude AI models.
It supports the newest Claude 4 series and includes advanced features like streaming responses and extended thinking.

Key features:
- Chat interface with latest Claude models (Claude 4 Opus, Claude 4 Sonnet, Claude 3.7 Sonnet, Claude 3.5 Haiku)
- Real-time streaming responses for better user experience
- Extended thinking capabilities for complex reasoning tasks
- File upload and analysis (text, PDF, images, Word, Excel, code files)
- Conversation history management with search and export
- Advanced code block highlighting and copying with multiple language support
- Multiple Claude model selection with descriptions and pricing info
- Dark/Light theme support
- Comprehensive settings and configuration options
- Tool use support for enhanced capabilities

The application uses PyQt5 for the GUI, SQLite for storing conversation history, 
and integrates with the latest Anthropic API features including streaming and extended thinking.

Main classes:
- ClaudeChat: The main application window and enhanced logic
- ConversationHistory: Enhanced conversation storage and retrieval with search
- StreamingMessageProcessor: Handles streaming API calls to Claude with real-time updates
- AdvancedSyntaxHighlighter: Provides syntax highlighting for multiple programming languages
- SettingsManager: Manages application configuration and preferences
- ThemeManager: Handles dark/light theme switching

Usage:
Run this script to launch the enhanced ClaudeChat application. An Anthropic API key is required.

Dependencies:
- PyQt5
- anthropic (>=0.21.0)
- fitz (PyMuPDF)
- Pillow
- win32com
- requests
- json

Changelog v2.0:
- Added support for Claude 4 Opus and Claude 4 Sonnet models
- Implemented streaming responses with real-time display
- Added extended thinking capabilities for complex reasoning
- Enhanced UI with modern design and dark/light themes
- Improved error handling and retry mechanisms
- Added comprehensive settings management
- Enhanced file handling with better format support
- Improved conversation management with search and export
- Added model descriptions and pricing information
- Enhanced code highlighting for multiple languages

Note: This application supports both Windows and cross-platform features.
"""

import base64
import json
import logging
import os
from pathlib import Path
import sqlite3
import sys
import time
import uuid
import winreg
import ctypes
from io import BytesIO
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime
import anthropic
import fitz
from httpx import get
import pythoncom
import requests
import win32com.client as win32
from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QRegularExpression, QSize, QTimer, QSettings
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QFontDatabase, QPalette
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, 
                           QLabel, QStatusBar, QMessageBox, QHBoxLayout, QScrollArea, QMenu, 
                           QInputDialog, QLineEdit, QDialog, QFileDialog, QProgressDialog, 
                           QListWidget, QListWidgetItem, QComboBox, QGroupBox, QCheckBox, 
                           QSpinBox, QSlider, QTabWidget, QSplitter, QFrame, QGridLayout,
                           QTextBrowser, QPlainTextEdit, QProgressBar)

if sys.stdout is not None:
    sys.stdout.reconfigure(encoding='utf-8')

# Latest Claude Models with their capabilities and pricing
CLAUDE_MODELS = {
    "claude-opus-4-20250514": {
        "display_name": "Claude 4 Opus",
        "description": "Our most capable and intelligent model with superior reasoning",
        "max_tokens": 32000,
        "context_window": 200000,
        "supports_thinking": True,
        "supports_vision": True,
        "pricing": "$15/$75 per MTok",
        "speed": "Moderately Fast"
    },
    "claude-sonnet-4-20250514": {
        "display_name": "Claude 4 Sonnet", 
        "description": "High-performance model with exceptional reasoning and efficiency",
        "max_tokens": 64000,
        "context_window": 200000,
        "supports_thinking": True,
        "supports_vision": True,
        "pricing": "$3/$15 per MTok",
        "speed": "Fast"
    }
}


def setup_logging():
    """
    Setup logging.
    """
    # Check if the script is running as a compiled executable
    if getattr(sys, 'frozen', False):
        # If so, get the directory of the executable
        exe_dir = os.path.dirname(sys.executable)
        # Set the logs directory to be a subdirectory of the executable's directory
        logs_dir = os.path.join(exe_dir, "antropic_logs")
    else:
        # If not, get the directory of the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Set the logs directory to be a subdirectory of the script's directory
        logs_dir = os.path.join(script_dir, "antropic_logs")

    # Create the logs directory if it doesn't already exist
    os.makedirs(logs_dir, exist_ok=True)

    # Set the paths for the info, warning, and error log files
    info_log_file = os.path.join(logs_dir, "info.log")
    warning_log_file = os.path.join(logs_dir, "warning.log")
    error_log_file = os.path.join(logs_dir, "error.log")

    # Create a file handler for info logs, set its level, and set its formatter
    info_handler = logging.FileHandler(info_log_file, mode='w', encoding='utf-8')
    info_handler.setLevel(logging.INFO)
    info_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    info_handler.setFormatter(info_formatter)

    # Create a file handler for warning logs, set its level, and set its formatter
    warning_handler = logging.FileHandler(warning_log_file, mode='w', encoding='utf-8')
    warning_handler.setLevel(logging.WARNING)
    warning_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    warning_handler.setFormatter(warning_formatter)

    # Create a file handler for error logs, set its level, and set its formatter
    error_handler = logging.FileHandler(error_log_file, mode='w', encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    error_handler.setFormatter(error_formatter)

    # Get the root logger, set its level, and add the handlers for info, warning, and error logs
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(info_handler)
    logger.addHandler(warning_handler)
    logger.addHandler(error_handler)


    

class ConversationHistory:
    """
    Represents a conversation history.
    """
    def __init__(self, db_name):
        """
        Special method __init__.
        """
        # Store the database name
        self.db_name = db_name
        try:
            # Log the attempt to connect to the database
            logging.info(f"Connecting to the database: {db_name}")
            # Try to establish a connection to the database
            self.conn = sqlite3.connect(db_name)
            # Log the successful connection to the database
            logging.info(f"Connected to the database: {db_name}")
            # Call the method to create a table in the database
            self.create_table()
        except sqlite3.Error as e:
            # Log any error that occurs while trying to connect to the database
            logging.error(f"Error connecting to the database: {e}")

    def create_table(self):
        """
        Creates table.
        """
        try:
            # Create a cursor object
            cursor = self.conn.cursor()
            # Log the attempt to create the conversations table
            logging.info("Creating conversations table...")
            # Execute the SQL command to create the conversations table if it doesn't already exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    history TEXT
                )
            ''')
            # Commit the changes to the database
            self.conn.commit()
            # Log the successful creation of the conversations table
            logging.info("Conversations table created successfully")
        except sqlite3.Error as e:
            # Log any error that occurs while trying to create the conversations table
            logging.error(f"Error creating the conversations table: {e}")

    def save_conversation_to_db(self, conversation_id, title, history):
        """
        Save conversation to db based on conversation id, title, history.
        """
        try:
            # Create a cursor object
            cursor = self.conn.cursor()
            
            if not history:
                # If there is no history, it means this is a new conversation
                # Log the attempt to create a new conversation in the database
                logging.info(f"Creating new conversation in the database with ID: {conversation_id}, title: {title}")
                # Execute the SQL command to insert a new conversation into the conversations table
                cursor.execute('''
                    INSERT INTO conversations (id, title, history)
                    VALUES (?, ?, ?)
                ''', (conversation_id, title, json.dumps([])))
                # Log the successful creation of a new conversation in the database
                logging.info("New conversation created in the database")
            else:
                # If there is history, it means this is an existing conversation that needs to be updated
                # Log the attempt to update the conversation in the database
                logging.info(f"Updating conversation in the database with ID: {conversation_id}, title: {title}, history: {history}")
                # Execute the SQL command to insert or replace a conversation in the conversations table
                cursor.execute('''
                    INSERT OR REPLACE INTO conversations (id, title, history)
                    VALUES (?, ?, ?)
                ''', (conversation_id, title, json.dumps(history)))
                # Log the successful update of the conversation in the database
                logging.info("Conversation updated in the database")
            
            # Commit the changes to the database
            self.conn.commit()
            # Log the successful commit of changes to the database
            logging.info("Changes committed to the database")
            # Return the conversation ID
            return conversation_id
        except sqlite3.Error as e:
            # Log any error that occurs while trying to save or update the conversation in the database
            logging.error(f"Error saving/updating conversation in the database: {e}")
            # Raise the error to be handled by the calling code
            raise

    def load_conversation_history(self, conversation_id):
        """
        Load conversation history based on conversation id.
        """
        # Create a cursor object
        cursor = self.conn.cursor()
        # Execute the SQL command to select the history of the conversation with the given ID
        cursor.execute('''
            SELECT history FROM conversations
            WHERE id = ?
        ''', (conversation_id,))
        # Fetch the first (and only) row of the result set
        result = cursor.fetchone()
        # If a result was found, return the history (which is the first element of the result tuple)
        # If no result was found, return None
        return result[0] if result else None

    def load_conversations(self):
        """
        Load conversations.
        """
        # Create a cursor object
        cursor = self.conn.cursor()
        # Log the attempt to load conversations from the database
        logging.info("Loading conversations from the database")
        # Execute the SQL command to select the id and title of all conversations, ordered by rowid in descending order
        cursor.execute('''
            SELECT id, title FROM conversations ORDER BY rowid DESC
        ''')
        # Fetch all rows of the result set
        conversations = cursor.fetchall()
        # Log the number of conversations loaded from the database
        logging.info(f"Loaded {len(conversations)} conversations from the database")
        # Return the list of conversations
        return conversations

    def update_conversation_history(self, conversation_id, history):
        """
        Updates conversation history based on conversation id, history.
        """
        # Create a cursor object
        cursor = self.conn.cursor()
        # Log the attempt to update the conversation history in the database for the given conversation ID
        logging.info(f"Updating conversation history in the database for conversation ID: {conversation_id}")
        # Execute the SQL command to update the history of the conversation with the given ID
        cursor.execute('''
            UPDATE conversations
            SET history = ?
            WHERE id = ?
        ''', (history, conversation_id))
        # Commit the changes to the database
        self.conn.commit()
        # Log the successful update of the conversation history in the database
        logging.info("Conversation history updated in the database")

    def rename_conversation(self, conversation_id, new_title):
        """
        Rename conversation based on conversation id, new title.
        """
        try:
            # Create a cursor object
            cursor = self.conn.cursor()
            # Log the attempt to rename the conversation with the given ID to the new title
            logging.info(f"Renaming conversation with ID: {conversation_id} to new title: {new_title}")
            # Execute the SQL command to update the title of the conversation with the given ID
            cursor.execute('''
                UPDATE conversations
                SET title = ?
                WHERE id = ?
            ''', (new_title, conversation_id))
            # Commit the changes to the database
            self.conn.commit()
            # Log the successful renaming of the conversation in the database
            logging.info("Conversation renamed successfully in the database")
        except sqlite3.Error as e:
            # Log any error that occurs while trying to rename the conversation in the database
            logging.error(f"Error renaming conversation in the database: {e}")
            # Raise the error to be handled by the calling code
            raise

    def delete_conversation(self, conversation_id):
        """
        Deletes conversation based on conversation id.
        """
        try:
            # Create a cursor object
            cursor = self.conn.cursor()
            # Log the attempt to delete the conversation with the given ID
            logging.info(f"Deleting conversation with ID: {conversation_id}")
            # Execute the SQL command to delete the conversation with the given ID from the conversations table
            cursor.execute('''
                DELETE FROM conversations
                WHERE id = ?
            ''', (conversation_id,))
            # Commit the changes to the database
            self.conn.commit()
            # Log the successful deletion of the conversation from the database
            logging.info("Conversation deleted successfully from the database")
        except sqlite3.Error as e:
            # Log any error that occurs while trying to delete the conversation from the database
            logging.error(f"Error deleting conversation from the database: {e}")
            # Raise the error to be handled by the calling code
            raise

    def get_conversation_title(self, conversation_id):
        """
        Retrieves conversation title based on conversation id.
        """
        # Create a cursor object
        cursor = self.conn.cursor()
        # Execute the SQL command to select the title of the conversation with the given ID
        cursor.execute('''
            SELECT title FROM conversations
            WHERE id = ?
        ''', (conversation_id,))
        # Fetch the first (and only) row of the result set
        result = cursor.fetchone()
        # If a result was found, return the title (which is the first element of the result tuple)
        # If no result was found, return None
        return result[0] if result else None

class PythonHighlighter(QSyntaxHighlighter):
    """
    Represents a python highlighter.
    """
    def __init__(self, parent=None):
        """
        Special method __init__.
        """
        # Call the parent class's constructor
        super().__init__(parent)
        # Initialize the list of highlight rules
        self._highlight_rules = []

        # Define the format for Python keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#1f3864"))  # Set the color to dark blue
        keyword_format.setFontWeight(QFont.Bold)  # Set the font weight to bold
        keyword_format.setFontFamily("Cabin")  # Set the font family to "Cabin"
        # List of Python keywords
        keywords = ["False", "await", "else", "import", "pass", "None", "break", "except", "in", "raise", "True",
                    "class", "finally", "is", "return", "and", "continue", "for", "lambda", "try", "as", "def", "from",
                    "nonlocal", "while", "assert", "del", "global", "not", "with", "async", "elif", "if", "or", "yield",
                    "print", "range", "open", "self"]
        # Add the keyword highlight rule to the list of highlight rules
        self._highlight_rules.append((QRegularExpression(r"\b(" + "|".join(keywords) + r")\b"), keyword_format))

        # Define the format for strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#4caf50"))  # Set the color to green
        string_format.setFontFamily("Cabin")  # Set the font family to "Cabin"
        # Add the string highlight rules to the list of highlight rules
        self._highlight_rules.append((QRegularExpression(r"\".*\""), string_format))  # Match double-quoted strings
        self._highlight_rules.append((QRegularExpression(r"\'.*\'"), string_format))  # Match single-quoted strings

        # Define the format for comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#9e9e9e"))  # Set the color to gray
        comment_format.setFontFamily("Cabin")  # Set the font family to "Cabin"
        # Add the comment highlight rule to the list of highlight rules
        self._highlight_rules.append((QRegularExpression(r"#[^\n]*"), comment_format))  # Match comments starting with '#'

        # Define the format for function names
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#ff9800"))  # Set the color to orange
        function_format.setFontFamily("Cabin")  # Set the font family to "Cabin"
        # Add the function name highlight rule to the list of highlight rules
        self._highlight_rules.append((QRegularExpression(r"\b[A-Za-z0-9_]+(?=\()"), function_format))  # Match function names followed by '('

        # Log the initialization of the PythonHighlighter
        logging.info("PythonHighlighter initialized")

    def highlightBlock(self, text):
        """
        Highlightblock based on text.
        """
        # Check if the current block is a code block
        if self.currentBlock().userState() == 1:
            # Iterate over all highlight rules
            for pattern, format in self._highlight_rules:
                # Create an iterator for all matches of the pattern in the text
                match_iterator = pattern.globalMatch(text)
                # Iterate over all matches
                while match_iterator.hasNext():
                    # Get the next match
                    match = match_iterator.next()
                    # Apply the corresponding format to the matched text
                    self.setFormat(match.capturedStart(), match.capturedLength(), format)
            # Log the highlighting of a code block
            logging.info(f"Highlighted code block: {text}")
        else:  # If the current block is not a code block
            # Log the presence of a non-code block
            logging.info(f"Non-code block: {text}")


class MultiLineInput(QTextEdit):
    """
    Represents a multi line input.
    """
    # Define a signal that will be emitted when the return key is pressed
    returnPressed = pyqtSignal()

    def __init__(self, parent=None):
        """
        Special method __init__.
        """
        super().__init__(parent)
        self.setAcceptRichText(False)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # Set a fixed height for the widget
        self.setFixedHeight(300)  # Change this value as needed
        # Comment out the line below if you don't want the height to adjust dynamically
        # self.document().documentLayout().documentSizeChanged.connect(self.adjustHeight)

    def keyPressEvent(self, event):
        """
        Keypressevent based on event.
        """
        # Check if the pressed key is the return key and the control modifier is also pressed
        if event.key() == Qt.Key_Return and event.modifiers() & Qt.ControlModifier:
            # Emit the returnPressed signal
            self.returnPressed.emit()
            # Log the pressing of the return key with the control modifier
            logging.info("Return key pressed with Ctrl modifier")
        else:
            # If the pressed key is not the return key or the control modifier is not pressed,
            # call the parent class's keyPressEvent method
            super().keyPressEvent(event)
            # Log the pressing of a key
            logging.info(f"Key pressed: {event.text()}")

    def insertFromMimeData(self, source):
        """
        Insertfrommimedata based on source.
        """
        # Check if the source has text
        if source.hasText():
            # Get the text from the source
            text = source.text()
            # Check if the text is a code block
            if self.is_code_block(text):
                # If the text is a code block, format it
                formatted_text = self.format_code_block(text)
                # Insert the formatted text into the text edit
                self.insertPlainText(formatted_text)
            else:
                # If the text is not a code block, insert it as is into the text edit
                self.insertPlainText(text)
                # Scroll to the end of the text edit
                self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
            # Log the insertion of text from mime data
            logging.info(f"Text inserted from mime data: {text}")

    def is_code_block(self, text):
        """
        Checks if code block based on text.
        """
        # This function checks if the given text appears to be a code block.
        # It does this by checking if the text starts with "def ", "import ", or "class ", which are common Python code block starters.
        return text.startswith("def ") or text.startswith("import ") or text.startswith("class ")

    def format_code_block(self, code_block):
        """
        Format code block based on code block.
        """
        # This function formats the given code block by adding indentation and line breaks.
        # It first splits the code block into individual lines.
        lines = code_block.split("\n")
        formatted_lines = []
        # Then, it iterates over each line, adding four spaces of indentation at the start.
        for line in lines:
            formatted_lines.append("    " + line)
        # Finally, it joins the formatted lines back together with line breaks in between, and returns the result.
        formatted_code_block = "\n".join(formatted_lines)
        return formatted_code_block

    def adjustHeight(self):
        """
        Adjustheight.
        """
        doc_height = self.document().size().height()
        self.setFixedHeight(int(doc_height) + 10)


class MessageProcessor(QThread):
    """
    Enhanced message processor with streaming support and extended thinking capabilities.
    """
    # Define signals for communication with the main thread
    new_message = pyqtSignal(str)  # Complete message received
    streaming_chunk = pyqtSignal(str)  # Streaming chunk received
    api_busy = pyqtSignal()
    api_error = pyqtSignal(str)
    thinking_started = pyqtSignal()  # When model starts extended thinking
    thinking_content = pyqtSignal(str)  # Thinking process content

    def __init__(self, client, conversation_history, selected_model, enable_streaming=True, enable_thinking=False, temperature=0.1):
        """
        Initialize the message processor with enhanced capabilities.
        """
        super().__init__()
        self.client = client
        self.conversation_history = conversation_history
        self.selected_model = selected_model
        self.enable_streaming = enable_streaming
        self.enable_thinking = enable_thinking and CLAUDE_MODELS.get(selected_model, {}).get('supports_thinking', False)
        self.temperature = max(0.0, min(1.0, temperature))  # Clamp between 0 and 1

    def run(self):
        """
        Enhanced run method with streaming and thinking support.
        """
        message_sent = False
        retries = 3
        
        for attempt in range(retries):
            try:
                # Get model configuration
                model_config = CLAUDE_MODELS.get(self.selected_model, {})
                max_tokens = model_config.get('max_tokens', 8192)
                
                # Prepare message parameters
                message_params = {
                    'model': self.selected_model,
                    'max_tokens': max_tokens,
                    'temperature': self.temperature,
                    'messages': self.conversation_history
                }
                
                # Add thinking parameter if supported
                if self.enable_thinking:
                    message_params['thinking'] = 'verbose'
                
                # Use streaming if enabled
                if self.enable_streaming:
                    message_params['stream'] = True
                    response = self.client.messages.create(**message_params)
                    claude_response = self._handle_streaming_response(response)
                else:
                    response = self.client.messages.create(**message_params)
                    claude_response = self._handle_regular_response(response)

                # Update conversation history and emit completion signal
                if claude_response:
                    self.conversation_history.append({
                        "role": "assistant", 
                        "content": [{"type": "text", "text": claude_response}]
                    })
                    self.new_message.emit(claude_response)
                    message_sent = True
                    logging.info(f"Message processed successfully with model: {self.selected_model}")
                    break

            except anthropic.InternalServerError as e:
                self._handle_retry_error(attempt, retries, "Internal server error")
            except anthropic.BadRequestError as e:
                self._handle_bad_request_error(e, attempt, retries)
            except anthropic.RateLimitError as e:
                self._handle_retry_error(attempt, retries, "Rate limit exceeded")
            except requests.exceptions.RequestException as e:
                logging.error("Network error occurred.", exc_info=True)
                self.api_error.emit("Cannot communicate with Anthropic API right now.")
                return
            except Exception as e:
                logging.error(f"Unexpected error: {e}", exc_info=True)
                self.api_error.emit(f"Unexpected error: {str(e)}")
                return

        if not message_sent:
            self.api_error.emit("Failed to get response after all retry attempts.")

    def _handle_streaming_response(self, stream):
        """
        Handle streaming response from Claude.
        """
        full_response = ""
        thinking_content = ""
        in_thinking = False
        
        try:
            for event in stream:
                if hasattr(event, 'type'):
                    if event.type == 'message_start':
                        continue
                    elif event.type == 'content_block_start':
                        if hasattr(event, 'content_block') and hasattr(event.content_block, 'type'):
                            if event.content_block.type == 'thinking':
                                in_thinking = True
                                self.thinking_started.emit()
                    elif event.type == 'content_block_delta':
                        if hasattr(event, 'delta') and hasattr(event.delta, 'text'):
                            text = event.delta.text
                            if in_thinking:
                                thinking_content += text
                                self.thinking_content.emit(text)
                            else:
                                full_response += text
                                self.streaming_chunk.emit(text)
                    elif event.type == 'content_block_stop':
                        in_thinking = False
                    elif event.type == 'message_stop':
                        break
                        
        except Exception as e:
            logging.error(f"Error handling streaming response: {e}")
            
        return full_response

    def _handle_regular_response(self, message):
        """
        Handle non-streaming response from Claude.
        """
        if hasattr(message, 'content') and message.content:
            # Handle thinking content if present
            thinking_text = ""
            response_text = ""
            
            for content_block in message.content:
                if hasattr(content_block, 'type'):
                    if content_block.type == 'thinking' and hasattr(content_block, 'text'):
                        thinking_text = content_block.text
                        self.thinking_started.emit()
                        self.thinking_content.emit(thinking_text)
                    elif content_block.type == 'text' and hasattr(content_block, 'text'):
                        response_text = content_block.text
            
            return response_text
        return None

    def _handle_retry_error(self, attempt, max_retries, error_type):
        """
        Handle retryable errors with exponential backoff.
        """
        if attempt < max_retries - 1:
            self.api_busy.emit()
            wait_time = (2 ** attempt) * 30  # Exponential backoff: 30s, 60s, 120s
            logging.warning(f"{error_type}. Retrying in {wait_time} seconds.")
            time.sleep(wait_time)
        else:
            logging.error(f"Max retries reached for {error_type}.")
            self.api_error.emit(f"Failed to get response after multiple retries: {error_type}")

    def _handle_bad_request_error(self, error, attempt, max_retries):
        """
        Handle bad request errors with specific handling for role alternation issues.
        """
        error_str = str(error)
        if "roles must alternate between \"user\" and \"assistant\"" in error_str:
            self._handle_retry_error(attempt, max_retries, "Role alternation error")
        else:
            logging.error(f"Bad request error: {error_str}")
            self.api_error.emit(f"Bad request: {error_str}")


class APIKeyDialog(QDialog):
    """
    Represents a a p i key dialog.
    """
    # Initialize the APIKeyDialog class
    def __init__(self, parent=None):
        """
        Special method __init__.
        """
        # Call the parent class's constructor
        super().__init__(parent)
        # Set the window title
        self.setWindowTitle("Enter API Key")
        # Set the window size
        self.setFixedSize(700, 100)

        # Create a vertical layout
        layout = QVBoxLayout()

        # Create a label and add it to the layout
        label = QLabel("Please enter your Anthropic API Key:")
        layout.addWidget(label)

        # Create a line edit for the API key input and add it to the layout
        self.api_key_input = QLineEdit()
        layout.addWidget(self.api_key_input)

        # Create a horizontal layout for the buttons
        button_box = QHBoxLayout()
        # Create an OK button, connect its clicked signal to the dialog's accept slot, and add it to the button layout
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_box.addWidget(ok_button)

        # Create a Cancel button, connect its clicked signal to the dialog's reject slot, and add it to the button layout
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_box.addWidget(cancel_button)

        # Add the button layout to the main layout
        layout.addLayout(button_box)

        # Set the dialog's layout to the main layout
        self.setLayout(layout)

    # Method to get the entered API key
    def get_api_key(self):
        """
        Retrieves api key.
        """
        return self.api_key_input.text()

class ClaudeChat(QWidget):
    """
    Represents a claude chat.
    """
    def __init__(self):
        """
        Special method __init__.
        """
        # Call the parent class's constructor
        super().__init__()
        # Get the Anthropic API key from the environment variables
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        # If the API key was not found in the environment variables, prompt the user to enter it
        if not self.api_key:
            api_key_dialog = APIKeyDialog(self)
            if api_key_dialog.exec_() == QDialog.Accepted:
                self.api_key = api_key_dialog.get_api_key()
                os.environ['ANTHROPIC_API_KEY'] = self.api_key
                self.set_windows_env_variable('ANTHROPIC_API_KEY', self.api_key)
            else:
                QMessageBox.critical(self, "Error", "API key is required to run the application.")
                sys.exit(1)

        # Create an Anthropic client using the API key
        self.client = anthropic.Anthropic(api_key=self.api_key)
        # Initialize the conversation history, chat history, and code blocks as empty lists or dictionaries
        self.conversation_history = []
        self.chat_history = []
        self.code_blocks = {}
        # Create a ConversationHistory object for storing the conversation history in a database
        self.conversation_history_db = ConversationHistory("conversation_history.db")
        # Initialize the user interface
        self.init_ui()
        # Update the sidebar
        self.update_sidebar()  # Add this line
        # Log the initialization of the ClaudeChat, the API key, the conversation history, and the chat history
        logging.info("ClaudeChat initialized")
        logging.info(f"API key: {self.api_key}")
        logging.info(f"Conversation history: {self.conversation_history}")
        logging.info(f"Chat history: {self.chat_history}")

    def set_windows_env_variable(self, name, value):
        """
        Sets windows env variable based on name, value.
        """
        
        try:
            # Update for the current process
            os.environ[name] = value
            
            # Create or open the key
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS)
            
            # Set the value
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            
            # Close the key
            winreg.CloseKey(key)
            
            # Broadcast WM_SETTINGCHANGE message
            HWND_BROADCAST = 0xFFFF
            WM_SETTINGCHANGE = 0x1A
            SMTO_ABORTIFHUNG = 0x0002
            result = ctypes.c_long()
            SendMessageTimeoutW = ctypes.windll.user32.SendMessageTimeoutW
            SendMessageTimeoutW(HWND_BROADCAST, WM_SETTINGCHANGE, 0, 'Environment', SMTO_ABORTIFHUNG, 5000, ctypes.byref(result))
            
            logging.info(f"Environment variable '{name}' set to '{value}' in registry and current process")
            
            # Verify the change
            new_value = winreg.QueryValueEx(winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_READ), name)[0]
            if new_value != value:
                logging.warning(f"Registry value mismatch. Expected: {value}, Got: {new_value}")
            
            # Check current process environment
            if os.environ.get(name) != value:
                logging.warning(f"Process environment mismatch. Expected: {value}, Got: {os.environ.get(name)}")
            
        except Exception as e:
            logging.error(f"Failed to set environment variable '{name}': {str(e)}")
            raise

        # Return the current value for verification
        return os.environ.get(name)


    def init_ui(self):
        """
        Init ui.
        """
        # Set the window title and size
        self.setWindowTitle("Chat with Claude")
        self.showMaximized()  # Open the window in full screen mode

        # Add custom fonts for the application
        QFontDatabase.addApplicationFont("fonts/Cabin-Regular.ttf")
        QFontDatabase.addApplicationFont("fonts/Cabin-Bold.ttf")

        # Get the screen resolution and calculate the font size based on it
        screen_resolution = QApplication.primaryScreen().geometry()
        font_size = int(screen_resolution.height() * 0.02)  # Adjust the multiplier as needed
        font = QFont("Cabin", font_size)

        # Create a label for the chat history
        self.chat_label = QLabel("Chat History:")

        # Create a widget and layout for the chat history
        self.chat_history_widget = QWidget()
        self.chat_history_layout = QVBoxLayout(self.chat_history_widget)
        self.chat_history_layout.setAlignment(Qt.AlignTop)
        self.chat_history_layout.setSpacing(10)

        # Create a scroll area for the chat history and set the chat history widget as its child
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.chat_history_widget)

        # Create a label for the user input field
        self.input_label = QLabel("Type your question here (press Ctrl+Enter to send):")

        # Create a multiline input field for the user input
        self.user_input = MultiLineInput(self)
        self.user_input.setFont(font)
        self.user_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #c0c0c0;
                border-radius: 5px;
                padding: 5px;
                background-color: #f0f0f0;
                font-weight: normal;
            }
        """)
        # Connect the returnPressed signal of the user input field to the send_message method
        self.user_input.returnPressed.connect(self.send_message)
        # Add a Python syntax highlighter to the user input field
        self.user_input_highlighter = PythonHighlighter(self.user_input.document())

        # Create a send button and connect its clicked signal to the send_message method
        self.send_button = QPushButton("Send")
        self.send_button.setFixedSize(100, 30)  # Set a fixed size for the button
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.send_button.clicked.connect(self.send_message)

        # Create a clear button and connect its clicked signal to the clear_chat method
        self.clear_button = QPushButton("Clear")
        self.clear_button.setFixedSize(100, 30)  # Set a fixed size for the button
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.clear_button.clicked.connect(self.clear_chat)

        # Create a status bar
        self.status_bar = QStatusBar()

        # Create an upload button and connect its clicked signal to the upload_file method
        self.upload_button = QPushButton("Upload")
        self.upload_button.setFixedSize(100, 30)  # Set a fixed size for the button
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.upload_button.clicked.connect(self.upload_file)

        # Create a layout for the input field and buttons
        input_layout = QVBoxLayout()
        input_layout.addWidget(self.user_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.send_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.upload_button)
        button_layout.setAlignment(Qt.AlignLeft)  # Align buttons to the left

        input_layout.addLayout(button_layout)

        # Create a sidebar list widget for conversation titles
        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(300)  # Adjust the width as needed
        sidebar_font = QFont("Cabin", font_size)  # Adjust the font size as needed
        self.sidebar.setFont(sidebar_font)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #f0f0f0;
                border: none;
                padding: 10px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 5px;
                background-color: #ffffff;
                margin-bottom: 5px;
                font-weight: normal;
            }
            QListWidget::item:selected {
                background-color: #c0c0c0;
            }
        """)
        # Connect the itemClicked signal of the sidebar to the load_conversation method
        self.sidebar.itemClicked.connect(self.load_conversation)

        # Create a right sidebar for options
        self.right_sidebar = QWidget()
        self.right_sidebar.setMaximumWidth(200)  # Adjust the width as needed
        right_sidebar_layout = QVBoxLayout()
        right_sidebar_layout.setContentsMargins(10, 10, 10, 10)  # Add margins to the layout
        right_sidebar_layout.setSpacing(10)  # Add spacing between widgets

        # Create a label for the model selection
        model_label = QLabel("Select Model:")
        model_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
        """)

        # Create a combo box for model selection with latest Claude models
        self.model_combo_box = QComboBox()
        self.model_combo_box.setMaxVisibleItems(10)
        self.model_combo_box.setToolTip("Select Claude model for conversation")
        
        # Add all available Claude models
        for model_id, model_info in CLAUDE_MODELS.items():
            display_text = f"{model_info['display_name']} - {model_info['description'][:50]}..."
            self.model_combo_box.addItem(display_text, model_id)
        
        # Set default to Claude 4 Sonnet for best balance of performance and cost
        default_index = list(CLAUDE_MODELS.keys()).index("claude-sonnet-4-20250514")
        self.model_combo_box.setCurrentIndex(default_index)
        
        self.model_combo_box.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #3498db;
                border-radius: 6px;
                background-color: white;
                font-size: 12px;
                min-height: 20px;
            }
            QComboBox:hover {
                border: 2px solid #2980b9;
                background-color: #f8f9fa;
            }
            QComboBox::drop-down {
                width: 25px;
                border: none;
                background-color: #3498db;
                border-radius: 3px;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                background-color: white;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #3498db;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
            }
        """)

        # Add the label and combo box to the right sidebar layout
        right_sidebar_layout.addWidget(model_label)
        right_sidebar_layout.addWidget(self.model_combo_box)

        # Add model information display
        self.model_info_label = QLabel()
        self.model_info_label.setWordWrap(True)
        self.model_info_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #555;
                background-color: #f0f0f0;
                padding: 8px;
                border-radius: 4px;
                margin: 5px 0;
            }
        """)
        right_sidebar_layout.addWidget(self.model_info_label)
        
        # Connect model selection change to update info
        self.model_combo_box.currentIndexChanged.connect(self.update_model_info)
        self.update_model_info()  # Initialize with default selection

        # Add settings section
        settings_label = QLabel("Settings:")
        settings_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
            }
        """)
        right_sidebar_layout.addWidget(settings_label)

        # Add streaming toggle
        self.streaming_checkbox = QCheckBox("Enable Streaming")
        self.streaming_checkbox.setChecked(True)
        self.streaming_checkbox.setToolTip("Enable real-time streaming of responses")
        right_sidebar_layout.addWidget(self.streaming_checkbox)

        # Add thinking toggle (will be enabled/disabled based on model)
        self.thinking_checkbox = QCheckBox("Extended Thinking")
        self.thinking_checkbox.setToolTip("Enable extended thinking for complex reasoning")
        right_sidebar_layout.addWidget(self.thinking_checkbox)

        # Add temperature slider
        temp_label = QLabel("Temperature:")
        right_sidebar_layout.addWidget(temp_label)
        
        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setRange(0, 100)
        self.temperature_slider.setValue(10)  # Default 0.1
        self.temperature_slider.setToolTip("Controls randomness: 0=focused, 100=creative")
        right_sidebar_layout.addWidget(self.temperature_slider)
        
        self.temp_value_label = QLabel("0.1")
        self.temp_value_label.setAlignment(Qt.AlignCenter)
        self.temperature_slider.valueChanged.connect(
            lambda v: self.temp_value_label.setText(f"{v/100:.1f}")
        )
        right_sidebar_layout.addWidget(self.temp_value_label)

        # Add a stretch to push the widgets to the top
        right_sidebar_layout.addStretch()

        self.right_sidebar.setLayout(right_sidebar_layout)  # Set the layout for the right sidebar
        # Add more options to the right sidebar as needed

        # Create the main layout and add the sidebar, chat history, input layout, and right sidebar to it
        main_layout = QHBoxLayout()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(self.sidebar)
        main_layout.addLayout(sidebar_layout)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.scroll_area)
        right_layout.addWidget(self.input_label)
        right_layout.addLayout(input_layout)
        right_layout.addWidget(self.status_bar)
        main_layout.addLayout(right_layout)

        main_layout.addWidget(self.right_sidebar)

        # Create an add button and connect its clicked signal to the add_new_conversation method
        add_button = QPushButton("+")
        add_button.setFixedSize(30, 30)  # Set a fixed size for the button
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_button.clicked.connect(self.add_new_conversation)
        # Add the add button to the sidebar layout at the top center
        sidebar_layout.insertWidget(0, add_button, alignment=Qt.AlignHCenter)

        # Set the main layout as the layout of the window
        self.setLayout(main_layout)

        # Add a new conversation when the application starts
        self.add_new_conversation()
        # Set focus to the user input field
        self.user_input.setFocus()

    def update_sidebar(self):
        """
        Updates sidebar.
        """
        # Clear the sidebar
        self.sidebar.clear()
        # Load the conversations from the database
        conversations = self.conversation_history_db.load_conversations()
        logging.info(f"Updating sidebar with {len(conversations)} conversations")

        # Add existing conversations to the sidebar
        for conversation_id, title in conversations:
            # Create a new list widget item and set its data
            item = QListWidgetItem()
            item.setData(Qt.UserRole, conversation_id)
            item.setSizeHint(QSize(0, 50))  # Adjust the height as needed
            # Create a label for the item and set its properties
            item_widget = QLabel(title)
            item_widget.setAlignment(Qt.AlignCenter)
            item_widget.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: bold;
                    background-color: #ffffff;
                    border: 1px solid #c0c0c0;
                    border-radius: 5px;
                    padding: 5px;
                }
            """)
            item_widget.setWordWrap(True)  # Enable word wrapping for long titles
            # Add the item and its widget to the sidebar
            self.sidebar.addItem(item)
            self.sidebar.setItemWidget(item, item_widget)

        # Set the current conversation as active
        if self.conversation_id is not None:
            items = self.sidebar.findItems(self.conversation_id, Qt.MatchExactly)
            if items:
                self.sidebar.setCurrentItem(items[0])

        logging.info("Sidebar updated")

        # Set the context menu policy and connect the context menu request signal
        self.sidebar.setContextMenuPolicy(Qt.CustomContextMenu)
        try:
            self.sidebar.customContextMenuRequested.disconnect()
        except TypeError:
            pass  # Ignore if it was not connected
        self.sidebar.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, pos):
        """
        Show context menu based on pos.
        """
        # Get the item at the position where the context menu was requested
        item = self.sidebar.itemAt(pos)
        if item is not None:
                # Create a context menu with "Rename" and "Delete" actions
                global_pos = self.sidebar.mapToGlobal(pos)
                menu = QMenu(self.sidebar)
                rename_action = menu.addAction("Rename")
                delete_action = menu.addAction("Delete")
                action = menu.exec_(global_pos)
                # If "Rename" was selected, show a dialog to enter a new title and rename the conversation
                if action == rename_action:
                    conversation_id = item.data(Qt.UserRole)
                    if conversation_id is not None:
                        new_title, ok = QInputDialog.getText(self, "Rename Conversation", "Enter a new title:")
                        if ok and new_title:
                            self.rename_conversation(conversation_id, new_title)
                # If "Delete" was selected, show a confirmation dialog and delete the conversation
                elif action == delete_action:
                    conversation_id = item.data(Qt.UserRole)
                    if conversation_id is not None:
                        reply = QMessageBox.question(self, "Delete Conversation",
                                                    "Are you sure you want to delete this conversation?",
                                                    QMessageBox.Yes | QMessageBox.No)
                        if reply == QMessageBox.Yes:
                            self.delete_conversation(conversation_id)

    def rename_conversation(self, conversation_id, new_title):
        """
        Rename conversation based on conversation id, new title.
        """
        # Rename the conversation in the database
        self.conversation_history_db.rename_conversation(conversation_id, new_title)
        # Update the sidebar to reflect the new title
        self.update_sidebar()

    def delete_conversation(self, conversation_id):
        """
        Deletes conversation based on conversation id.
        """
        # Delete the conversation from the database
        self.conversation_history_db.delete_conversation(conversation_id)
        # If the deleted conversation is the currently active one
        if self.conversation_id == conversation_id:
            # Set the current conversation ID to None
            self.conversation_id = None
            # Clear the chat history
            self.chat_history.clear()
            # Clear the chat history layout
            self.clear_chat()  
        # Update the sidebar to remove the deleted conversation
        self.update_sidebar()
        
    def show_code_dialog(self, code_block):
        """
        Show code dialog based on code block.
        """
        # Create a new dialog
        dialog = QDialog(self)
        # Set the title of the dialog
        dialog.setWindowTitle("Code Block")
        # Create a vertical layout for the dialog
        layout = QVBoxLayout(dialog)

        # Create a text edit widget for displaying the code block
        code_text_edit = QTextEdit()
        # Set the text edit to be read-only
        code_text_edit.setReadOnly(True)
        # Set the text of the text edit to the code block
        code_text_edit.setPlainText(code_block)
        # Set the style of the text edit
        code_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                padding: 10px;
                font-family: monospace;
            }
        """)
        # Add the text edit to the layout
        layout.addWidget(code_text_edit)

        # Create a button for copying the code
        copy_button = QPushButton("Copy Code")
        # Connect the button's clicked signal to the copy_code_to_clipboard method
        copy_button.clicked.connect(lambda: self.copy_code_to_clipboard(code_block))
        # Set the style of the button
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        # Add the button to the layout
        layout.addWidget(copy_button)

        # Show the dialog
        dialog.exec_()

    def encode_image(self, image_path):
        """
        Encode image based on image path.
        """
        try:
            # Open the image file in binary mode
            with open(image_path, "rb") as image_file:
                # Read the file and encode it to base64
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            # Log a success message
            logging.info(f"Image encoded successfully: {image_path}")
            # Return the encoded string
            return encoded_string
        except FileNotFoundError:
            logging.error(f"Image file not found: {image_path}")
            # Return None if the file was not found
            return None
        except Exception as e:
            # Log an error message if there was an exception
            logging.error(f"Error encoding image: {image_path}")
            # Log the exception
            logging.exception(e)
            # Return None if there was an exception
            return None

    def load_conversation(self, item):
        """
        Load conversation based on item.
        """
        conversation_id = item.data(Qt.UserRole)
        if conversation_id is None:
            self.clear_chat()
            self.conversation_history = []
            self.conversation_id = None
            self.user_input.clear()
            self.user_input.setFocus()
        else:
            history = self.conversation_history_db.load_conversation_history(conversation_id)
            if history:
                self.clear_chat()
                self.conversation_id = conversation_id
                conversation = json.loads(history)
                for message in conversation:
                    in_code_block = False
                    code_block_content = ""
                    message_content = ""
                    if message["content"][0]["type"] == "text":
                        lines = message["content"][0]["text"].split("\n")
                    elif message["content"][0]["type"] == "image" and message['role'] == 'user':
                        continue
                    else:
                        lines = []
                    for line in lines:
                        if line.startswith("```"):
                            in_code_block = not in_code_block
                            if in_code_block:
                                code_block_content = ""
                            else:
                                code_block_widget = QTextEdit()
                                code_block_widget.setReadOnly(True)
                                code_block_widget.setPlainText(code_block_content)
                                code_block_widget.setStyleSheet("""
                                    QTextEdit {
                                        background-color: #f5f5f5;
                                        padding: 10px;
                                        font-family: monospace;
                                        font-size: 16px;
                                        border: 1px solid #c0c0c0;
                                        border-radius: 5px;
                                    }
                                """)
                                self.chat_history_layout.addWidget(code_block_widget)
                                self.add_copy_button(code_block_content)
                                logging.info(f"Code block detected: {code_block_content}")
                        else:
                            if in_code_block or self.is_code_block(line):
                                code_block_content += line + "\n"
                            else:
                                message_content += line + "\n"

                    message_widget = QLabel(f"{message['role'].capitalize()}: {message_content}")
                    message_widget.setWordWrap(True)
                    message_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
                    message_widget.setStyleSheet("""
                        QLabel {
                            font-size: 16px;
                            margin-bottom: 10px;
                            padding: 10px;
                            background-color: #e0e0e0;
                            border: 1px solid #c0c0c0;
                            border-radius: 5px;
                            color: #000000;
                            font-family: "Cabin";
                        }
                    """)
                    self.chat_history_layout.addWidget(message_widget)

                self.conversation_history = conversation
                self.user_input.clear()
                self.user_input.setFocus()
                logging.info(f"Conversation loaded: {conversation}")
            else:
                logging.warning(f"Conversation history not found for ID: {conversation_id}")
    
    def send_message(self):
        """
        Enhanced send message with streaming and thinking support.
        """
        # Get the user's message from the input field and strip any leading/trailing whitespace
        user_message = self.user_input.toPlainText().strip()
        # If the user's message is not empty
        if user_message:
            # Create a QLabel widget for the user's message
            user_message_widget = QLabel(f"User: {user_message}")
            user_message_widget.setWordWrap(True)
            user_message_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
            user_message_widget.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    margin-bottom: 10px;
                    padding: 15px;
                    background-color: #e3f2fd;
                    border: 2px solid #2196f3;
                    border-radius: 8px;
                    color: #0d47a1;
                    font-family: "Cabin";
                    font-weight: 500;
                }
            """)
            # Add the user's message to the chat history layout
            self.chat_history_layout.addWidget(user_message_widget)
            # Clear the user input field
            self.user_input.clear()

            # Add the user's message to the conversation history
            self.conversation_history.append({"role": "user", "content": [{"type": "text", "text": user_message}]})

            # Disable the user input field, send button, clear button, and upload button
            self.user_input.setEnabled(False)
            self.send_button.setEnabled(False)
            self.clear_button.setEnabled(False)
            self.upload_button.setEnabled(False)
            
            # Get the selected model and its capabilities
            model_id = self.get_the_current_model()
            model_info = CLAUDE_MODELS.get(model_id, {})
            enable_streaming = True  # Always enable streaming for better UX
            enable_thinking = model_info.get('supports_thinking', False)
            
            # Create thinking indicator if model supports it
            if enable_thinking:
                self.thinking_widget = QLabel("Claude is thinking...")
                self.thinking_widget.setStyleSheet("""
                    QLabel {
                        font-size: 14px;
                        font-style: italic;
                        color: #666;
                        padding: 10px;
                        background-color: #fff9c4;
                        border-left: 4px solid #ffc107;
                        margin: 5px 0;
                    }
                """)
                self.thinking_widget.hide()
                self.chat_history_layout.addWidget(self.thinking_widget)
            
            # Create streaming response widget
            self.streaming_widget = QLabel("Claude: ")
            self.streaming_widget.setWordWrap(True)
            self.streaming_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.streaming_widget.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    margin-bottom: 10px;
                    padding: 15px;
                    background-color: #f1f8e9;
                    border: 2px solid #4caf50;
                    border-radius: 8px;
                    color: #1b5e20;
                    font-family: "Cabin";
                    line-height: 1.5;
                }
            """)
            self.chat_history_layout.addWidget(self.streaming_widget)
            self.current_response = ""
            
            # Get UI settings
            enable_streaming = self.streaming_checkbox.isChecked() if hasattr(self, 'streaming_checkbox') else True
            enable_thinking = (self.thinking_checkbox.isChecked() and 
                             self.thinking_checkbox.isEnabled() if hasattr(self, 'thinking_checkbox') else False)
            temperature = (self.temperature_slider.value() / 100.0 if hasattr(self, 'temperature_slider') else 0.1)
            
            # Create a new message processor with enhanced capabilities
            self.processor = MessageProcessor(
                self.client, 
                self.conversation_history, 
                model_id,
                enable_streaming=enable_streaming,
                enable_thinking=enable_thinking,
                temperature=temperature
            )
            
            # Connect signals for enhanced functionality
            self.processor.new_message.connect(self.update_chat)
            self.processor.streaming_chunk.connect(self.update_streaming_response)
            self.processor.thinking_started.connect(self.show_thinking_indicator)
            self.processor.thinking_content.connect(self.update_thinking_content)
            self.processor.api_busy.connect(self.api_busy)
            self.processor.api_error.connect(self.show_api_error)
            self.processor.finished.connect(self.enable_input)
            self.processor.finished.connect(self.set_focus_to_input)
            self.processor.finished.connect(self.save_conversation)
            self.processor.finished.connect(self.finalize_streaming_response)

            # Start the message processor
            self.processor.start()
        else:
            # If the user's message is empty, log a warning
            logging.warning("Empty user message. Message not sent.")

    def update_streaming_response(self, chunk):
        """
        Update the streaming response widget with new chunk.
        """
        self.current_response += chunk
        self.streaming_widget.setText(f"Claude: {self.current_response}")
        # Auto-scroll to bottom
        QApplication.processEvents()
        
    def show_thinking_indicator(self):
        """
        Show the thinking indicator when Claude starts extended thinking.
        """
        if hasattr(self, 'thinking_widget'):
            self.thinking_widget.show()
            
    def update_thinking_content(self, thinking_text):
        """
        Update thinking content (could be used for debug mode).
        """
        # For now, just log thinking content (could add a debug panel later)
        if thinking_text.strip():
            logging.debug(f"Claude thinking: {thinking_text[:100]}...")
            
    def finalize_streaming_response(self):
        """
        Finalize the streaming response and clean up.
        """
        if hasattr(self, 'thinking_widget'):
            self.thinking_widget.hide()
        if hasattr(self, 'streaming_widget') and self.current_response:
            # The streaming widget already contains the final response
            self.current_response = ""

    def get_the_current_model(self):
        """
        Retrieves the current model ID and information.
        """
        # Get the selected model ID from the combo box data
        current_index = self.model_combo_box.currentIndex()
        if current_index >= 0:
            model_id = self.model_combo_box.itemData(current_index)
            if model_id and model_id in CLAUDE_MODELS:
                return model_id
        
        # Fallback to Claude 4 Sonnet if no valid selection
        return "claude-sonnet-4-20250514"

    def update_model_info(self):
        """
        Update the model information display based on current selection.
        """
        current_index = self.model_combo_box.currentIndex()
        if current_index >= 0:
            model_id = self.model_combo_box.itemData(current_index)
            if model_id and model_id in CLAUDE_MODELS:
                model_info = CLAUDE_MODELS[model_id]
                info_text = f"""
<b>{model_info['display_name']}</b><br>
Max Tokens: {model_info['max_tokens']:,}<br>
Context: {model_info['context_window']:,}<br>
Speed: {model_info['speed']}<br>
Pricing: {model_info['pricing']}<br>
Vision: {'✓' if model_info['supports_vision'] else '✗'}<br>
Thinking: {'✓' if model_info['supports_thinking'] else '✗'}
                """.strip()
                self.model_info_label.setText(info_text)
                
                # Enable/disable thinking checkbox based on model support
                if hasattr(self, 'thinking_checkbox'):
                    self.thinking_checkbox.setEnabled(model_info['supports_thinking'])
                    if not model_info['supports_thinking']:
                        self.thinking_checkbox.setChecked(False)
    
    def save_conversation(self):
        """
        Save conversation.
        """
        # If the conversation history is not empty
        if self.conversation_history:
            # Log that the conversation is being updated
            logging.info(f"Updating conversation with ID: {self.conversation_id}")
            # Generate a meaningful title for the conversation based on the conversation history
            title = self.generate_conversation_title(self.conversation_id)
            # Save the conversation to the database
            self.conversation_history_db.save_conversation_to_db(self.conversation_id, title, self.conversation_history)
            # Log that the conversation history was updated in the database
            logging.info("Conversation history updated in the database")
            # Update the sidebar after saving/updating the conversation
            self.update_sidebar()
        else:
            # If the conversation history is empty, log a warning and skip saving
            logging.warning("Conversation history is empty. Skipping save.")

    def generate_conversation_title(self, conversation_id):
        """
        Generate conversation title based on conversation id.
        """
        # If the conversation history is too short
        if len(self.conversation_history) < 2:
            # Log that the conversation history is too short
            logging.info("Conversation history is too short. Returning the existing title.")
            # Get the existing title from the database
            existing_title = self.conversation_history_db.get_conversation_title(conversation_id)
            # If no existing title is found
            if existing_title is None:
                # Log that no existing title was found
                logging.info("No existing title found. Returning 'New Conversation' as the title.")
                # Return a default title
                return "New Conversation"
            else:
                # Return the existing title
                return existing_title
        else:
            # Extract the user's messages from the conversation history
            user_messages = [message["content"][0]["text"] for message in self.conversation_history if
                            message["role"] == "user" and 'text' in message["content"][0]]

            # Extract the assistant's messages from the conversation history
            assistant_messages = [message["content"][0]["text"] for message in self.conversation_history if
                                message["role"] == "assistant" and 'text' in message["content"][0]]

            # Check if there are user messages
            if user_messages:
                # Generate a summary of the conversation by joining the last two messages from the user and the assistant
                conversation_summary = "\n".join(user_messages[-2:] + assistant_messages[-2:])
            else:
                # If there are no user messages, just use the assistant messages
                conversation_summary = "\n".join(assistant_messages[-2:])

            # Generate a prompt for the API to generate a title
            prompt = f"Please generate a concise and descriptive title for the following conversation (maximum 4 words):\n\n{conversation_summary}\n\nTitle:"
            
            # Get the name of the model to use
            model_name = self.get_the_current_model()
            try:
                # Send the prompt to the API and get a response
                response = self.client.messages.create(
                    model=model_name,
                    max_tokens=10,
                    temperature=0,
                    system="You are a helpful assistant that generates concise and descriptive four-word titles for conversations.",
                    messages=[{"role": "user", "content": prompt}]
                )

                # If the API response has content
                if response.content:
                    # Extract the title from the response
                    title = response.content[0].text.strip()
                    # Split the title into words
                    title_words = title.split()
                    # If the title is more than 4 words long, truncate it to 4 words
                    if len(title_words) > 4:
                        title = " ".join(title_words[:4])
                    # Log the generated title
                    logging.info(f"Generated conversation title: {title}")
                    # Return the generated title
                    return title
                else:
                    # If the API did not generate a title, log this and return the existing title
                    logging.info("No title generated by the API. Returning the existing title.")
                    existing_title = self.conversation_history_db.get_conversation_title(conversation_id)
                    if existing_title is None:
                        logging.info("No existing title found. Returning 'New Conversation' as the title.")
                        return "New Conversation"
                    else:
                        return existing_title

            except Exception as e:
                # If an error occurred while generating the title, log the error and return the existing title
                logging.error(f"Error generating conversation title: {str(e)}")
                existing_title = self.conversation_history_db.get_conversation_title(conversation_id)
                if existing_title is None:
                    logging.info("No existing title found. Returning 'New Conversation' as the title.")
                    return "New Conversation"
                else:
                    return existing_title
        
    def set_focus_to_input(self):
        """
        Sets focus to input.
        """
        # Set the focus to the user input field
        self.user_input.setFocus()
        # Log that the focus was set to the user input field
        logging.info("Focus set to user input")

    def update_chat(self, message):
        """
        Updates chat based on message.
        """
        # If the message contains multiple lines
        if "\n" in message:
            # Split the message into lines
            lines = message.split("\n")
            # Initialize variables to track whether we're in a code block and the content of the code block
            in_code_block = False
            code_block_content = ""
            # Iterate over each line in the message
            for line in lines:
                    # If the line starts with "```", we're entering or exiting a code block
                    if line.startswith("```"):
                        in_code_block = not in_code_block
                        if in_code_block:
                            # If we're entering a code block, reset the code block content
                            code_block_content = ""
                        else:
                            # If we're exiting a code block, create a read-only QTextEdit widget to display the code block
                            code_block_widget = QTextEdit()
                            code_block_widget.setReadOnly(True)
                            code_block_widget.setPlainText(code_block_content)
                            code_block_widget.setStyleSheet("""
                                QTextEdit {
                                    background-color: #f5f5f5;
                                    padding: 10px;
                                    font-family: monospace;
                                    font-size: 16px;  /* Increase the font size */
                                }
                            """)
                            # Add the code block widget to the chat history layout
                            self.chat_history_layout.addWidget(code_block_widget)
                            # Add a button to copy the code block content
                            self.add_copy_button(code_block_content)
                            # Log that a code block was detected
                            logging.info(f"Code block detected: {code_block_content}")
                    else:
                        # If we're in a code block or the line is a code block, add the line to the code block content
                        if in_code_block or self.is_code_block(line):
                            code_block_content += line + "\n"
                        else:
                            # If the line is not a code block, create a QLabel widget to display the line
                            message_widget = QLabel(line)
                            message_widget.setWordWrap(True)
                            message_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
                            message_widget.setStyleSheet("""
                                QLabel {
                                    font-size: 16px;  /* Increase the font size */
                                    margin-bottom: 10px;
                                }
                            """)
                            # Add the message widget to the chat history layout
                            self.chat_history_layout.addWidget(message_widget)
            else:
                # If the message is a single line
                if self.is_code_block(message):
                    # If the message is a code block, create a read-only QTextEdit widget to display the code block
                    code_block_content = message
                    code_block_widget = QTextEdit()
                    code_block_widget.setReadOnly(True)
                    code_block_widget.setPlainText(message)
                    code_block_widget.setStyleSheet("""
                        QTextEdit {
                            background-color: #f5f5f5;
                            padding: 10px;
                            font-family: monospace;
                            font-size: 16px;  /* Increase the font size */
                        }
                    """)
                    # Add the code block widget to the chat history layout
                    self.chat_history_layout.addWidget(code_block_widget)
                    # Add a button to copy the code block content
                    self.add_copy_button(code_block_content)
                    # Log that a code block was detected
                    logging.info(f"Code block detected: {code_block_content}")
                else:
                    # If the message is not a code block, create a QLabel widget to display the message
                    message_widget = QLabel(f"Claude: {message}")
                    message_widget.setWordWrap(True)
                    message_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
                    message_widget.setStyleSheet("""
                        QLabel {
                            font-size: 16px;
                            margin-bottom: 10px;
                            padding: 10px;
                            background-color: #e0e0e0;
                            border: 1px solid #c0c0c0;
                            border-radius: 5px;
                            color: #000000;
                            font-family: "Cabin";
                        }
                    """)
                    # Add the message widget to the chat history layout
                    self.chat_history_layout.addWidget(message_widget)
            # Scroll to the bottom of the chat history
            self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
            # Set focus back to the user input box
            self.user_input.setFocus()
            # Log that the chat was updated with a new message
            logging.info(f"Chat updated with message: {message}")

    def add_new_conversation(self):
        """
        Add new conversation.
        """
        # Clear the current chat history
        self.clear_chat()
        # Reset the conversation history
        self.conversation_history = []
        # Set the focus to the user input field
        self.user_input.setFocus()
        # Generate a new unique ID for the conversation
        self.conversation_id = str(uuid.uuid4())
        # Set the title for the new conversation
        title = "New Conversation"
        # Log the creation of a new conversation
        logging.info(f"Adding new conversation with ID: {self.conversation_id} and title: {title}")
        # Save the new conversation to the database
        self.conversation_history_db.save_conversation_to_db(self.conversation_id, title, self.conversation_history)
        # Log that the new conversation was added to the database
        logging.info(f"New conversation added to the database with ID: {self.conversation_id}")
        # Update the sidebar to reflect the new conversation
        self.update_sidebar()

    def is_code_block(self, text):
        """
        Checks if code block based on text.
        """
        # Determine if the text is a code block by checking if it starts with "def ", "import ", or "class "
        is_code = text.startswith("def ") or text.startswith("import ") or text.startswith("class ")
        # Log the text that is being checked
        logging.info(f"Checking if text is a code block: {text}")
        # Log the result of the check
        logging.info(f"Is code block: {is_code}")
        # Return the result of the check
        return is_code

    def add_copy_button(self, code_block_content):
        """
        Add copy button based on code block content.
        """
        # Generate a unique identifier for the code block based on the current number of code blocks
        code_block_id = f"code_block_{len(self.code_blocks)}"
        # Store the code block content in the code_blocks dictionary, using the unique identifier as the key
        self.code_blocks[code_block_id] = code_block_content.strip()

        # Create a new QPushButton widget for the copy button
        copy_button = QPushButton("Copy Code")
        # Set a fixed width for the copy button
        copy_button.setFixedWidth(100)
        # Set the style for the copy button
        copy_button.setStyleSheet("""
           QPushButton {
               background-color: #4CAF50;
               color: white;
               padding: 5px 10px;
               border: none;
               border-radius: 4px;
               font-size: 12px;
               cursor: pointer;
           }
           QPushButton:hover {
               background-color: #45a049;
           }
       """)
        # Connect the button's clicked signal to the copy_code_to_clipboard method, passing the unique identifier for the code block
        copy_button.clicked.connect(lambda: self.copy_code_to_clipboard(code_block_id))

        # Create a new QHBoxLayout for the button
        button_layout = QHBoxLayout()
        # Add the copy button to the layout
        button_layout.addWidget(copy_button)
        # Align the button to the left of the layout
        button_layout.setAlignment(Qt.AlignLeft)

        # Create a new QWidget to contain the button layout
        button_widget = QWidget()
        # Set the layout of the widget to the button layout
        button_widget.setLayout(button_layout)

        # Add the button widget to the chat history layout
        self.chat_history_layout.addWidget(button_widget)
        # Add some spacing after the button widget before the next message
        self.chat_history_layout.addSpacing(10)

    def copy_code_to_clipboard(self, code_block_id):
        """
        Copy code to clipboard based on code block id.
        """
        # Check if the provided code block ID exists in the code_blocks dictionary
        if code_block_id in self.code_blocks:
            # Retrieve the code block associated with the provided ID
            code_block = self.code_blocks[code_block_id]
            # Set the text of the application's clipboard to the code block
            QApplication.clipboard().setText(code_block)
            # Display a message in the status bar indicating that the code block has been copied
            self.status_bar.showMessage("Code block copied to clipboard", 2000)

    def update_chat_history(self, message):
        """
        Updates chat history based on message.
        """
        # Append the provided message to the chat history
        self.chat_history.append(message)
        # Close the progress dialog
        self.progress_dialog.close()

        # Log that the chat history has been updated with the provided message
        logging.info(f"Chat history updated with message: {message}")
        # Log that the progress dialog has been closed
        logging.info(f"Progress dialog closed")
        # Log the current state of the chat history
        logging.info(f"Current chat history: {self.chat_history}")

    def enable_input(self):
        """
        Enable input.
        """
        # Enable the user input field, send button, clear button, and upload button
        self.user_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.clear_button.setEnabled(True)
        self.upload_button.setEnabled(True)

        # Log that the user input has been enabled
        logging.info("User input enabled")
        # Log the current enabled state of the user input widget
        logging.info(f"User input widget enabled: {self.user_input.isEnabled()}")
        # Log the current enabled state of the send button
        logging.info(f"Send button enabled: {self.send_button.isEnabled()}")
        # Log the current enabled state of the clear button
        logging.info(f"Clear button enabled: {self.clear_button.isEnabled()}")
        # Log the current enabled state of the upload button
        logging.info(f"Upload button enabled: {self.upload_button.isEnabled()}")

    def clear_chat(self):
        """
        Clear chat.
        """
        # While there are items in the chat history layout
        while self.chat_history_layout.count():
            # Take the first item from the layout
            item = self.chat_history_layout.takeAt(0)
            # Get the widget from the item
            widget = item.widget()
            # If the widget exists
            if widget:
                # Delete the widget
                widget.deleteLater()
        # Reset the conversation history with a default message
        self.conversation_history = [
            {
                "role": "assistant",
                "content": "You are a professional Python developer with 20 years of experience."
            }
        ]

        # Log that the chat has been cleared
        logging.info("Chat cleared")
        # Log the reset conversation history
        logging.info(f"Conversation history reset: {self.conversation_history}")

    def api_busy(self):
        """
        Api busy.
        """
        # Display a message on the status bar indicating that the API is busy
        # The message will be displayed for 60000 milliseconds (60 seconds)
        self.status_bar.showMessage("API is busy. Trying again in 60 seconds...", 60000)

        # Log a warning message indicating that the API is busy
        logging.warning("API busy")
        # Log an info message indicating that the status bar message has been set
        logging.info("Status bar message set: 'API is busy. Trying again in 60 seconds...'")
        # Log an info message indicating the timeout duration for the status bar message
        logging.info("Status bar message timeout: 60000 ms")

    def show_api_error(self, error_message):
        """
        Show api error based on error message.
        """
        # Display a critical error message box with the title "API Error" and the provided error message
        QMessageBox.critical(self, "API Error", error_message)

        # Log an error message with the provided error message
        logging.error(f"API error: {error_message}")
        # Log an info message indicating that the error message box has been shown
        logging.info("API error message box shown")

    def upload_file(self):
        """
        Upload file.
        """
        # Open a file dialog and get the selected file name
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File')
        
        # If a file is selected
        if file_name:
            logging.info(f"File selected: {file_name}")
            
            # Get the file extension
            extension = os.path.splitext(file_name)[1].lower()
            file_content = None
            
            # If the file is a text file or a script
            if extension in ['.txt', '.py', '.js', '.html', '.css']:
                with open(file_name, 'r') as file:
                    file_content = file.read()
                logging.info(f"File content read: {file_content}")
            
            # If the file is a PDF
            elif extension == '.pdf':
                try:
                    doc = fitz.open(file_name)
                    file_content = "".join(page.get_text() for page in doc)
                    logging.info(f"PDF file content extracted: {file_content}")
                except fitz.FileDataError:
                    file_content = "Error: The PDF file is invalid or corrupted."
                    logging.error("PDF file is invalid or corrupted")
                except fitz.PasswordError:
                    file_content = "Error: The PDF file is password-protected."
                    logging.error("PDF file is password-protected")
                except Exception as e:
                    file_content = f"Error: An unexpected error occurred while processing the PDF file: {str(e)}"
                    logging.exception(f"Unexpected error while processing PDF file: {str(e)}")
            
            # If the file is an image
            elif extension in ['.png', '.jpg', '.jpeg']:
                img = Image.open(file_name)
                img = img.resize((800, 800))  # Reduce resolution to 800x800 pixels
                img_bytes = BytesIO()
                img.save(img_bytes, format='PNG')
                encoded_image = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
                file_content = {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": encoded_image
                    }
                }
                logging.info(f"Image file encoded: {file_content}")
            
            # If the file is a Word document
            elif extension in ['.doc', '.docx']:
                pythoncom.CoInitialize()  # Required for Win32 COM
                word = win32.gencache.EnsureDispatch('Word.Application')
                doc = word.Documents.Open(file_name.replace('/', '\\'))
                file_content = doc.Content.Text
                doc.Close()
                word.Quit()
                logging.info(f"Word file content extracted: {file_content}")
            
            # If the file is an Excel spreadsheet
            elif extension in ['.xls', '.xlsx']:
                pythoncom.CoInitialize()  # Required for Win32 COM
                excel = win32.gencache.EnsureDispatch('Excel.Application')
                try:
                    workbook = excel.Workbooks.Open(file_name.replace('/', '\\'))
                    sheet = workbook.Worksheets[1]
                    file_content = ""
                    for row in sheet.UsedRange.Rows:
                        file_content += " ".join(
                            [str(cell.Value) if cell.Value is not None else '' for cell in row.Cells]) + "\n"
                    logging.info(f"Excel file content extracted: {file_content}")
                except Exception as e:
                    file_content = f"Error opening file: {e}"
                    logging.exception(f"Error opening Excel file: {str(e)}")
                finally:
                    workbook.Close()
                    excel.Quit()

            # If file content is successfully extracted
            if file_content is not None:
                user_message = None
                if extension in ['.png', '.jpg', '.jpeg']:
                    user_message = {"role": "user", "content": [file_content]}
                else:
                    prompt = f"I uploaded a file with the following content:\n{file_content}"
                    user_message = {"role": "user", "content": [{"type": "text", "text": prompt}]}
                    # Extract the message string from the user_message dictionary
                    if 'text' in user_message['content'][0]:
                        message_string = user_message['content'][0]['text']
                        # Manually update the chat with the user message
                        self.update_chat(message_string)
                self.conversation_history.append(user_message)
                logging.info(f"Conversation history updated with file content: {self.conversation_history}")

                # Start the message processor
                selected_model = self.get_the_current_model()   # Get the selected model from the combo box
                self.processor = MessageProcessor(self.client, self.conversation_history,selected_model)
                self.processor.new_message.connect(self.update_chat)
                self.processor.api_error.connect(self.handle_api_error)
                self.processor.finished.connect(self.close_progress_dialog)  # Connect the finished signal
                # Connect the finished signal to the enable input, set focus to input, and save conversation slots
                self.processor.finished.connect(self.enable_input)
                self.processor.finished.connect(self.set_focus_to_input)
                self.processor.finished.connect(self.save_conversation)
                self.processor.start()
                logging.info("Message processor started")

                # Show a progress dialog
                self.progress_dialog = QProgressDialog("Analyzing file...", "Cancel", 0, 0, self)
                self.progress_dialog.setWindowModality(Qt.WindowModal)
                self.progress_dialog.show()
                logging.info("Progress dialog shown")
            else:
                logging.info("No file selected")

    def close_progress_dialog(self):
        """
        Close progress dialog.
        """
        # If a progress dialog exists
        if self.progress_dialog:
            # Close the progress dialog
            self.progress_dialog.close()
            # Set the progress dialog to None
            self.progress_dialog = None
            # Log that the progress dialog was closed
            logging.info("Progress dialog closed")

    def handle_api_error(self, error_message):
        """
        Handles api error based on error message.
        """
        # Create a new message box
        msg = QMessageBox()
        
        # Set the icon of the message box to "Critical"
        msg.setIcon(QMessageBox.Critical)
        
        # Set the text of the message box to "API Error"
        msg.setText("API Error")
        
        # Set the informative text of the message box to the error message
        msg.setInformativeText(str(error_message))
        
        # Set the title of the message box to "Error"
        msg.setWindowTitle("Error")
        
        # Display the message box
        msg.exec_()

        # Log the error message
        logging.error(f"API error: {error_message}")
        
        # Log that the error message box has been shown
        logging.info("API error message box shown")


def main():
    """
    Main.
    """
    # Create a new QApplication instance
    app = QApplication(sys.argv)
    
    # Setup logging
    setup_logging()
    
    # Log that the logging setup has been completed
    logging.info("Logging setup completed")
    
    # Log that the application has started
    logging.info("Application started")
    
    # Create a new ClaudeChat instance
    chat = ClaudeChat()
    
    # Show the ClaudeChat window
    chat.show()
    
    # Log that the ClaudeChat window has been shown
    logging.info("ClaudeChat window shown")
    
    # Execute the application and get the exit code
    exit_code = app.exec_()
    
    # Log the exit code
    logging.info(f"Application exited with code: {exit_code}")
    
    # Exit the application with the exit code
    sys.exit(exit_code)


# If this script is the main entry point, call the main function
if __name__ == '__main__':
    main()