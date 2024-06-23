import os
import logging
import sys

def setup_logging():
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        logs_dir = os.path.join(exe_dir, "antropic_logs")
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        logs_dir = os.path.join(script_dir, "antropic_logs")

    os.makedirs(logs_dir, exist_ok=True)

    info_log_file = os.path.join(logs_dir, "info.log")
    warning_log_file = os.path.join(logs_dir, "warning.log")
    error_log_file = os.path.join(logs_dir, "error.log")

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler(info_log_file, mode='w', encoding='utf-8'),
                            logging.FileHandler(warning_log_file, mode='w', encoding='utf-8'),
                            logging.FileHandler(error_log_file, mode='w', encoding='utf-8'),
                            logging.StreamHandler()
                        ])