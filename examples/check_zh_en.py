import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from charset_mnbvc import api, common_utils

# load directory
folder_path = "tests/fixtures/"

file_paths = common_utils.get_file_paths(folder_path)
for file_path in file_paths:
    with open(file_path, "rb") as f:
        data = f.read()
        ret, percentage = api.check_zh_en(data)
        print(file_path,ret, f"zh,en percentage:{percentage:.2f}%")
