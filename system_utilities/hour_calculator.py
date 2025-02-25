"""
This script handles hour calculator.
"""

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
    Converts total minutes into 'hours:minutes' string, with rounding to nearest minute.
    """
    total_minutes = round(total_minutes)
    sign = '-' if total_minutes < 0 else ''
    total_minutes = abs(total_minutes)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{sign}{hours}:{minutes:02d}"

def evaluate_expression(tokens):
    """
    Given a list of tokens in the form [time_in_minutes, operator, time_in_minutes, operator, ...],
    evaluate them with standard operator precedence (*, / before +, -).

    Returns the final result in minutes (float).
    """

    # First pass: handle * and /
    # We'll build a new list (temp) that collapses multiplication/division immediately.
    temp = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if isinstance(token, float):
            # Just push the number into temp, but watch for next operator if it's * or /
            if i + 1 < len(tokens) and tokens[i+1] in ('*', '/'):
                operator = tokens[i+1]
                # Next token after operator
                if i+2 < len(tokens):
                    next_value = tokens[i+2]
                    if not isinstance(next_value, float):
                        raise ValueError("Invalid expression structure.")

                    if operator == '*':
                        # Multiply by hours factor
                        # e.g. (time_in_minutes) * (next_value/60)
                        # but we handle it as integer minutes times decimal multiplier
                        factor = next_value / 60.0
                        merged = round(token * factor)
                    else:  # operator == '/'
                        factor = next_value / 60.0
                        if factor == 0:
                            raise ValueError("Division by zero is not allowed.")
                        merged = round(token / factor)

                    # Put merged result into temp
                    temp.append(float(merged))
                    # Skip ahead past the operator & next value
                    i += 3
                else:
                    raise ValueError("Invalid expression: operator at the end.")
            else:
                # No multiplication or division next; just push the time
                temp.append(token)
                i += 1
        else:
            # If it's an operator + or -, just push it for second pass
            # If it's * or /, that means there's no valid time before/after it, which is an error
            if token in ('*', '/'):
                raise ValueError("Invalid position for '*' or '/'.")
            temp.append(token)
            i += 1

    # Second pass: handle + and -
    # Now temp should contain minutes or + or - only.
    if not temp:
        return 0.0
    result = temp[0]
    i = 1
    while i < len(temp):
        operator = temp[i]
        next_value = temp[i+1]
        if operator == '+':
            result += next_value
        elif operator == '-':
            result -= next_value
        i += 2

    return result

class TimeCalculator(QWidget):
    """
    Represents a time calculator.
    """
    def __init__(self):
        """
        Special method __init__.
        """
        super().__init__()
        self.setWindowTitle("מחשבון שעות (עשרוני)")

        # Display for showing the expression (not just the current value).
        # We'll keep the "expression_display" to show what the user typed so far (tokens).
        self.expression_display = QLineEdit()
        self.expression_display.setReadOnly(True)
        self.expression_display.setStyleSheet("font-size: 14px; height: 25px;")

        # Display for the current input (where user types hours:minutes or partial numbers)
        self.current_input = QLineEdit()
        self.current_input.setStyleSheet("font-size: 18px; height: 40px;")

        # We store tokens in a list: [float_minutes, operator, float_minutes, operator, ...]
        self.tokens = []

        grid = QGridLayout()
        grid.addWidget(self.expression_display, 0, 0, 1, 4)
        grid.addWidget(self.current_input,     1, 0, 1, 4)

        # Button definitions
        buttons = {
            '7': (2, 0), '8': (2, 1), '9': (2, 2),
            '4': (3, 0), '5': (3, 1), '6': (3, 2),
            '1': (4, 0), '2': (4, 1), '3': (4, 2),
            '0': (5, 0),
            ':': (5, 1),
            'נקה': (5, 2),
            '+': (2, 3), '-': (3, 3), '*': (4, 3), '/': (5, 3),
            'שווה': (6, 0, 1, 4)
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
        """
        On button clicked.
        """
        sender = self.sender()
        text = sender.text()

        if text.isdigit() or text == ':':
            # Append digit or ':' to current input
            self.current_input.setText(self.current_input.text() + text)
            return

        if text == 'נקה':
            self.clear_all()
            return

        if text in ['+', '-', '*', '/']:
            self.process_operator(text)
            return

        if text == 'שווה':
            self.process_equals()
            return

    def clear_all(self):
        """Reset everything."""
        self.tokens = []
        self.current_input.clear()
        self.expression_display.clear()

    def process_operator(self, operator):
        """
        1. Parse whatever is in `current_input` to minutes and store it in tokens.
        2. Store the operator in tokens.
        3. Clear the input field.
        4. Update the expression_display to show the user the ongoing expression.
        """
        val_str = self.current_input.text().strip()
        if val_str:
            try:
                minutes_val = parse_time(val_str)
            except ValueError as e:
                self.show_error(str(e))
                return
            self.tokens.append(minutes_val)
            self.current_input.clear()
            # Update expression display
            self.update_expression_display(val_str)

        # Now store the operator
        # But don't store an operator if the last token was also an operator (avoid duplicates)
        if self.tokens and not isinstance(self.tokens[-1], str):
            self.tokens.append(operator)
            # For expression display
            self.expression_display.setText(self.expression_display.text() + f" {operator} ")

    def process_equals(self):
        """
        1. Parse the last input (if any).
        2. Evaluate the list of tokens with operator precedence.
        3. Display the final result.
        """
        val_str = self.current_input.text().strip()
        if val_str:
            try:
                minutes_val = parse_time(val_str)
            except ValueError as e:
                self.show_error(str(e))
                return
            self.tokens.append(minutes_val)
            self.update_expression_display(val_str)
            self.current_input.clear()

        if not self.tokens:
            return

        # If the last token is an operator, remove it to avoid error
        if isinstance(self.tokens[-1], str):
            self.tokens.pop()

        try:
            result_minutes = evaluate_expression(self.tokens)
        except ValueError as e:
            self.show_error(str(e))
            self.clear_all()
            return

        self.expression_display.setText(self.expression_display.text() + " =")
        self.current_input.setText(format_hours(result_minutes))
        # Clear tokens so next operation starts fresh (or you could keep them, depending on preference)
        self.tokens = []

    def update_expression_display(self, new_part):
        """
        Updates the expression display with the newly entered time or operator.
        If the last character was '=' from a previous calculation, clear first.
        """
        txt = self.expression_display.text()
        # If previous expression ended with "=", start fresh
        if txt.endswith('='):
            txt = ""
        if txt and not txt.endswith(' '):
            txt += " "
        txt += new_part
        self.expression_display.setText(txt)

    def show_error(self, message):
        """
        Show error based on message.
        """
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Warning)
        error_dialog.setText(message)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec_()

def main():
    """
    Main.
    """
    app = QApplication(sys.argv)
    window = TimeCalculator()
    window.resize(350, 400)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
