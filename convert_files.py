import time
import os
import argparse

from charset_mnbvc import api

ENCODING_MAP = {
    "big5hkscs": "big5"
}
BLOCK_SIZE = 1024 * 1024


def parse_args():
    parser = argparse.ArgumentParser(
        prog='charset_mnbvc',
        description='对大量文本文件进行快速编码检测以辅助mnbvc语料集项目的数据清洗工作'
    )
    parser.add_argument(
        '-c', '--cchardet',
        action='store_const',
        default=1,
        const=3,
        dest='mode',
        help='使用cchardet方案'
    )
    parser.add_argument(
        '-n', '--normalizer',
        action='store_const',
        default=1,
        const=2,
        dest='mode',
        help='使用charset_normalizer方案'
    )
    parser.add_argument(
        '-i',
        required=True,
        metavar='inputDirectory',
        dest='folder_path',
        help='inputDirectory为需要检测的目录'
    )

    return parser.parse_args()


def convert_to_utf8(file_path, old_encoding):
    path, file_name = os.path.split(file_path)
    new_file_path = file_name.split(".")[0]
    file_ext = file_name.split(".")[1]
    target_file_path = f"{path}/{new_file_path}_bak.{file_ext}"
    try:
        with open(file_path, 'rb') as inf:
            with open(target_file_path, 'wb') as ouf:
                while True:
                    data = inf.read(BLOCK_SIZE)
                    if not data:
                        break
                    converted = data.decode(old_encoding).encode('utf-8')
                    ouf.write(converted)
    except Exception as e:
        print(e)
        return False
    return True


def main():
    inputs = parse_args()
    start = time.time()
    file_count, results = api.from_dir(
        folder_path=inputs.folder_path,
        mode=inputs.normalizer
    )
    for result in results:
        file_path = result[0]
        encoding = result[1]
        if not encoding:
            continue

        if "utf_8" not in encoding or "utf_16" not in encoding:
            old_encoding = encoding[0]
            old_encoding = ENCODING_MAP.get(old_encoding, old_encoding)
            ret = convert_to_utf8(
                file_path=file_path,
                old_encoding=old_encoding
            )
            print(f"文件: {file_path} 转换为utf-8: {ret}")
    print(f"总文件数: {file_count}")
    end = time.time()
    print(f"总耗时长: {end - start}")


if __name__ == "__main__":
    main()
