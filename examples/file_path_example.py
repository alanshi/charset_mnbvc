import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from charset_mnbvc import api

from pathlib import PurePosixPath, Path
folder_path = "/Users/alan/Downloads/arXiv-0901.4554v3"
folder_path = Path(folder_path)
file_list = folder_path.rglob("**/*.*")
for file_path in file_list:
    x = api.convert_encoding(file_path.read_bytes(), "utf-8")
    print(file_path, x)
