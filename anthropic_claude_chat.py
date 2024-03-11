import os
import sys
import anthropic
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QStatusBar, QMessageBox, QHBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QRegularExpression, QPoint
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QFontDatabase, QTextCursor, QTextBlockFormat, QTextDocument
from PyQt5.QtWidgets import QFileDialog, QProgressDialog
import time
import logging
import os
import fitz
from PIL import Image
import pythoncom
import win32com.client as win32
import base64
from io import BytesIO
import requests
import os
import sys
import logging

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
    info_handler = logging.FileHandler(info_log_file, mode='w')
    info_handler.setLevel(logging.INFO)
    info_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    info_handler.setFormatter(info_formatter)

    # Configure logging for warning logs
    warning_handler = logging.FileHandler(warning_log_file, mode='w')
    warning_handler.setLevel(logging.WARNING)
    warning_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    warning_handler.setFormatter(warning_formatter)

    # Configure logging for error logs
    error_handler = logging.FileHandler(error_log_file, mode='w')
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    error_handler.setFormatter(error_formatter)

    # Create a logger and add the handlers
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(info_handler)
    logger.addHandler(warning_handler)
    logger.addHandler(error_handler)




class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._highlight_rules = []

        # Keyword format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#1f3864"))  # Dark blue
        keyword_format.setFontWeight(QFont.Bold)
        keywords = ["False", "await", "else", "import", "pass", "None", "break", "except", "in", "raise", "True", "class", "finally", "is", "return", "and", "continue", "for", "lambda", "try", "as", "def", "from", "nonlocal", "while", "assert", "del", "global", "not", "with", "async", "elif", "if", "or", "yield", "print", "range", "open", "self"]
        self._highlight_rules.append((QRegularExpression(r"\b(" + "|".join(keywords) + r")\b"), keyword_format))

        # String format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#4caf50"))  # Green
        self._highlight_rules.append((QRegularExpression(r"\".*\""), string_format))
        self._highlight_rules.append((QRegularExpression(r"\'.*\'"), string_format))

        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#9e9e9e"))  # Gray
        self._highlight_rules.append((QRegularExpression(r"#[^\n]*"), comment_format))

        # Function format
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#ff9800"))  # Orange
        self._highlight_rules.append((QRegularExpression(r"\b[A-Za-z0-9_]+(?=\()"), function_format))

        logging.info("PythonHighlighter initialized")

    def highlightBlock(self, text):
        if self.currentBlock().userState() == 1:  # Inside a code block
            for pattern, format in self._highlight_rules:
                match_iterator = pattern.globalMatch(text)
                while match_iterator.hasNext():
                    match = match_iterator.next()
                    self.setFormat(match.capturedStart(), match.capturedLength(), format)
            logging.info(f"Highlighted code block: {text}")
        else:  # Outside a code block
            self.setFormat(0, len(text), QTextCharFormat())  # Clear formatting
            logging.info(f"Cleared formatting for non-code block: {text}")


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
        self.insertPlainText(source.text())
        logging.info(f"Text inserted from mime data: {source.text()}")


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
                        self.conversation_history.append({"role": "assistant", "content": claude_response})
                        message_sent = True
                        logging.info(f"New message received: {claude_response}")
                        break
                except anthropic.InternalServerError as e:
                    logging.error("Failed to get a response from Claude.", exc_info=True)
                    if i < retries - 1:
                        self.api_busy.emit()
                        logging.warning("API busy. Retrying in 60 seconds.")
                        time.sleep(60)
                    else:
                        logging.error("Max retries reached. Aborting.")
                        return
                except anthropic.BadRequestError as e:
                    logging.error("Bad request error occurred.", exc_info=True)
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
        self.init_ui()
        logging.info("ClaudeChat initialized")
        logging.info(f"API key: {self.api_key}")
        logging.info(f"Conversation history: {self.conversation_history}")
        logging.info(f"Chat history: {self.chat_history}")

    def init_ui(self):
        self.setWindowTitle("Chat with Claude")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.resize(800, 600)
        QFontDatabase.addApplicationFont("fonts/Cabin-Regular.ttf")
        QFontDatabase.addApplicationFont("fonts/Cabin-Bold.ttf")
        font = QFont("Cabin", 14)

        self.chat_label = QLabel("Chat History:")
        self.layout.addWidget(self.chat_label)

        self.chat_history = QTextEdit()
        self.chat_history.setFont(font)
        self.chat_history.setReadOnly(True)
        self.chat_history_layout = QVBoxLayout()
        self.chat_history_layout.addWidget(self.chat_history)
        self.layout.addLayout(self.chat_history_layout)

        self.chat_history_highlighter = PythonHighlighter(self.chat_history.document())  # Add this line

        self.copy_button_layout = QHBoxLayout()
        self.copy_button_layout.setAlignment(Qt.AlignRight)
        self.chat_history_layout.addLayout(self.copy_button_layout)

        self.input_label = QLabel("Type your question here (press Ctrl+Enter to send):")
        self.layout.addWidget(self.input_label)

        self.user_input = MultiLineInput()
        self.user_input.setFont(font)
        self.user_input.returnPressed.connect(self.send_message)
        self.layout.addWidget(self.user_input)
        self.user_input_highlighter = PythonHighlighter(self.user_input.document())

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.layout.addWidget(self.send_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_chat)
        self.layout.addWidget(self.clear_button)

        self.status_bar = QStatusBar()
        self.layout.addWidget(self.status_bar)

        self.upload_button = QPushButton("Upload")
        self.upload_button.clicked.connect(self.upload_file)
        self.layout.addWidget(self.upload_button)

        logging.info("UI initialized")
        logging.info(f"Window title: {self.windowTitle()}")
        logging.info(f"Window size: {self.size()}")
        logging.info(f"Font: {font.family()} {font.pointSize()}")
        logging.info(f"Chat history highlighter: {type(self.chat_history_highlighter).__name__}")
        logging.info(f"User input highlighter: {type(self.user_input_highlighter).__name__}")
        logging.info(f"Send button connected to: {self.send_button.receivers(self.send_button.clicked)}")
        logging.info(f"Clear button connected to: {self.clear_button.receivers(self.clear_button.clicked)}")
        logging.info(f"Upload button connected to: {self.upload_button.receivers(self.upload_button.clicked)}")


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

    def send_message(self):
        user_message = self.user_input.toPlainText().strip()
        if user_message:
            self.chat_history.setTextColor(QColor("#212121"))  # Dark gray
            self.chat_history.setFontFamily("Cabin")
            self.chat_history.append(f"User: {user_message}")
            self.user_input.clear()

            self.conversation_history.append({"role": "user", "content": user_message})

            self.user_input.setEnabled(False)
            self.send_button.setEnabled(False)

            logging.info(f"User message sent: {user_message}")
            logging.info(f"Conversation history updated: {self.conversation_history}")

            self.processor = MessageProcessor(self.client, self.conversation_history)
            self.processor.new_message.connect(self.update_chat)
            self.processor.api_busy.connect(self.api_busy)
            self.processor.api_error.connect(self.show_api_error)
            self.processor.finished.connect(self.enable_input)
            self.processor.finished.connect(self.set_focus_to_input)  # Connect the finished signal to set_focus_to_input

            logging.info("Message processor created and connected")
            logging.info(f"Message processor connected to: {self.processor.receivers(self.processor.new_message)}")
            logging.info(f"API busy signal connected to: {self.processor.receivers(self.processor.api_busy)}")
            logging.info(f"API error signal connected to: {self.processor.receivers(self.processor.api_error)}")
            logging.info(f"Finished signal connected to: {self.processor.receivers(self.processor.finished)}")

            self.processor.start()
            logging.info("Message processor started")
        else:
            logging.warning("Empty user message. Message not sent.")


    def set_focus_to_input(self):
        self.user_input.setFocus()
        logging.info("Focus set to user input")

    def update_chat(self, message):
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.End)

        # Add space between user question and bot answer
        space_format = QTextCharFormat()
        space_format.setFontPointSize(6)
        cursor.insertText("\n\n", space_format)

        # Set background color for bot answer
        bot_format = QTextCharFormat()
        bot_format.setBackground(QColor("#f5f5f5"))  # Light gray background

        # Check if the message contains a code block
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
                        self.add_copy_button(code_block_content)
                        logging.info(f"Code block detected: {code_block_content}")
                    cursor.insertBlock()
                    block_format = QTextBlockFormat()
                    block_format.setBackground(QColor("#f5f5f5"))  # Light gray background
                    cursor.setBlockFormat(block_format)
                else:
                    if in_code_block or self.is_code_block(line):
                        code_block_content += line + "\n"
                        cursor.insertText(line)
                        cursor.block().setUserState(1)  # Set block state to indicate code block
                    else:
                        cursor.insertText(line, bot_format)
                    cursor.insertBlock()
        else:
            if self.is_code_block(message):
                code_block_content = message
                cursor.insertText(message)
                cursor.block().setUserState(1)  # Set block state to indicate code block
                self.add_copy_button(code_block_content)
                logging.info(f"Code block detected: {code_block_content}")
            else:
                cursor.insertText(f"Claude: {message}\n", bot_format)

        self.chat_history_highlighter.rehighlight()
        self.chat_history.moveCursor(QTextCursor.End)
        self.user_input.setFocus()  # Set focus back to the user input box

        logging.info(f"Chat updated with message: {message}")

    def is_code_block(self, text):
            # Check if the text appears to be a code block without the ```python prefix
            is_code = text.startswith("def ") or text.startswith("import ") or text.startswith("class ")
            logging.info(f"Checking if text is a code block: {text}")
            logging.info(f"Is code block: {is_code}")
            return is_code

    def add_copy_button(self, code_block):
        copy_button = QPushButton("Copy Code")
        copy_button.clicked.connect(lambda: QApplication.clipboard().setText(code_block))
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

        self.copy_button_layout.addWidget(copy_button)

        logging.info(f"Copy button added for code block: {code_block}")
        logging.info(f"Copy button connected to: {copy_button.receivers(copy_button.clicked)}")



    def copy_code(self, cursor):
        cursor.movePosition(QTextCursor.StartOfBlock)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        code_block = cursor.selectedText()
        QApplication.clipboard().setText(code_block)

        logging.info(f"Code block copied to clipboard: {code_block}")
        logging.info(f"Cursor position: {cursor.position()}")
        logging.info(f"Cursor selection start: {cursor.selectionStart()}")
        logging.info(f"Cursor selection end: {cursor.selectionEnd()}")



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
        self.chat_history.clear()
        self.conversation_history = [
            {
                "role": "assistant",
                "content": "You are a professional Python developer with 20 years of experience."
            }
        ]

        logging.info("Chat cleared")
        logging.info(f"Chat history cleared: {self.chat_history.toPlainText()}")
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
                        file_content += " ".join([str(cell.Value) if cell.Value is not None else '' for cell in row.Cells]) + "\n"
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
                    prompt = f"You uploaded a file with the following content:\n{file_content}"
                    self.conversation_history.append({"role": "user", "content": [{"type": "text", "text": prompt}]})
                logging.info(f"Conversation history updated with file content: {self.conversation_history}")

                self.message_processor = MessageProcessor(self.client, self.conversation_history)
                self.message_processor.new_message.connect(self.update_chat_history)
                self.message_processor.api_error.connect(self.handle_api_error)
                self.message_processor.start()
                logging.info("Message processor started")

                self.progress_dialog = QProgressDialog("Analyzing file...", "Cancel", 0, 0, self)
                self.progress_dialog.setWindowModality(Qt.WindowModal)
                self.progress_dialog.show()
                logging.info("Progress dialog shown")
        else:
            logging.info("No file selected")

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
    logging.info("Application started")

    chat = ClaudeChat()
    chat.show()
    logging.info("ClaudeChat window shown")

    setup_logging()
    logging.info("Logging setup completed")

    exit_code = app.exec_()
    logging.info(f"Application exited with code: {exit_code}")
    sys.exit(exit_code)

if __name__ == '__main__':
    main()