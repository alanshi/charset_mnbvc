import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from charset_mnbvc import api


def convert_data():
    """
    Convert data encoding
    """
    source_data = b'\xb5\xda\xcb\xc4\xd5\xc2' #gbk 编码

    ret = api.convert_encoding(
        source_data=source_data,
        source_encoding="gbk",
        target_encoding="utf-8",
    )
    print(ret)

if __name__ == '__main__':
    convert_data()
