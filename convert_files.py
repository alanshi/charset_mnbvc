import os
import csv
import shutil
import argparse
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

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
        default=2,
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
    parser.add_argument(
        '-step',
        default=1,
        type=int,
        dest='process_step',
        help='执行步骤,1为编码检测,2为编码转换'
    )
    parser.add_argument(
        '-r',
        required=True,
        metavar='result_file_name',
        dest='result_file_name',
        help='指定编码检测结果文件名'
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
    if not encoding:
        msg = f"{file_path} 转换失败, 编码格式错误:{encoding} 可能是文件内容为空!"
        os.remove(file_path)
        return False, msg

    try:
        # overwrite raw file
        with open(raw_file_path, "r", encoding=encoding) as f_in:
            with open(file_path, "w", encoding="utf-8") as f_out:
                f_out.write(f_in.read())

    except Exception as e:
        msg = f"{file_path} {encoding}转换到utf8失败, {e}"
        os.remove(file_path)
        return False, msg

    return True, None


def run_convert_files(files, process_num):
    results = []
    with ProcessPoolExecutor(process_num) as executor:
        futures = []
        with tqdm(desc="编码转换进度", total=len(files)) as pbar:
            for file in files:
                # 提交任务，并将Future对象添加到futures列表中
                future = executor.submit(convert_file_to_utf8, file)
                futures.append(future)

            # 遍历futures列表，获取结果并更新进度条
            for future in futures:
                results.append(future.result())
                pbar.update(1)

    return results

def encoding_check(inputs):
    # 获取文件编码
    file_count, results = api.from_dir(
        folder_path=inputs.folder_path,
        mode=inputs.mode
    )
    return file_count, results

def main():

    inputs = parse_args()
    process_step = inputs.process_step
    result_file_name = inputs.result_file_name

    if process_step == 1:
        file_count, results = encoding_check(inputs)
        with open(result_file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            for row in results:
                writer.writerow(row)
        print(f"已将检测结果保存至{result_file_name}文件中,请查阅!")

    else:
        files = []
        with open(result_file_name, newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                files.append(
                    (row[0],row[1])
                )
        results = run_convert_files(files, inputs.process_num)

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
        print(f"总文件数: {len(results)}")
        print(f"转换成功文件数: {success_count}")
        print(f"转换失败文件数: {failed_count}")
        for msg in failed_msgs:
            print(msg)


if __name__ == "__main__":
    main()
