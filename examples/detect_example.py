import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from charset_mnbvc import api



def detect_file():
    """
    Detect file encoding
    """
    file_path = "tests/fixtures/10.txt"
    coding_name = api.get_cn_charset(source_data=file_path,  source_type="file", mode=2)
    print(f"文件名: {file_path}, 编码: {coding_name}")


def detect_files():
    """
    Detect files encoding
    """
    folder_path = "tests/fixtures/"
    file_count, results = api.from_dir(
        folder_path=folder_path,
        mode=2
    )
    print(f"文件夹: {folder_path}, 文件数: {file_count}")
    for row in results:
        print(row)

def detect_data():
    """
    Detect data encoding
    """
    with open("tests/fixtures/10.txt", "rb") as f:
        data = f.read()
        coding_name = api.from_data(data=data, mode=2)
        print(f"数据编码: {coding_name}")


if __name__ == '__main__':
    detect_file()
    detect_files()
    detect_data()
