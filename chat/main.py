import sys
import logging
from PyQt5.QtWidgets import QApplication

from config import setup_logging
from gui.main_window import ClaudeChat

def main():
    app = QApplication(sys.argv)
    setup_logging()
    
    logging.info("Application started")
    
    chat = ClaudeChat()
    chat.show()
    
    logging.info("ClaudeChat window shown")
    
    exit_code = app.exec_()
    logging.info(f"Application exited with code: {exit_code}")
    sys.exit(exit_code)

if __name__ == '__main__':
    main()