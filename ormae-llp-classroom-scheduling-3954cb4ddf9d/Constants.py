import os

# Define the path to the 'inputs' directory and config file
INPUT_PATH = "inputs"
CONFIG_PATH = "config.json"
CURRENT_DIR = os.getcwd()

input_full_path = os.path.join(CURRENT_DIR, INPUT_PATH)
config_full_path = os.path.join(CURRENT_DIR, CONFIG_PATH)
