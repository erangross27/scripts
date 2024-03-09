import os
import sys
import anthropic
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QStatusBar, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QRegularExpression
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCharFormat, QColor, QFontDatabase, QTextCursor, QTextBlockFormat
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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

    def highlightBlock(self, text):
        if self.currentBlock().userState() == 1:  # Inside a code block
            for pattern, format in self._highlight_rules:
                match_iterator = pattern.globalMatch(text)
                while match_iterator.hasNext():
                    match = match_iterator.next()
                    self.setFormat(match.capturedStart(), match.capturedLength(), format)
        else:  # Outside a code block
            self.setFormat(0, len(text), QTextCharFormat())  # Clear formatting

class MultiLineInput(QTextEdit):
    returnPressed = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() & Qt.ControlModifier:
            self.returnPressed.emit()
        else:
            super().keyPressEvent(event)

    def insertFromMimeData(self, source):
        self.insertPlainText(source.text())

class MessageProcessor(QThread):
    new_message = pyqtSignal(str)
    api_busy = pyqtSignal()
    api_error = pyqtSignal(str)

    def __init__(self, client, conversation_history):
        super().__init__()
        self.client = client
        self.conversation_history = conversation_history

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
                        break
                except anthropic.InternalServerError as e:
                    logging.error("Failed to get a response from Claude.", exc_info=True)
                    if i < retries - 1:
                        self.api_busy.emit()
                        time.sleep(60)
                    else:
                        return
                except anthropic.BadRequestError as e:
                    logging.error("Bad request error occurred.", exc_info=True)
                    self.api_error.emit(str(e))
                    return

            if message_sent:
                break

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
        self.layout.addWidget(self.chat_history)
        self.chat_history_highlighter = PythonHighlighter(self.chat_history.document())

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

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string

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

            self.processor = MessageProcessor(self.client, self.conversation_history)
            self.processor.new_message.connect(self.update_chat)
            self.processor.api_busy.connect(self.api_busy)
            self.processor.api_error.connect(self.show_api_error)
            self.processor.finished.connect(self.enable_input)
            self.processor.finished.connect(self.set_focus_to_input)  # Connect the finished signal to set_focus_to_input
            self.processor.start()

    def set_focus_to_input(self):
        self.user_input.setFocus()

    def update_chat(self, message):
        cursor = self.chat_history.textCursor()
        cursor.movePosition(QTextCursor.End)

        # Add space between user question and bot answer
        space_format = QTextCharFormat()
        space_format.setFontPointSize(6)
        cursor.insertText("\n", space_format)

        # Set background color for bot answer
        bot_format = QTextCharFormat()
        bot_format.setBackground(QColor("#f5f5f5"))  # Light gray background

        # Check if the message contains a code block
        if "\n" in message:
            lines = message.split("\n")
            in_code_block = False
            for line in lines:
                if line.startswith("```"):
                    in_code_block = not in_code_block
                    cursor.insertBlock()
                    block_format = QTextBlockFormat()
                    block_format.setBackground(QColor("#f5f5f5"))  # Light gray background
                    cursor.setBlockFormat(block_format)
                else:
                    if in_code_block:
                        cursor.insertText(line)
                        cursor.block().setUserState(1)  # Set block state to indicate code block
                    else:
                        cursor.insertText(line, bot_format)
                    cursor.insertBlock()
        else:
            cursor.insertText(f"Claude: {message}", bot_format)

        self.chat_history_highlighter.rehighlight()
        self.chat_history.moveCursor(QTextCursor.End)
         # Set focus back to the user input box
        self.user_input.setFocus()

    def update_chat_history(self, message):
        self.chat_history.append(message)
        self.progress_dialog.close()

    def enable_input(self):
        self.user_input.setEnabled(True)
        self.send_button.setEnabled(True)

    def clear_chat(self):
        self.chat_history.clear()
        self.conversation_history = [
            {
                "role": "assistant",
                "content": "You are a professional Python developer with 20 years of experience."
            }
        ]

    def api_busy(self):
        self.status_bar.showMessage("API is busy. Trying again in 60 seconds...", 60000)

    def show_api_error(self, error_message):
        QMessageBox.critical(self, "API Error", error_message)

    def upload_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File')
        if file_name:
            extension = os.path.splitext(file_name)[1].lower()
            file_content = None
            if extension in ['.txt', '.py', '.js', '.html', '.css']:
                with open(file_name, 'r') as file:
                    file_content = file.read()
            elif extension == '.pdf':
                try:
                    doc = fitz.open(file_name)
                    file_content = "".join(page.get_text() for page in doc)
                except fitz.FileDataError:
                    file_content = "Error: The PDF file is invalid or corrupted."
                except fitz.PasswordError:
                    file_content = "Error: The PDF file is password-protected."
                except Exception as e:
                    file_content = f"Error: An unexpected error occurred while processing the PDF file: {str(e)}"
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
            elif extension in ['.doc', '.docx']:
                pythoncom.CoInitialize()  # Required for Win32 COM
                word = win32.gencache.EnsureDispatch('Word.Application')
                doc = word.Documents.Open(file_name.replace('/', '\\'))
                file_content = doc.Content.Text
                doc.Close()
                word.Quit()
            elif extension in ['.xls', '.xlsx']:
                pythoncom.CoInitialize()  # Required for Win32 COM
                excel = win32.gencache.EnsureDispatch('Excel.Application')
                try:
                    workbook = excel.Workbooks.Open(file_name.replace('/', '\\'))
                    sheet = workbook.Worksheets[1]
                    file_content = ""
                    for row in sheet.UsedRange.Rows:
                        file_content += " ".join([str(cell.Value) if cell.Value is not None else '' for cell in row.Cells]) + "\n"
                except Exception as e:
                    file_content = f"Error opening file: {e}"
                finally:
                    workbook.Close()
                    excel.Quit()

            if file_content is not None:
                if extension in ['.png', '.jpg', '.jpeg']:
                    self.conversation_history.append({"role": "user", "content": [file_content]})
                else:
                    prompt = f"You uploaded a file with the following content:\n{file_content}"
                    self.conversation_history.append({"role": "user", "content": [{"type": "text", "text": prompt}]})

                self.message_processor = MessageProcessor(self.client, self.conversation_history)
                self.message_processor.new_message.connect(self.update_chat_history)
                self.message_processor.api_error.connect(self.handle_api_error)
                self.message_processor.start()

                self.progress_dialog = QProgressDialog("Analyzing file...", "Cancel", 0, 0, self)
                self.progress_dialog.setWindowModality(Qt.WindowModal)
                self.progress_dialog.show()

    def handle_api_error(self, error_message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("API Error")
        msg.setInformativeText(str(error_message))
        msg.setWindowTitle("Error")
        msg.exec_()

app = QApplication(sys.argv)
chat = ClaudeChat()
chat.show()
sys.exit(app.exec_())