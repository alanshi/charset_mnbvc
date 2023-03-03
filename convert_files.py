import os
import shutil
import argparse
import concurrent.futures
import tqdm

from charset_mnbvc import api

BLOCK_SIZE = 1024 * 1024


def parse_args():
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


def convert_file_to_utf8(file):
    file_path = file[0]
    encoding = file[1]
    path, file_name = os.path.split(file_path)
    new_file_name = file_name.split(".")[0]
    raw_file_path = f"{path}/{new_file_name}.raw"
    # backup process
    shutil.copy2(file_path, raw_file_path)

    old_encoding = None

    if not encoding:
        msg = f"{file_path} 转换失败, 编码格式错误:{encoding}, 可能是文件内容为空!"
        return False, msg

    if "utf_8" not in encoding or "utf_16" not in encoding:
        old_encoding = encoding[0]

    if not old_encoding:
        msg = f"{file_path} 转换失败, 编码格式错误:{encoding}, 可能是文件内容为空!"
        return False, msg

    try:
        # overwrite origin file
        with open(raw_file_path, 'rb') as inf:
            with open(file_path, 'wb') as ouf:
                while True:
                    data = inf.read(BLOCK_SIZE)
                    if not data:
                        break
                    converted = data.decode(old_encoding, 'ignore').encode('utf-8')
                    ouf.write(converted)
    except Exception as e:
        msg = f"{file_path} [{old_encoding}] convert to utf-8 Failed, {e}"
        return False, msg

    return True, None


def run(files, process_num):
    with concurrent.futures.ProcessPoolExecutor(process_num) as executor:
        results = list(tqdm.tqdm(executor.map(convert_file_to_utf8, files), "文件转换进度",  total=len(files)))
    return results


def main():

    inputs = parse_args()
    # 获取文件编码
    file_count, files = api.from_dir(
        folder_path=inputs.folder_path,
        mode=inputs.mode
    )
    results = run(files, inputs.process_num)
    success_count = len([
        i
        for i in results if i[0]
    ])
    failed_count = len([
        i
        for i in results if not i[0]
    ])
    failed_msgs = [
        i[1]
        for i in results if not i[0]
    ]

    print(f"总文件数: {file_count}")
    print(f"转换成功文件数: {success_count}")
    print(f"转换失败文件数: {failed_count}")
    for msg in failed_msgs:
        print(msg)


if __name__ == "__main__":
    main()
