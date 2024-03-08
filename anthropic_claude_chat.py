import os
import sys
import anthropic
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QStatusBar, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QKeyEvent, QFont
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

class MultiLineInput(QTextEdit):
    returnPressed = pyqtSignal(str)
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
            self.returnPressed.emit(self.toPlainText())
            self.clear()
            
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
                    # Create a message with the Claude model
                    message = self.client.messages.create(
                        model="claude-3-opus-20240229",
                        max_tokens=4096,
                        temperature=0,
                        messages=self.conversation_history
                    )

                    # Extract the text from the message content
                    claude_response = message.content[0].text if message.content else None

                    # Emit the new message
                    if claude_response:
                        self.new_message.emit(claude_response)

                        # Append the assistant's response to the conversation history
                        self.conversation_history.append({"role": "assistant", "content": claude_response})

                        # Set the flag to indicate that the message has been sent
                        message_sent = True
                        break
                except anthropic.InternalServerError as e:
                    # Log the error and retry if it's not the last attempt
                    logging.error("Failed to get a response from Claude.", exc_info=True)
                    if i < retries - 1:
                        self.api_busy.emit()
                        time.sleep(60)
                    else:
                        return
                except anthropic.BadRequestError as e:
                    # Log the error and exit the method
                    logging.error("Bad request error occurred.", exc_info=True)
                    self.api_error.emit(str(e))
                    return

            # Break the while loop if the message has been sent
            if message_sent:
                break

            # Wait for 60 seconds before trying to send the message again
            time.sleep(60)

# Create a new class for the chat window
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
        self.resize(800, 400)

        font = QFont()
        font.setPointSize(14)  # Set the font size to 14 points

        self.chat_label = QLabel("Chat History:")
        self.layout.addWidget(self.chat_label)

        self.chat_history = QTextEdit()
        self.chat_history.setFont(font)  # Set the font for chat_history
        self.chat_history.setReadOnly(True)
        self.layout.addWidget(self.chat_history)

        self.input_label = QLabel("Type your question here:")
        self.layout.addWidget(self.input_label)

        self.user_input = MultiLineInput()
        self.user_input.setFont(font)  # Set the font for user_input
        self.user_input.returnPressed.connect(self.send_message)
        self.layout.addWidget(self.user_input)

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
    
    def encode_image(self,image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string

    def send_message(self):
        user_message = self.user_input.toPlainText().strip()
        user_message = user_message.replace('\n', ' ')  # Replace newlines with spaces
        if user_message:
            self.chat_history.append("User: " + user_message + "\n")
            self.user_input.clear()

            self.conversation_history.append({"role": "user", "content": user_message})

            self.processor = MessageProcessor(self.client, self.conversation_history)
            self.processor.new_message.connect(self.update_chat)
            self.processor.api_busy.connect(self.api_busy)
            self.processor.api_error.connect(self.show_api_error)
            self.processor.start()

    def update_chat(self, message):
        self.chat_history.append("Claude: " + message + "\n\n\n")

    def update_chat_history(self, message):
        self.chat_history.append(message)
        self.progress_dialog.close()
   
        
    def clear_chat(self):
        self.chat_history.clear()
        self.conversation_history = [
            {
                "role": "assistant",
                "content": "You are professional python developer with 20 years experience"
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
                    # Assuming you want to read the first worksheet in the workbook
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

                # Show a progress dialog
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