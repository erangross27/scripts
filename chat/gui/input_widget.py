from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import Qt

class InputWidget(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setAcceptRichText(False)
        self.setFixedHeight(100)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() & Qt.ControlModifier:
            self.parent().send_message()
        else:
            super().keyPressEvent(event)

    def get_input(self):
        return self.toPlainText().strip()

    def clear_input(self):
        self.clear()