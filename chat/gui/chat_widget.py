from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt5.QtCore import Qt

class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.conversation_history = []

    def init_ui(self):
        layout = QVBoxLayout()
        self.chat_area = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_area)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.chat_area)

        layout.addWidget(scroll)
        self.setLayout(layout)

    def add_message(self, sender, message):
        label = QLabel(f"{sender}: {message}")
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.chat_layout.addWidget(label)
        self.conversation_history.append({"role": sender.lower(), "content": message})

    def clear_chat(self):
        for i in reversed(range(self.chat_layout.count())): 
            self.chat_layout.itemAt(i).widget().setParent(None)
        self.conversation_history.clear()

    def get_conversation_history(self):
        return self.conversation_history