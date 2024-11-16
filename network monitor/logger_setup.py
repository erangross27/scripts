# Import required logging modules and system module
import logging
import sys
from logging.handlers import QueueHandler, QueueListener
from multiprocessing import Queue

class LoggerSetup:
    """A class to set up and manage a thread-safe logging system using a queue-based approach"""
    
    def __init__(self):
        """Initialize the logger setup with a queue, logger, and queue listener"""
        # Create an unlimited size queue for log messages
        self.queue = Queue(-1)
        # Set up the logger instance
        self.logger = self._setup_logger()
        # Set up and store the queue listener
        self.listener = self._setup_queue_listener()
        # Start the queue listener to begin processing log messages
        self.listener.start()

    def _setup_logger(self):
        """Configure and return a logger instance with queue handler"""
        # Create a logger instance with the module name
        logger = logging.getLogger(__name__)
        # Set the logging level to INFO
        logger.setLevel(logging.INFO)
        
        # Create a handler that sends log records to the queue
        queue_handler = QueueHandler(self.queue)
        logger.addHandler(queue_handler)
        
        # Remove any pre-existing handlers to prevent duplicate logging
        # Keep only the queue handler we just added
        for handler in logger.handlers[:-1]:
            logger.removeHandler(handler)
        
        return logger

    def _setup_queue_listener(self):
        """Set up and return a queue listener with stream handler for console output"""
        # Create a handler that writes log messages to stdout (console)
        stream_handler = logging.StreamHandler(sys.stdout)
        # Create a formatter to define the log message format
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        # Apply the formatter to the stream handler
        stream_handler.setFormatter(formatter)
        
        # Create and return a queue listener that processes messages from the queue
        # and sends them to the stream handler
        return QueueListener(self.queue, stream_handler)

    def get_logger(self):
        """Return the configured logger instance"""
        return self.logger

    def stop_listener(self):
        """Stop the queue listener if it exists"""
        if self.listener:
            self.listener.stop()
