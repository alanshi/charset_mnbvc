import argparse
import csv
import os
import shutil
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from tqdm import tqdm

from charset_mnbvc import api, verify
from icu import UnicodeString

BLOCK_SIZE = 1024 * 1024


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
    parser.add_argument(
        '-u',
        action='store_true',
        dest='undo',
        help='恢复文件'
    )

    return parser.parse_args()


def revert_files(file_path):
    """
    根据目录恢复文件
    """
    try:
        path = Path(file_path)
        raw_file_path = f"{path.parent}/{path.stem}.raw"
        txt_file_path = f"{path.parent}/{path.stem}.txt"
        shutil.copy2(raw_file_path, txt_file_path)
        os.remove(raw_file_path)
    except Exception as e:
        return False

    return True

def convert_file_to_utf8_use_icu(input_file, output_file, encoding):
        # 打开二进制文件进行读取
    with open(input_file, "rb") as f_input:
        with open(output_file, "w") as f_output:
            data = f_input.read()
            # 将读取的数据转换为UTF-8编码
            utf8_data = UnicodeString(data, encoding.upper())
            # 将转换后的UTF-8数据写入输出文件
            f_output.write(str(utf8_data))

def convert_file_to_utf8(file):
    """
    将单个文件转换为utf-8编码
    """
    file_path = file[0]
    encoding = file[1]
    path = Path(file_path)
    raw_file_path = f"{path.parent}/{path.stem}.raw"
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
        # 检测encoding是否为gbk或者gb18030，调用pyicu进行转换
        msg = f"{file_path} {encoding} 转换到utf8失败, {e}"
        if encoding == 'gb18030' or encoding == 'gbk':
            try:
                with open(raw_file_path, "rb") as f:
                    data = f.read()
                    encoding = api.from_data(data=data, mode=3)

                convert_file_to_utf8_use_icu(raw_file_path, file_path, encoding)
                msg = msg + f" 重新转换 {encoding}，使用 icu 成功"
                return True, msg
            except Exception as e:
                msg = msg + f" 重新转换 {encoding}，使用 icu 失败"
                os.remove(file_path)
                return False, msg
        else:
            os.remove(file_path)
            return False, msg

        # os.remove(file_path)
        # return False, msg
    return True, None


def run_revert_files(files, process_num):
    """
    恢复文件
    """
    results = []
    with ProcessPoolExecutor(process_num) as executor:
        futures = []
        with tqdm(desc="文件恢复进度", total=len(files)) as pbar:
            for file in files:
                # 提交任务，并将Future对象添加到futures列表中
                future = executor.submit(revert_files, file)
                futures.append(future)

            # 遍历futures列表，获取结果并更新进度条
            for future in futures:
                results.append(future.result())
                pbar.update(1)

    return results


def run_convert_files(files, process_num):
    """
    转换文件编码
    """
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
    """
    编码检测
    """
    file_count, results = api.from_dir(
        folder_path=inputs.folder_path,
        mode=inputs.mode
    )
    return file_count, results


def main():
    """
    主函数
    """
    inputs = parse_args()
    process_step = inputs.process_step
    result_file_name = inputs.result_file_name
    undo = inputs.undo
    input_folder_path = inputs.folder_path

    if undo:
        files = []
        with open(result_file_name, newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                files.append(
                    (row[0])
                )
        run_revert_files(files, inputs.process_num)
        print("文件恢复完毕!")
        sys.exit()

    if process_step == 1:
        print("###################################### Step1 start ######################################")
        file_count, results = encoding_check(inputs)
        with open(result_file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            for row in results:
                writer.writerow(row)
        print(f"已将检测结果保存至{result_file_name}文件中,请查阅!")
        print("###################################### Step1 end ######################################")

    if process_step == 2:
        print("###################################### Step2 start ######################################")
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
            sys.stderr.write(f"{msg}\n")
        print("###################################### Step2 end ######################################")

        verify.process(input_folder_path)

    if process_step == 3:
        # auto verify files
        verify.process(input_folder_path)

if __name__ == "__main__":
    main()
