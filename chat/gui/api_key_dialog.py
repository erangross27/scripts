from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

class APIKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enter API Key")
        self.layout = QVBoxLayout()
        
        self.label = QLabel("Please enter your Anthropic API Key:")
        self.layout.addWidget(self.label)
        
        self.api_key_input = QLineEdit()
        self.layout.addWidget(self.api_key_input)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)
        
        self.setLayout(self.layout)

    def get_api_key(self):
        return self.api_key_input.text()