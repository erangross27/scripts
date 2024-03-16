import base64
import json
import logging
import os
import sqlite3
import sys
import time
import uuid
from io import BytesIO

import anthropic
import fitz
import pythoncom
import requests
import win32com.client as win32
from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QRegularExpression, QSize
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QFontDatabase
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QStatusBar, QMessageBox, \
    QHBoxLayout, QScrollArea, QMenu, QInputDialog
from PyQt5.QtWidgets import QFileDialog, QProgressDialog, QListWidget, QListWidgetItem, QDialog

if sys.stdout is not None:
    sys.stdout.reconfigure(encoding='utf-8')


def setup_logging():
    if getattr(sys, 'frozen', False):
        # Running as a compiled executable
        exe_dir = os.path.dirname(sys.executable)
        logs_dir = os.path.join(exe_dir, "antropic_logs")
    else:
        # Running as a script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(script_dir, "antropic_logs")

    # Create the logs directory if it doesn't exist
    os.makedirs(logs_dir, exist_ok=True)

    # Set the log file paths
    info_log_file = os.path.join(logs_dir, "info.log")
    warning_log_file = os.path.join(logs_dir, "warning.log")
    error_log_file = os.path.join(logs_dir, "error.log")

    # Configure logging for info logs
    info_handler = logging.FileHandler(info_log_file, mode='w', encoding='utf-8')
    info_handler.setLevel(logging.INFO)
    info_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    info_handler.setFormatter(info_formatter)

    # Configure logging for warning logs
    warning_handler = logging.FileHandler(warning_log_file, mode='w', encoding='utf-8')
    warning_handler.setLevel(logging.WARNING)
    warning_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    warning_handler.setFormatter(warning_formatter)

    # Configure logging for error logs
    error_handler = logging.FileHandler(error_log_file, mode='w', encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    error_handler.setFormatter(error_formatter)

    # Create a logger and add the handlers
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(info_handler)
    logger.addHandler(warning_handler)
    logger.addHandler(error_handler)


class ConversationHistory:
    def __init__(self, db_name):
        self.db_name = db_name
        try:
            logging.info(f"Connecting to the database: {db_name}")
            self.conn = sqlite3.connect(db_name)
            logging.info(f"Connected to the database: {db_name}")
            self.create_table()
        except sqlite3.Error as e:
            logging.error(f"Error connecting to the database: {e}")

    def create_table(self):
        try:
            cursor = self.conn.cursor()
            logging.info("Creating conversations table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    title TEXT,
                    history TEXT
                )
            ''')
            self.conn.commit()
            logging.info("Conversations table created successfully")
        except sqlite3.Error as e:
            logging.error(f"Error creating the conversations table: {e}")

    def save_conversation_to_db(self, conversation_id, title, history):
        try:
            cursor = self.conn.cursor()
            
            if not history:
                # New conversation with empty history
                logging.info(f"Creating new conversation in the database with ID: {conversation_id}, title: {title}")
                cursor.execute('''
                    INSERT INTO conversations (id, title, history)
                    VALUES (?, ?, ?)
                ''', (conversation_id, title, json.dumps([])))
                logging.info("New conversation created in the database")
            else:
                # Existing conversation with history
                logging.info(f"Updating conversation in the database with ID: {conversation_id}, title: {title}, history: {history}")
                cursor.execute('''
                    INSERT OR REPLACE INTO conversations (id, title, history)
                    VALUES (?, ?, ?)
                ''', (conversation_id, title, json.dumps(history)))
                logging.info("Conversation updated in the database")
            
            self.conn.commit()
            logging.info("Changes committed to the database")
            return conversation_id
        except sqlite3.Error as e:
            logging.error(f"Error saving/updating conversation in the database: {e}")
            raise

    def load_conversation_history(self, conversation_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT history FROM conversations
            WHERE id = ?
        ''', (conversation_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def load_conversations(self):
        cursor = self.conn.cursor()
        logging.info("Loading conversations from the database")
        cursor.execute('''
            SELECT id, title FROM conversations ORDER BY rowid DESC
        ''')
        conversations = cursor.fetchall()
        logging.info(f"Loaded {len(conversations)} conversations from the database")
        return conversations

    def update_conversation_history(self, conversation_id, history):
        cursor = self.conn.cursor()
        logging.info(f"Updating conversation history in the database for conversation ID: {conversation_id}")
        cursor.execute('''
            UPDATE conversations
            SET history = ?
            WHERE id = ?
        ''', (history, conversation_id))
        self.conn.commit()
        logging.info("Conversation history updated in the database")

    def rename_conversation(self, conversation_id, new_title):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE conversations
            SET title = ?
            WHERE id = ?
        ''', (new_title, conversation_id))
        self.conn.commit()

    def delete_conversation(self, conversation_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM conversations
            WHERE id = ?
        ''', (conversation_id,))
        self.conn.commit()

    def get_conversation_title(self, conversation_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT title FROM conversations
            WHERE id = ?
        ''', (conversation_id,))
        result = cursor.fetchone()
        return result[0] if result else None



class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._highlight_rules = []

        # Define the format for keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#1f3864"))  # Set the color to dark blue
        keyword_format.setFontWeight(QFont.Bold)  # Set the font weight to bold
        keywords = ["False", "await", "else", "import", "pass", "None", "break", "except", "in", "raise", "True",
                    "class", "finally", "is", "return", "and", "continue", "for", "lambda", "try", "as", "def", "from",
                    "nonlocal", "while", "assert", "del", "global", "not", "with", "async", "elif", "if", "or", "yield",
                    "print", "range", "open", "self"]
        self._highlight_rules.append((QRegularExpression(r"\b(" + "|".join(keywords) + r")\b"), keyword_format))

        # Define the format for strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#4caf50"))  # Set the color to green
        self._highlight_rules.append((QRegularExpression(r"\".*\""), string_format))  # Match double-quoted strings
        self._highlight_rules.append((QRegularExpression(r"\'.*\'"), string_format))  # Match single-quoted strings

        # Define the format for comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#9e9e9e"))  # Set the color to gray
        self._highlight_rules.append(
            (QRegularExpression(r"#[^\n]*"), comment_format))  # Match comments starting with '#'

        # Define the format for functions
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#ff9800"))  # Set the color to orange
        self._highlight_rules.append(
            (QRegularExpression(r"\b[A-Za-z0-9_]+(?=\()"), function_format))  # Match function names followed by '('

        logging.info("PythonHighlighter initialized")

    def highlightBlock(self, text):
        if self.currentBlock().userState() == 1:  # Check if inside a code block
            for pattern, format in self._highlight_rules:
                match_iterator = pattern.globalMatch(text)
                while match_iterator.hasNext():
                    match = match_iterator.next()
                    self.setFormat(match.capturedStart(), match.capturedLength(),
                                   format)  # Apply the corresponding format to the matched text
            logging.info(f"Highlighted code block: {text}")
        else:  # Outside a code block
            logging.info(f"Non-code block: {text}")


class MultiLineInput(QTextEdit):
    returnPressed = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() & Qt.ControlModifier:
            self.returnPressed.emit()
            logging.info("Return key pressed with Ctrl modifier")
        else:
            super().keyPressEvent(event)
            logging.info(f"Key pressed: {event.text()}")

    def insertFromMimeData(self, source):
        if source.hasText():
            text = source.text()
            if self.is_code_block(text):
                # Format the code block
                formatted_text = self.format_code_block(text)
                self.insertPlainText(formatted_text)
            else:
                self.insertPlainText(text)
            logging.info(f"Text inserted from mime data: {text}")

    def is_code_block(self, text):
        # Check if the text appears to be a code block
        return text.startswith("def ") or text.startswith("import ") or text.startswith("class ")

    def format_code_block(self, code_block):
        # Format the code block by adding indentation and line breaks
        lines = code_block.split("\n")
        formatted_lines = []
        for line in lines:
            formatted_lines.append("    " + line)
        formatted_code_block = "\n".join(formatted_lines)
        return formatted_code_block


class MessageProcessor(QThread):
    new_message = pyqtSignal(str)
    api_busy = pyqtSignal()
    api_error = pyqtSignal(str)

    def __init__(self, client, conversation_history):
        super().__init__()
        self.client = client
        self.conversation_history = conversation_history
        logging.info("MessageProcessor initialized")

    def run(self):
        message_sent = False
        while not message_sent:
            retries = 3
            for i in range(retries):
                try:
                    message = self.client.messages.create(
                        model="claude-3-opus-20240229",
                        max_tokens=4096,
                        temperature=0,
                        messages=self.conversation_history
                    )

                    claude_response = message.content[0].text if message.content else None

                    if claude_response:
                        self.new_message.emit(claude_response)
                        self.conversation_history.append(
                            {"role": "assistant", "content": [{"type": "text", "text": claude_response}]})
                        message_sent = True
                        logging.info(f"New message received: {claude_response}")
                        logging.info(f"Conversation history updated: {self.conversation_history}")
                        break
                except anthropic.InternalServerError as e:
                    logging.error("Failed to get a response from Claude.", exc_info=True)
                    if i < retries - 1:
                        self.api_busy.emit()
                        logging.warning("API busy. Retrying in 60 seconds.")
                        time.sleep(60)
                    else:
                        logging.error("Max retries reached. Aborting.")
                        self.api_error.emit("Failed to get a response from Claude after multiple retries.")
                        return
                except anthropic.BadRequestError as e:
                    logging.error("Bad request error occurred.", exc_info=True)
                    if "roles must alternate between \"user\" and \"assistant\"" in str(e):
                        if i < retries - 1:
                            self.api_busy.emit()
                            logging.warning("Server is busy. Retrying in 60 seconds.")
                            time.sleep(60)
                        else:
                            logging.error("Max retries reached. Aborting.")
                            self.api_error.emit("Failed to get a response from Claude after multiple retries.")
                            return
                    else:
                        self.api_error.emit(str(e))
                        return
                except requests.exceptions.RequestException as e:
                    logging.error("Network error occurred.", exc_info=True)
                    self.api_error.emit("Cannot communicate with Anthropic API right now.")
                    return

            if message_sent:
                break

            logging.warning("Message not sent. Retrying in 60 seconds.")
            time.sleep(60)


class ClaudeChat(QWidget):
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            self.api_key = input("Enter your Anthropic API Key: ")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.conversation_history = []
        self.chat_history = []
        self.code_blocks = {}
        self.conversation_history_db = ConversationHistory("conversation_history.db")
        self.init_ui()
        self.update_sidebar()  # Add this line
        logging.info("ClaudeChat initialized")
        logging.info(f"API key: {self.api_key}")
        logging.info(f"Conversation history: {self.conversation_history}")
        logging.info(f"Chat history: {self.chat_history}")

    def init_ui(self):
        self.setWindowTitle("Chat with Claude")
        self.resize(800, 600)
        QFontDatabase.addApplicationFont("fonts/Cabin-Regular.ttf")
        QFontDatabase.addApplicationFont("fonts/Cabin-Bold.ttf")

        screen_resolution = QApplication.primaryScreen().geometry()
        font_size = int(screen_resolution.height() * 0.02)  # Adjust the multiplier as needed
        font = QFont("Cabin", font_size)

        self.chat_label = QLabel("Chat History:")

        self.chat_history_widget = QWidget()
        self.chat_history_layout = QVBoxLayout(self.chat_history_widget)
        self.chat_history_layout.setAlignment(Qt.AlignTop)
        self.chat_history_layout.setSpacing(10)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.chat_history_widget)

        self.input_label = QLabel("Type your question here (press Ctrl+Enter to send):")

        self.user_input = MultiLineInput()
        self.user_input.setFont(font)
        self.user_input.setStyleSheet("""
            QTextEdit {
                border: 2px solid #c0c0c0;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        self.user_input.returnPressed.connect(self.send_message)
        self.user_input_highlighter = PythonHighlighter(self.user_input.document())

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_chat)

        self.status_bar = QStatusBar()

        self.upload_button = QPushButton("Upload")
        self.upload_button.clicked.connect(self.upload_file)

        input_layout = QVBoxLayout()
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.user_input)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.clear_button)
        input_layout.addWidget(self.upload_button)
        input_layout.addWidget(self.status_bar)

        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(400)  # Adjust the width as needed
        sidebar_font = QFont("Cabin", font_size)  # Adjust the font size as needed
        self.sidebar.setFont(sidebar_font)
        self.sidebar.setStyleSheet("""
            QListWidget {
                background-color: #f0f0f0;
                border: none;
                padding: 10px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #c0c0c0;
            }
        """)
        self.sidebar.itemClicked.connect(self.load_conversation)
        main_layout = QHBoxLayout()
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(self.sidebar)
        main_layout.addLayout(sidebar_layout)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.scroll_area)
        right_layout.addLayout(input_layout)
        main_layout.addLayout(right_layout)

        add_button = QPushButton("+")
        add_button.clicked.connect(self.add_new_conversation)
        add_button.setStyleSheet("""
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
        sidebar_layout.addWidget(add_button)

        self.setLayout(main_layout)

        # Add a new conversation when the application starts
        self.add_new_conversation()
        self.user_input.setFocus()  # Set focus to the user input field

    def update_sidebar(self):
        self.sidebar.clear()
        conversations = self.conversation_history_db.load_conversations()
        logging.info(f"Updating sidebar with {len(conversations)} conversations")

        # Add existing conversations to the sidebar
        for conversation_id, title in conversations:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, conversation_id)
            item.setSizeHint(QSize(0, 50))  # Adjust the height as needed
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
            self.sidebar.addItem(item)
            self.sidebar.setItemWidget(item, item_widget)

        # Set the current conversation as active
        if self.conversation_id is not None:
            items = self.sidebar.findItems(self.conversation_id, Qt.MatchExactly)
            if items:
                self.sidebar.setCurrentItem(items[0])

        logging.info("Sidebar updated")

        def show_context_menu(pos):
            global_pos = self.sidebar.mapToGlobal(pos)
            menu = QMenu(self.sidebar)
            rename_action = menu.addAction("Rename")
            delete_action = menu.addAction("Delete")
            action = menu.exec_(global_pos)
            if action == rename_action:
                item = self.sidebar.itemAt(pos)
                conversation_id = item.data(Qt.UserRole)
                if conversation_id is not None:
                    new_title, ok = QInputDialog.getText(self, "Rename Conversation", "Enter a new title:")
                    if ok and new_title:
                        self.rename_conversation(conversation_id, new_title)
            elif action == delete_action:
                item = self.sidebar.itemAt(pos)
                conversation_id = item.data(Qt.UserRole)
                if conversation_id is not None:
                    reply = QMessageBox.question(self, "Delete Conversation",
                                                "Are you sure you want to delete this conversation?",
                                                QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        self.delete_conversation(conversation_id)

        self.sidebar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sidebar.customContextMenuRequested.connect(show_context_menu)

    def rename_conversation(self, conversation_id, new_title):
        self.conversation_history_db.rename_conversation(conversation_id, new_title)
        self.update_sidebar()

    def delete_conversation(self, conversation_id):
        self.conversation_history_db.delete_conversation(conversation_id)
        self.update_sidebar()

    def show_code_dialog(self, code_block):
        dialog = QDialog(self)
        dialog.setWindowTitle("Code Block")
        layout = QVBoxLayout(dialog)

        code_text_edit = QTextEdit()
        code_text_edit.setReadOnly(True)
        code_text_edit.setPlainText(code_block)
        code_text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                padding: 10px;
                font-family: monospace;
            }
        """)
        layout.addWidget(code_text_edit)

        copy_button = QPushButton("Copy Code")
        copy_button.clicked.connect(lambda: self.copy_code_to_clipboard(code_block))
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
        layout.addWidget(copy_button)

        dialog.exec_()

    def encode_image(self, image_path):
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            logging.info(f"Image encoded successfully: {image_path}")
            return encoded_string
        except FileNotFoundError:
            logging.error(f"Image file not found: {image_path}")
            return None
        except Exception as e:
            logging.error(f"Error encoding image: {image_path}")
            logging.exception(e)
            return None

    def load_conversation(self, item):
        conversation_id = item.data(Qt.UserRole)
        if conversation_id is None:
            self.clear_chat()
            self.conversation_history = []
            self.conversation_id = None  # Reset the conversation ID
            self.user_input.clear()  # Clear the user input field
            self.user_input.setFocus()
        else:
            history = self.conversation_history_db.load_conversation_history(conversation_id)
            if history:
                self.clear_chat()
                self.conversation_id = conversation_id  # Set the conversation ID
                conversation = json.loads(history)
                for message in conversation:
                    if message["role"] == "user":
                        user_message = message["content"][0]["text"]
                        user_message_widget = QLabel(f"User: {user_message}")
                        user_message_widget.setWordWrap(True)
                        user_message_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
                        user_message_widget.setStyleSheet("""
                            QLabel {
                                font-size: 16px;
                                margin-bottom: 10px;
                            }
                        """)
                        self.chat_history_layout.addWidget(user_message_widget)
                    elif message["role"] == "assistant":
                        assistant_message = message["content"][0]["text"]
                        if "```" in assistant_message:
                            lines = assistant_message.split("\n")
                            in_code_block = False
                            code_block_content = ""
                            for line in lines:
                                if line.startswith("```"):
                                    in_code_block = not in_code_block
                                    if not in_code_block:
                                        code_block_widget = QTextEdit()
                                        code_block_widget.setReadOnly(True)
                                        code_block_widget.setPlainText(code_block_content)
                                        code_block_widget.setStyleSheet("""
                                            QTextEdit {
                                                background-color: #f5f5f5;
                                                padding: 10px;
                                                font-family: monospace;
                                                font-size: 16px;
                                            }
                                        """)
                                        self.chat_history_layout.addWidget(code_block_widget)
                                        self.add_copy_button(code_block_content)
                                        code_block_content = ""
                                else:
                                    if in_code_block:
                                        code_block_content += line + "\n"
                                    else:
                                        assistant_message_widget = QLabel(line)
                                        assistant_message_widget.setWordWrap(True)
                                        assistant_message_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
                                        assistant_message_widget.setStyleSheet("""
                                            QLabel {
                                                font-size: 16px;
                                                margin-bottom: 10px;
                                            }
                                        """)
                                        self.chat_history_layout.addWidget(assistant_message_widget)
                        else:
                            assistant_message_widget = QLabel(f"Assistant: {assistant_message}")
                            assistant_message_widget.setWordWrap(True)
                            assistant_message_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
                            assistant_message_widget.setStyleSheet("""
                                QLabel {
                                    font-size: 16px;
                                    margin-bottom: 10px;
                                }
                            """)
                            self.chat_history_layout.addWidget(assistant_message_widget)
                self.conversation_history = conversation  # Update the conversation history
                self.user_input.clear()  # Clear the user input field
                self.user_input.setFocus()  # Set focus to the user input field
                logging.info(f"Conversation loaded: {conversation}")
            else:
                logging.warning(f"Conversation history not found for ID: {conversation_id}")
    
    def send_message(self):
        user_message = self.user_input.toPlainText().strip()
        if user_message:
            user_message_widget = QLabel(f"User: {user_message}")
            user_message_widget.setWordWrap(True)
            user_message_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
            user_message_widget.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    margin-bottom: 10px;
                }
            """)
            self.chat_history_layout.addWidget(user_message_widget)
            self.user_input.clear()

            self.conversation_history.append({"role": "user", "content": [{"type": "text", "text": user_message}]})

            self.user_input.setEnabled(False)
            self.send_button.setEnabled(False)

            logging.info(f"User message sent: {user_message}")
            logging.info(f"Conversation history updated: {self.conversation_history}")

            self.processor = MessageProcessor(self.client, self.conversation_history)
            self.processor.new_message.connect(self.update_chat)
            self.processor.api_busy.connect(self.api_busy)
            self.processor.api_error.connect(self.show_api_error)
            self.processor.finished.connect(self.enable_input)
            self.processor.finished.connect(self.set_focus_to_input)
            self.processor.finished.connect(self.save_conversation)

            logging.info("Message processor created and connected")
            logging.info(f"Message processor connected to: {self.processor.receivers(self.processor.new_message)}")
            logging.info(f"API busy signal connected to: {self.processor.receivers(self.processor.api_busy)}")
            logging.info(f"API error signal connected to: {self.processor.receivers(self.processor.api_error)}")
            logging.info(f"Finished signal connected to: {self.processor.receivers(self.processor.finished)}")

            self.processor.start()
            logging.info("Message processor started")
        else:
            logging.warning("Empty user message. Message not sent.")

    def save_conversation(self):
        if self.conversation_history:
            logging.info(f"Updating conversation with ID: {self.conversation_id}")
            title = self.generate_conversation_title(self.conversation_id)  # Generate a meaningful title based on the conversation history
            self.conversation_history_db.save_conversation_to_db(self.conversation_id, title, self.conversation_history)
            logging.info("Conversation history updated in the database")
            self.update_sidebar()  # Update the sidebar after saving/updating the conversation
        else:
            logging.warning("Conversation history is empty. Skipping save.")

    def generate_conversation_title(self, conversation_id):
        if len(self.conversation_history) < 2:
            logging.info("Conversation history is too short. Returning the existing title.")
            existing_title = self.conversation_history_db.get_conversation_title(conversation_id)  # Get the existing title from the database
            if existing_title is None:
                logging.info("No existing title found. Returning 'New Conversation' as the title.")
                return "New Conversation"  # Return a default title if no existing title is found
            else:
                return existing_title  # Return the existing title if found
        else:
            user_messages = [message["content"][0]["text"] for message in self.conversation_history if
                            message["role"] == "user"]
            assistant_messages = [message["content"][0]["text"] for message in self.conversation_history if
                                message["role"] == "assistant"]

            conversation_summary = "\n".join(user_messages[-2:] + assistant_messages[-2:])

            prompt = f"Please generate a concise and descriptive title for the following conversation (maximum 4 words):\n\n{conversation_summary}\n\nTitle:"

            try:
                response = self.client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=10,
                    temperature=0,
                    system="You are a helpful assistant that generates concise and descriptive four-word titles for conversations.",
                    messages=[{"role": "user", "content": prompt}]
                )

                if response.content:
                    title = response.content[0].text.strip()
                    title_words = title.split()
                    if len(title_words) > 4:
                        title = " ".join(title_words[:4])
                    logging.info(f"Generated conversation title: {title}")
                    return title
                else:
                    logging.info("No title generated by the API. Returning the existing title.")
                    existing_title = self.conversation_history_db.get_conversation_title(conversation_id)  # Get the existing title from the database
                    if existing_title is None:
                        logging.info("No existing title found. Returning 'New Conversation' as the title.")
                        return "New Conversation"  # Return a default title if no existing title is found
                    else:
                        return existing_title  # Return the existing title if found

            except Exception as e:
                logging.error(f"Error generating conversation title: {str(e)}")
                existing_title = self.conversation_history_db.get_conversation_title(conversation_id)  # Get the existing title in case of an error
                if existing_title is None:
                    logging.info("No existing title found. Returning 'New Conversation' as the title.")
                    return "New Conversation"  # Return a default title if no existing title is found
                else:
                    return existing_title  # Return the existing title if found
       
    def set_focus_to_input(self):
        self.user_input.setFocus()
        logging.info("Focus set to user input")

    def update_chat(self, message):
        if "\n" in message:
            lines = message.split("\n")
            in_code_block = False
            code_block_content = ""
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
                                font-size: 16px;  /* Increase the font size */
                            }
                        """)
                        self.chat_history_layout.addWidget(code_block_widget)
                        self.add_copy_button(code_block_content)
                        logging.info(f"Code block detected: {code_block_content}")
                else:
                    if in_code_block or self.is_code_block(line):
                        code_block_content += line + "\n"
                    else:
                        message_widget = QLabel(line)
                        message_widget.setWordWrap(True)
                        message_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
                        message_widget.setStyleSheet("""
                            QLabel {
                                font-size: 16px;  /* Increase the font size */
                                margin-bottom: 10px;
                            }
                        """)
                        self.chat_history_layout.addWidget(message_widget)
        else:
            if self.is_code_block(message):
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
                self.chat_history_layout.addWidget(code_block_widget)
                self.add_copy_button(code_block_content)
                logging.info(f"Code block detected: {code_block_content}")
            else:
                message_widget = QLabel(f"Claude: {message}")
                message_widget.setWordWrap(True)
                message_widget.setTextInteractionFlags(Qt.TextSelectableByMouse)
                message_widget.setStyleSheet("""
                    QLabel {
                        font-size: 18px;  /* Increase the font size */
                        margin-bottom: 10px;
                    }
                """)
                self.chat_history_layout.addWidget(message_widget)

        # Scroll to the bottom of the chat history
        self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())

        self.user_input.setFocus()  # Set focus back to the user input box

        logging.info(f"Chat updated with message: {message}")

    def add_new_conversation(self):
        self.clear_chat()
        self.conversation_history = []
        self.user_input.setFocus()
        self.conversation_id = str(uuid.uuid4())
        title = "New Conversation"
        logging.info(f"Adding new conversation with ID: {self.conversation_id} and title: {title}")
        self.conversation_history_db.save_conversation_to_db(self.conversation_id, title, self.conversation_history)
        logging.info(f"New conversation added to the database with ID: {self.conversation_id}")
        self.update_sidebar()

    def is_code_block(self, text):
        # Check if the text appears to be a code block without the ```python prefix
        is_code = text.startswith("def ") or text.startswith("import ") or text.startswith("class ")
        logging.info(f"Checking if text is a code block: {text}")
        logging.info(f"Is code block: {is_code}")
        return is_code

    def add_copy_button(self, code_block_content):
        # Generate a unique identifier for the code block
        code_block_id = f"code_block_{len(self.code_blocks)}"
        self.code_blocks[code_block_id] = code_block_content.strip()

        # Create a copy button
        copy_button = QPushButton("Copy Code")
        copy_button.setFixedWidth(100)  # Set a fixed width for the button
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
        copy_button.clicked.connect(lambda: self.copy_code_to_clipboard(code_block_id))

        button_layout = QHBoxLayout()
        button_layout.addWidget(copy_button)
        button_layout.setAlignment(Qt.AlignLeft)  # Align the button to the left

        button_widget = QWidget()
        button_widget.setLayout(button_layout)

        self.chat_history_layout.addWidget(button_widget)
        self.chat_history_layout.addSpacing(10)  # Add spacing between the button and the next message

    def copy_code_to_clipboard(self, code_block_id):
        if code_block_id in self.code_blocks:
            code_block = self.code_blocks[code_block_id]
            QApplication.clipboard().setText(code_block)
            self.status_bar.showMessage("Code block copied to clipboard", 2000)

    def update_chat_history(self, message):
        self.chat_history.append(message)
        self.progress_dialog.close()

        logging.info(f"Chat history updated with message: {message}")
        logging.info(f"Progress dialog closed")
        logging.info(f"Current chat history: {self.chat_history}")

    def enable_input(self):
        self.user_input.setEnabled(True)
        self.send_button.setEnabled(True)

        logging.info("User input enabled")
        logging.info(f"User input widget enabled: {self.user_input.isEnabled()}")
        logging.info(f"Send button enabled: {self.send_button.isEnabled()}")

    def clear_chat(self):
        while self.chat_history_layout.count():
            item = self.chat_history_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.conversation_history = [
            {
                "role": "assistant",
                "content": "You are a professional Python developer with 20 years of experience."
            }
        ]

        logging.info("Chat cleared")
        logging.info(f"Conversation history reset: {self.conversation_history}")

    def api_busy(self):
        self.status_bar.showMessage("API is busy. Trying again in 60 seconds...", 60000)

        logging.warning("API busy")
        logging.info("Status bar message set: 'API is busy. Trying again in 60 seconds...'")
        logging.info("Status bar message timeout: 60000 ms")

    def show_api_error(self, error_message):
        QMessageBox.critical(self, "API Error", error_message)

        logging.error(f"API error: {error_message}")
        logging.info("API error message box shown")

    def upload_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File')
        if file_name:
            logging.info(f"File selected: {file_name}")
            extension = os.path.splitext(file_name)[1].lower()
            file_content = None
            if extension in ['.txt', '.py', '.js', '.html', '.css']:
                with open(file_name, 'r') as file:
                    file_content = file.read()
                logging.info(f"File content read: {file_content}")
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
            elif extension in ['.doc', '.docx']:
                pythoncom.CoInitialize()  # Required for Win32 COM
                word = win32.gencache.EnsureDispatch('Word.Application')
                doc = word.Documents.Open(file_name.replace('/', '\\'))
                file_content = doc.Content.Text
                doc.Close()
                word.Quit()
                logging.info(f"Word file content extracted: {file_content}")
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

            if file_content is not None:
                if extension in ['.png', '.jpg', '.jpeg']:
                    self.conversation_history.append({"role": "user", "content": [file_content]})
                else:
                    prompt = f"I uploaded a file with the following content:\n{file_content}"
                    self.conversation_history.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
                logging.info(f"Conversation history updated with file content: {self.conversation_history}")

                self.processor = MessageProcessor(self.client, self.conversation_history)
                self.processor.new_message.connect(self.update_chat)
                self.processor.api_error.connect(self.handle_api_error)
                self.processor.finished.connect(self.close_progress_dialog)  # Connect the finished signal
                self.processor.start()
                logging.info("Message processor started")

                self.progress_dialog = QProgressDialog("Analyzing file...", "Cancel", 0, 0, self)
                self.progress_dialog.setWindowModality(Qt.WindowModal)
                self.progress_dialog.show()
                logging.info("Progress dialog shown")
        else:
            logging.info("No file selected")

    def close_progress_dialog(self):
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
            logging.info("Progress dialog closed")

    def handle_api_error(self, error_message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("API Error")
        msg.setInformativeText(str(error_message))
        msg.setWindowTitle("Error")
        msg.exec_()

        logging.error(f"API error: {error_message}")
        logging.info("API error message box shown")


def main():
    app = QApplication(sys.argv)
    setup_logging()
    logging.info("Logging setup completed")
    logging.info("Application started")
    chat = ClaudeChat()
    chat.show()
    logging.info("ClaudeChat window shown")
    exit_code = app.exec_()
    logging.info(f"Application exited with code: {exit_code}")
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
