import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt

class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator")
        self.setGeometry(100, 100, 300, 400)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setStyleSheet("font-size: 24px; padding: 10px;")
        main_layout.addWidget(self.display)

        buttons_layout = QGridLayout()
        main_layout.addLayout(buttons_layout)

        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]

        row = 0
        col = 0
        for button_text in buttons:
            button = QPushButton(button_text)
            button.setStyleSheet("font-size: 18px; padding: 10px;")
            button.clicked.connect(self.button_clicked)
            buttons_layout.addWidget(button, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

        self.equation = ""

    def button_clicked(self):
        button = self.sender()
        if button.text() == '=':
            result = eval(self.equation)
            self.display.setText(str(result))
            self.equation = ""
        else:
            self.equation += button.text()
            self.display.setText(self.equation)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calculator = Calculator()
    calculator.show()
    sys.exit(app.exec_())