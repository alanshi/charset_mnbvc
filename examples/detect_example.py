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

def detect_data_by_mnbvc():
    data = b'\xd6\xa7\xb3\xc5\xb2\xc4\xc1\xcf/Code/p_3_1.m'
    coding_name = api.get_cn_charset(
        source_data=data,
        source_type="data",
        mode=1,
        special_encodings=["gbk", "gb2312", "utf-8"]
    )
    print(coding_name)

def detect_url():
    import requests
    url = "http://www.webpage.idv.tw/maillist/maillist3/skill/05/meta.htm"
    data = requests.get(url).content
    coding_name = api.get_cn_charset(
        source_data=data,
        source_type="data",
        mode=2,
    )
    print(coding_name)


if __name__ == '__main__':
    #detect_url()
    detect_file()
    detect_files()
    detect_data()
    detect_data_by_mnbvc()
