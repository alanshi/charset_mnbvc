import argparse

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from tqdm import tqdm

from charset_mnbvc import api, verify
from charset_mnbvc.common_utils import get_file_paths

def parse_args():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(
        prog='convert_files.py',
        description='对大量文本文件进行快速编码检测以辅助mnbvc语料集项目的数据清洗工作'
    )
    parser.add_argument(
        '-p', '--process_num',
        default=4,
        type=int,
        dest='process_num',
        help='指定进程数，默认为4'
    )
    parser.add_argument(
        '-m', '--mode',
        default=2,
        type=int,
        dest='mode',
        help='mode=1 mnbvc, mode=2 ccharde(默认)'
    )
    parser.add_argument(
        '-i',
        required=True,
        metavar='inputDirectory',
        dest='folder_path',
        help='inputDirectory为需要检测的目录'
    )
    return parser.parse_args()


def encoding_check(inputs):
    """
    编码检测
    """
    # file_count, files = api.from_dir(
    #     folder_path=inputs.folder_path,
    #     mode=inputs.mode
    # )
    files = []
    results = []
    files = get_file_paths(inputs.folder_path, suffix='.txt')
    with ProcessPoolExecutor(inputs.process_num) as executor:
        futures = []
        with tqdm(desc="检测进度", total=len(files)) as pbar:
            # 提交任务，并将Future对象添加到futures列表中
            for file in files:
                future = executor.submit(api.from_file, file, inputs.mode)
                futures.append(future)

            # 遍历futures列表，获取结果并更新进度条
            for future in futures:
                results.append(future.result())
                pbar.update(1)

    return results

def convert_check(file_path, encoding):
    with open(file_path, "rb") as f:
        data = f.read()
        if not data:
            return False, f"{file_path}, 文件为空"
        try:
            ret = api.decode_check(data, encoding)
            if not ret[0]:
                return False, f"{file_path}, {ret[1]}"
        except Exception as e:
            return False, f"{file_path}, {str(e)}"

    return True, "success"

def process(files, inputs):
    results = []
    with ProcessPoolExecutor(inputs.process_num) as executor:
        futures = []
        with tqdm(desc="检测进度", total=len(files)) as pbar:
            for file in files:
                file_path = file[0]
                encoding = file[1]
                # 提交任务，并将Future对象添加到futures列表中
                future = executor.submit(convert_check, file_path, encoding)
                futures.append(future)

            # 遍历futures列表，获取结果并更新进度条
            for future in futures:
                results.append(future.result())
                pbar.update(1)
    return results


def main():
    inputs = parse_args()
    input_folder = inputs.folder_path
    mode = inputs.mode
    process_num = inputs.process_num
    encoding_results = encoding_check(inputs)
    process_results = process(encoding_results, inputs)
    for i in process_results:
        if not i[0]:
            print(i)



if __name__ == "__main__":
    main()