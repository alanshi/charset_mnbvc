import os,sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from charset_mnbvc.api import (
    convert_encoding
)


def convert_file():
    """
    Convert file encoding
    """
    source_data = b'\xb5\xda\xcb\xc4\xd5\xc2' #gbk 编码

    ret = convert_encoding(
        source_data=source_data,
        source_encoding="gbk",
        target_encoding="utf-8",
    )
    print(ret)

if __name__ == '__main__':
    convert_file()