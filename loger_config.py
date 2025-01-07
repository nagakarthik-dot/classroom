# logger_config.py
import logging
from datetime import datetime
import os

# Create a directory for logs if it doesn't exist
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

# Generate a unique log file name with a timestamp
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file_name = f"Scenerio_log_{timestamp}.txt"
log_file_path = os.path.join(log_dir, log_file_name)

# Configure the custom logger
custom_logger = logging.getLogger('customLogger')
custom_logger.setLevel(logging.INFO)

# Create a file handler for the custom log file
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)

# Create a logging format
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the custom logger
custom_logger.addHandler(file_handler)
