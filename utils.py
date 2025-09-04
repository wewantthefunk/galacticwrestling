import os
from pathlib import Path

def create_folder(directory):
    # Create the directory if it does not exist
    dir_path = Path(directory)
    if not dir_path.exists():
        dir_path.mkdir()