import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLineEdit, QPushButton, QMessageBox
)

def parse_time(time_str):
    """
    Convert a string 'hours:minutes' or 'hours' into total minutes as a float.
    """
    time_str = time_str.strip()
    try:
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) != 2:
                raise ValueError("Invalid time format.")
            h_str, m_str = parts
            h = int(h_str) if h_str else 0
            m = int(m_str) if m_str else 0
            total_minutes = h * 60 + m
        else:
            total_minutes = int(time_str) * 60
    except ValueError:
        raise ValueError("Please enter a valid time (e.g., 12, 12:30, or 0:45).")
    return float(total_minutes)

def format_hours(total_minutes):
    """
    Converts total minutes into 'hours:minutes' string.
    """
    total_minutes = round(total_minutes)
    sign = '-' if total_minutes < 0 else ''
    total_minutes = abs(total_minutes)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{sign}{hours}:{minutes:02d}"

class TimeCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("מחשבון שעות (עשרוני)")
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setStyleSheet("font-size: 18px; height: 40px;")
        
        # Calculator state: store minutes as a float
        self.current_value = 0.0
        self.current_operator = None
        self.waiting_for_new_value = True

        grid = QGridLayout()
        grid.addWidget(self.display, 0, 0, 1, 4)
        
        # Button definitions: text -> (row, col) or (row, col, rowspan, colspan)
        buttons = {
            '7': (1, 0), '8': (1, 1), '9': (1, 2),
            '4': (2, 0), '5': (2, 1), '6': (2, 2),
            '1': (3, 0), '2': (3, 1), '3': (3, 2),
            '0': (4, 0),
            ':': (4, 1),
            'נקה': (4, 2),
            '+': (1, 3), '-': (2, 3), '*': (3, 3), '/': (4, 3),
            'שווה': (5, 0, 1, 4)
        }
        
        for btn_text, pos in buttons.items():
            button = QPushButton(btn_text)
            button.setStyleSheet("font-size: 16px; height: 40px;")
            button.clicked.connect(self.on_button_clicked)
            if len(pos) == 2:
                grid.addWidget(button, pos[0], pos[1])
            else:
                row, col, rowspan, colspan = pos
                grid.addWidget(button, row, col, rowspan, colspan)
                
        self.setLayout(grid)

    def on_button_clicked(self):
        sender = self.sender()
        text = sender.text()
        
        # If digit or colon, append to the current input
        if text.isdigit() or text == ':':
            if self.waiting_for_new_value:
                self.display.clear()
                self.waiting_for_new_value = False
            self.display.setText(self.display.text() + text)
            return

        # Clear button resets the calculation
        if text == 'נקה':
            self.current_value = 0.0
            self.current_operator = None
            self.display.clear()
            self.waiting_for_new_value = True
            return

        # If an operator button is pressed (+, -, *, /)
        if text in ['+', '-', '*', '/']:
            self.process_operator(text)
            return

        # The equals button: perform the pending calculation
        if text == 'שווה':
            self.process_equals()
            return

    def process_operator(self, new_operator):
        new_value_str = self.display.text().strip()
        # If there is a valid input, parse it to minutes.
        if new_value_str:
            try:
                new_val_minutes = parse_time(new_value_str)
            except ValueError as e:
                self.show_error(str(e))
                return

            # If an operator is already pending and user has entered a new operand,
            # perform the pending operation.
            if not self.waiting_for_new_value and self.current_operator is not None:
                self.calculate(new_val_minutes)
            else:
                self.current_value = new_val_minutes
        self.current_operator = new_operator
        self.waiting_for_new_value = True
        
    def process_equals(self):
        new_value_str = self.display.text().strip()
        if new_value_str:
            try:
                new_val_minutes = parse_time(new_value_str)
            except ValueError as e:
                self.show_error(str(e))
                return
            if self.current_operator is not None:
                self.calculate(new_val_minutes)
                self.current_operator = None

    def calculate(self, new_val_minutes):
        if self.current_operator == '+':
            self.current_value += new_val_minutes
        elif self.current_operator == '-':
            self.current_value -= new_val_minutes
        elif self.current_operator == '*':
            # For multiplication, treat the second operand as a multiplier in hours.
            decimal_multiplier = new_val_minutes / 60.0
            self.current_value = round(self.current_value * decimal_multiplier)
        elif self.current_operator == '/':
            if new_val_minutes == 0:
                self.show_error("Division by zero is not allowed.")
                return
            self.current_value = round(self.current_value / (new_val_minutes / 60.0))
        
        self.display.setText(format_hours(self.current_value))
        self.waiting_for_new_value = True

    def show_error(self, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Warning)
        error_dialog.setText(message)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec_()

def main():
    app = QApplication(sys.argv)
    window = TimeCalculator()
    window.resize(300, 300)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
