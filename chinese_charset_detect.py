import time
import argparse

from charset_mnbvc import api


def parse_args():
    parser = argparse.ArgumentParser(
        prog='charset_mnbvc',
        description='对大量文本文件进行快速编码检测以辅助mnbvc语料集项目的数据清洗工作'
    )
    parser.add_argument(
        '-n', '--normalizer',
        action='store_const',
        default=1, const=2,
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


def main():
    inputs = parse_args()

    start = time.time()
    file_count, results = api.from_dir(
        folder_path=inputs.folder_path, mode=inputs.normalizer
    )
    for result in results:
        print(f'文件名: {result[0]}, 编码: {result[1]}')
    print(f'总文件数: {file_count}')

    end = time.time()
    print(f'总耗时长: {end - start}')


if __name__ == '__main__':
    main()
