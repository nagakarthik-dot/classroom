from Constants import*
from libraries import json, os

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

configs = load_config(config_full_path)

def find_excel_files(directory):
    excel_files = []  

    # Ensure the directory exists
    if not os.path.isdir(directory):
        print(f"The directory '{directory}' does not exist.")
        return excel_files

    # List all files in the directory
    files = os.listdir(directory)

    # Filter for Excel files
    excel_files = [f for f in files if f.endswith(('.xlsx', '.xls'))]

    # Construct full paths
    full_paths = [os.path.join(directory, file_name) for file_name in excel_files]

    return full_paths

