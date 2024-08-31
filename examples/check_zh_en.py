import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from charset_mnbvc import api


with open("tests/fixtures/test5.txt", "rb") as f:
    data = f.read()
    ret = api.check_zh_en(data)
    print(ret)
