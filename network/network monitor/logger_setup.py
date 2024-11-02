import logging
import sys
from logging.handlers import QueueHandler, QueueListener
from multiprocessing import Queue

class LoggerSetup:
    def __init__(self):
        self.queue = Queue(-1)
        self.logger = self._setup_logger()
        self.listener = self._setup_queue_listener()
        self.listener.start()

    def _setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # Create a queue handler
        queue_handler = QueueHandler(self.queue)
        logger.addHandler(queue_handler)
        
        # Remove any existing handlers to avoid duplicate logging
        for handler in logger.handlers[:-1]:
            logger.removeHandler(handler)
        
        return logger

    def _setup_queue_listener(self):
        # Create a stream handler for console output
        stream_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        stream_handler.setFormatter(formatter)
        
        # Create and return a queue listener
        return QueueListener(self.queue, stream_handler)

    def get_logger(self):
        return self.logger

    def stop_listener(self):
        if self.listener:
            self.listener.stop()
