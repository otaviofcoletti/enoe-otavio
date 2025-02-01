import logging
from logging.handlers import TimedRotatingFileHandler
import os

class Logger:
    def __init__(self, name, log_dir='./log', rotation='W0', retention=20, level=logging.DEBUG):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = os.path.join(log_dir, f'{name}.log')
        handler = TimedRotatingFileHandler(log_file, when=rotation, interval=1, backupCount=retention)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

    def get_logger(self):
        return self.logger

# Usage example
if __name__ == "__main__":
    main_logger = Logger('main', rotation='W0').get_logger()  # Weekly rotation
    main_logger.info("This is an info message")
