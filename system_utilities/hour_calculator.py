import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLineEdit, QPushButton
)

def parse_time(time_str):
    """
    ממיר מחרוזת 'שעות:דקות' או 'שעות' למספר שלם של דקות.
    """
    time_str = time_str.strip()
    if ':' in time_str:
        h_str, m_str = time_str.split(':')
        h = int(h_str) if h_str else 0
        m = int(m_str) if m_str else 0
        total_minutes = h * 60 + m
    else:
        total_minutes = int(time_str) * 60
    return total_minutes

def format_hours(total_minutes):
    """
    ממיר מספר שלם של דקות לפורמט של 'שעות:דקות',
    למשל 4500 דקות -> 75:00
    """
    # מאפשר התמודדות עם ערכים שליליים (אם צריך)
    sign = -1 if total_minutes < 0 else 1
    total_minutes = abs(total_minutes)

    # חישוב שעות ודקות
    hours = total_minutes // 60
    minutes = total_minutes % 60

    # החזרה עם סימן אם הערך שלילי
    result = f"{sign * hours}:{minutes:02d}"
    return result

class TimeCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("מחשבון שעות (עשרוני)")

        # תצוגה
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setStyleSheet("font-size: 18px; height: 40px;")

        self.current_value = 0
        self.current_operator = None
        self.waiting_for_new_value = True

        # סידור גריד
        grid = QGridLayout()
        grid.addWidget(self.display, 0, 0, 1, 4)

        # הגדרת כפתורים
        buttons = {
            '7': (1,0), '8': (1,1), '9': (1,2), 
            '4': (2,0), '5': (2,1), '6': (2,2),
            '1': (3,0), '2': (3,1), '3': (3,2),
            '0': (4,0),
            ':': (4,1),
            'נקה': (4,2),
            '+': (1,3), '-': (2,3), '*': (3,3), '/': (4,3),
            'שווה': (5,0,1,4)
        }

        for btn_text, pos in buttons.items():
            if len(pos) == 2:
                button = QPushButton(btn_text)
                button.setStyleSheet("font-size: 16px; height: 40px;")
                button.clicked.connect(self.on_button_clicked)
                grid.addWidget(button, pos[0], pos[1])
            else:
                row, col, rowspan, colspan = pos
                button = QPushButton(btn_text)
                button.setStyleSheet("font-size: 16px; height: 40px;")
                button.clicked.connect(self.on_button_clicked)
                grid.addWidget(button, row, col, rowspan, colspan)

        self.setLayout(grid)

    def on_button_clicked(self):
        sender = self.sender()
        text = sender.text()

        if text.isdigit() or text == ':':
            if self.waiting_for_new_value:
                self.display.setText("")
                self.waiting_for_new_value = False
            self.display.setText(self.display.text() + text)

        elif text in ['+', '-', '*', '/']:
            new_value_str = self.display.text().strip()
            if new_value_str:
                new_val_minutes = parse_time(new_value_str)
                if self.current_operator is not None:
                    self.calculate(new_val_minutes)
                else:
                    self.current_value = new_val_minutes

            self.current_operator = text
            self.waiting_for_new_value = True

        elif text == 'שווה':
            new_value_str = self.display.text().strip()
            if new_value_str:
                new_val_minutes = parse_time(new_value_str)
                self.calculate(new_val_minutes)
                self.current_operator = None

        elif text == 'נקה':
            self.current_value = 0
            self.current_operator = None
            self.display.setText("")
            self.waiting_for_new_value = True

    def calculate(self, new_val_minutes):
        if self.current_operator == '+':
            self.current_value += new_val_minutes
        elif self.current_operator == '-':
            self.current_value -= new_val_minutes
        elif self.current_operator == '*':
            # For multiplication, we convert the second operand to decimal hours
            decimal_multiplier = new_val_minutes / 60
            self.current_value = int(self.current_value * decimal_multiplier)
        elif self.current_operator == '/':
            if new_val_minutes != 0:
                self.current_value //= new_val_minutes

        # הצגת התוצאה בפורמט שעות עשרוני
        self.display.setText(format_hours(self.current_value))
        self.waiting_for_new_value = True

def main():
    app = QApplication(sys.argv)
    window = TimeCalculator()
    window.resize(300, 300)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
