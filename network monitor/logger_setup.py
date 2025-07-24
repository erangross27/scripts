"""
This script handles logger setup.
"""

# Import required logging modules and system module
import logging
import sys
try:
    from logging.handlers import QueueHandler, QueueListener
    from multiprocessing import Queue
except ImportError:
    Queue = None
    QueueHandler = None
    QueueListener = None
    print("Warning: multiprocessing not available. Logging may be limited.")

class LoggerSetup:
    """A class to set up and manage a thread-safe logging system using a queue-based approach"""
    
    def __init__(self):
        """Initialize the logger setup with a queue, logger, and queue listener"""
        try:
            # Create an unlimited size queue for log messages
            if Queue:
                self.queue = Queue(-1)
            else:
                self.queue = None
                
            # Set up the logger instance
            self.logger = self._setup_logger()
            
            # Set up and store the queue listener
            if QueueListener:
                self.listener = self._setup_queue_listener()
                # Start the queue listener to begin processing log messages
                if self.listener:
                    self.listener.start()
            else:
                self.listener = None
        except Exception as e:
            print(f"Error initializing LoggerSetup: {e}")
            # Fallback to basic logging
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
            self.listener = None

    def _setup_logger(self):
        """Configure and return a logger instance with queue handler"""
        try:
            # Create a logger instance with the module name
            logger = logging.getLogger(__name__)
            # Set the logging level to INFO
            logger.setLevel(logging.INFO)
            
            # Only add queue handler if QueueHandler is available
            if QueueHandler and self.queue:
                # Create a handler that sends log records to the queue
                queue_handler = QueueHandler(self.queue)
                logger.addHandler(queue_handler)
                
                # Remove any pre-existing handlers to prevent duplicate logging
                # Keep only the queue handler we just added
                for handler in logger.handlers[:-1]:
                    logger.removeHandler(handler)
            else:
                # Fallback to stream handler if queue handler is not available
                if not logger.handlers:
                    stream_handler = logging.StreamHandler(sys.stdout)
                    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
                    stream_handler.setFormatter(formatter)
                    logger.addHandler(stream_handler)
            
            return logger
        except Exception as e:
            # Fallback to basic logger
            logger = logging.getLogger(__name__)
            logger.setLevel(logging.INFO)
            return logger

    def _setup_queue_listener(self):
        """Set up and return a queue listener with stream handler for console output"""
        try:
            if not QueueListener:
                return None
                
            # Create a handler that writes log messages to stdout (console)
            stream_handler = logging.StreamHandler(sys.stdout)
            # Create a formatter to define the log message format
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            # Apply the formatter to the stream handler
            stream_handler.setFormatter(formatter)
            
            # Create and return a queue listener that processes messages from the queue
            # and sends them to the stream handler
            return QueueListener(self.queue, stream_handler)
        except Exception as e:
            print(f"Error setting up queue listener: {e}")
            return None

    def get_logger(self):
        """Return the configured logger instance"""
        return self.logger

    def stop_listener(self):
        """Stop the queue listener if it exists"""
        try:
            if self.listener:
                self.listener.stop()
        except Exception as e:
            # Don't let errors in stopping the listener break the application
            pass