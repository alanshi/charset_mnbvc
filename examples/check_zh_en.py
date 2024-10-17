import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from charset_mnbvc import api, common_utils



def check_zh_en_by_folder(folder_path):
    file_paths = common_utils.get_file_paths(folder_path)
    for file_path in file_paths:
        with open(file_path, "rb") as f:
            data = f.read()
            ret, percentage = api.check_zh_en(data)
            print(file_path,ret, f"zh,en percentage:{percentage:.2f}%")

def check_zh_en_by_file(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        ret, percentage = api.check_zh_en(data)
        print(f"是否为中英文文档: {ret}, 比例: {percentage}")


if __name__ == "__main__":
    # load directory

    folder_path = "/Users/alan/Downloads/text.output"
    # file_path = "tests/fixtures/18.txt"
    check_zh_en_by_folder(folder_path)
    # check_zh_en_by_file(file_path)