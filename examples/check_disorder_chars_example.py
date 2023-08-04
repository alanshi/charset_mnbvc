from charset_mnbvc import api
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def check_disorder_chars():
    """
    check the disorder chars
    """
    file_path = "/Users/alan/mywork/mnbvc/tests/fixtures/errors/48.txt"
    ret, ratio = api.check_disorder_chars(file_path=file_path, threshold=0.05)
    print(f"包含乱码的字符拷锟斤等字符, 乱码比例约:{round(float(ratio)*100)}%" if ret else "未找到乱码的字符，请注意调节阈值")


if __name__ == '__main__':
    check_disorder_chars()