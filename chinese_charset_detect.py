import argparse

from charset_mnbvc import api


def parse_args():
    parser = argparse.ArgumentParser(
        prog='chinese_charset_detect.py',
        description='对大量文本文件进行快速编码检测以辅助mnbvc语料集项目的数据清洗工作'
    )
    parser.add_argument(
        '-s', '--show_result',
        action='store_true',
        dest='show_result',
        help='显示编码检测结果'
    )
    parser.add_argument(
        '-c', '--cchardet',
        action='store_const',
        default=1,
        const=2,
        dest='mode',
        help='使用cchardet方案'
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

    file_count, results = api.from_dir(
        folder_path=inputs.folder_path, mode=inputs.mode
    )

    if inputs.show_result:
        for result in results:
            file_path = result[0]
            coding_name = result[1]
            print(f'文件名: {file_path}, 编码: {coding_name}')


if __name__ == '__main__':
    main()
