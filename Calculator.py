import sys
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt

class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Set up the main window
        self.setWindowTitle("Pro Scientific Calculator")
        self.setGeometry(100, 100, 400, 600)

        # Create central widget and main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create display (input/output field)
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setStyleSheet("font-size: 24px; padding: 10px;")
        main_layout.addWidget(self.display)

        # Create button layout
        buttons_layout = QGridLayout()
        buttons = [
            # Scientific functions and constants
            ('sin', self.add_function), ('cos', self.add_function), ('tan', self.add_function), ('log', self.add_function),
            ('ln', self.add_function), ('√', self.add_function), ('π', self.add_constant), ('e', self.add_constant),
            ('(', self.add_to_equation), (')', self.add_to_equation), ('^', self.add_to_equation), ('abs', self.add_function),
            ('C', self.clear), ('←', self.backspace), ('%', self.calculate_percentage), ('/', self.add_to_equation),
            # Numbers and basic operations
            ('7', self.add_to_equation), ('8', self.add_to_equation), ('9', self.add_to_equation), ('*', self.add_to_equation),
            ('4', self.add_to_equation), ('5', self.add_to_equation), ('6', self.add_to_equation), ('-', self.add_to_equation),
            ('1', self.add_to_equation), ('2', self.add_to_equation), ('3', self.add_to_equation), ('+', self.add_to_equation),
            ('±', self.toggle_sign), ('0', self.add_to_equation), ('.', self.add_to_equation), ('=', self.calculate_result),
        ]

        # Create and add buttons to the layout
        for i, (text, callback) in enumerate(buttons):
            button = QPushButton(text)
            button.setStyleSheet("font-size: 16px; padding: 10px;")
            button.clicked.connect(callback)
            buttons_layout.addWidget(button, i // 4, i % 4)

        main_layout.addLayout(buttons_layout)
        
        # Initialize the equation string
        self.equation = ""
    def add_to_equation(self):
        # Add the clicked button's text to the equation
        button = self.sender()
        self.equation += button.text()
        self.display.setText(self.equation)

    def add_function(self):
        # Add the clicked function to the equation and immediately calculate it
        button = self.sender()
        function = button.text()
        if self.equation:
            try:
                result = self.calculate_function(function, float(self.equation))
                self.equation = str(result)
                self.display.setText(self.equation)
            except ValueError:
                self.display.setText("Error")
                self.equation = ""
        else:
            self.display.setText(f"{function}(")
            self.equation = f"{function}("

    def calculate_function(self, function, value):
        # Calculate the result of the function
        if function == 'sin':
            return math.sin(value)
        elif function == 'cos':
            return math.cos(value)
        elif function == 'tan':
            return math.tan(value)
        elif function == 'log':
            return math.log10(value)
        elif function == 'ln':
            return math.log(value)
        elif function == '√':
            return math.sqrt(value)
        elif function == 'abs':
            return abs(value)

    def add_constant(self):
        # Add the clicked constant (pi or e) to the equation
        button = self.sender()
        if button.text() == 'π':
            self.equation += str(math.pi)
        elif button.text() == 'e':
            self.equation += str(math.e)
        self.display.setText(self.equation)

    def calculate_result(self):
        # Evaluate the equation and display the result
        try:
            # Create a safe environment for eval
            safe_env = {
                "math": math,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "log": math.log10,
                "ln": math.log,
                "sqrt": math.sqrt,
                "abs": abs,
                "pi": math.pi,
                "e": math.e
            }
            # Evaluate the equation
            result = eval(self.equation, {"__builtins__": None}, safe_env)
            self.display.setText(str(result))
            self.equation = str(result)
        except Exception as e:
            self.display.setText("Error")
            self.equation = ""

    def clear(self):
        # Clear the equation and display
        self.equation = ""
        self.display.setText("")

    def backspace(self):
        # Remove the last character from the equation
        self.equation = self.equation[:-1]
        self.display.setText(self.equation)

    def toggle_sign(self):
        # Toggle the sign of the current number
        if self.equation.startswith('-'):
            self.equation = self.equation[1:]
        elif self.equation:
            self.equation = '-' + self.equation
        self.display.setText(self.equation)

    def calculate_percentage(self):
        # Calculate the percentage of the current number
        if self.equation:
            try:
                result = eval(self.equation) / 100
                self.equation = str(result)
                self.display.setText(self.equation)
            except Exception:
                self.display.setText("Error")
                self.equation = ""
if __name__ == "__main__":
    # Create and run the application
    app = QApplication(sys.argv)
    calc = Calculator()
    calc.show()
    sys.exit(app.exec_())