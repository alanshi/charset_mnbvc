import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from charset_mnbvc import api


def fix_data():
    """
    Fix data encoding
    """
    data_1 = "变巨"
    data_2 = "é‡ ç‚¹å»ºè®¾åŠžå…¬å®¤"
    result_1 = api.fix_data(s=data_1)
    result_2 = api.fix_data(s=data_2)

if __name__ == '__main__':
    fix_data()
