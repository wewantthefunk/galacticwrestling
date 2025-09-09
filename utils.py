import os
from pathlib import Path

def create_folder(directory):
    # Create the directory if it does not exist
    dir_path = Path(directory)
    if not dir_path.exists():
        dir_path.mkdir()

def clear_console():
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Unix/Linux/MacOS
        os.system('clear')

def get_files(path):
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    return files 

def write_file(file, data):
    with open(file, "w") as f:
        f.write(data)

def read_file(file):
    with open(file, "r") as f:
        d = f.read()

    return d