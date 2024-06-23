import sys
import logging
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QListWidget, QComboBox, QStatusBar, QDialog
from PyQt5.QtCore import Qt

from .chat_widget import ChatWidget
from .sidebar import Sidebar
from .input_widget import InputWidget
from .api_key_dialog import APIKeyDialog
from utils.api_key_manager import get_api_key, set_api_key
from api.anthropic_client import AnthropicClient
from database.conversation_manager import ConversationManager

class ClaudeChat(QWidget):
    def __init__(self):
        super().__init__()
        self.api_key = get_api_key()
        if not self.api_key:
            self.get_api_key_from_user()
        
        self.client = AnthropicClient(self.api_key)
        self.conversation_manager = ConversationManager("conversation_history.db")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Chat with Claude")
        self.showMaximized()

        main_layout = QHBoxLayout()

        self.sidebar = Sidebar(self.conversation_manager)
        main_layout.addWidget(self.sidebar)

        chat_layout = QVBoxLayout()
        self.chat_widget = ChatWidget()
        chat_layout.addWidget(self.chat_widget)

        self.input_widget = InputWidget()
        chat_layout.addWidget(self.input_widget)

        button_layout = QHBoxLayout()
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        button_layout.addWidget(self.send_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_chat)
        button_layout.addWidget(self.clear_button)

        self.upload_button = QPushButton("Upload")
        self.upload_button.clicked.connect(self.upload_file)
        button_layout.addWidget(self.upload_button)

        chat_layout.addLayout(button_layout)

        self.status_bar = QStatusBar()
        chat_layout.addWidget(self.status_bar)

        main_layout.addLayout(chat_layout)

        self.model_selector = QComboBox()
        self.model_selector.addItems(["claude-3-5-sonnet", "Claude-3-Haiku", "Claude-3-Opus", "Claude-3-Sonnet"])
        main_layout.addWidget(self.model_selector)

        self.setLayout(main_layout)

    def get_api_key_from_user(self):
        dialog = APIKeyDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.api_key = dialog.get_api_key()
            set_api_key(self.api_key)
        else:
            logging.error("No API key provided. Exiting.")
            sys.exit(1)

    def send_message(self):
        user_message = self.input_widget.get_input()
        if user_message:
            self.chat_widget.add_message("User", user_message)
            self.input_widget.clear_input()

            selected_model = self.model_selector.currentText()
            response = self.client.get_response(user_message, selected_model)
            self.chat_widget.add_message("Claude", response)

            self.conversation_manager.save_conversation(self.chat_widget.get_conversation_history())

    def clear_chat(self):
        self.chat_widget.clear_chat()
        self.conversation_manager.create_new_conversation()

    def upload_file(self):
        # Implement file upload functionality here
        pass