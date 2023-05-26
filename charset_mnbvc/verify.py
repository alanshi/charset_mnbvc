import os
import sys
from tqdm import tqdm

from .common_utils import get_file_paths


def process(dir_path: any) -> any:
    """
    读取文件夹下所有txt文件,验证是否已转换为utf-8编码
    """
    print("###################################### Step3 start ######################################")
    print("文件二次验证开始")
    print(f"检测目录: {dir_path}")
    files = get_file_paths(dir_path)
    with tqdm(desc="验证进度", total=len(files)) as pbar:
        for file_path in files:
            try:
                with open(file_path, encoding='utf-8') as f:
                    f.read()
                    pbar.update(1)
            except Exception as error:
                # 编码错误的文件名(非utf-8编码)
                sys.stderr.write(f"错误文件: {file_path}, {error}")


    print("文件二次验证结束")
    print("所有已转换为utf-8的txt文件验证完成!")
    print("###################################### Step3 end ######################################")
    return True

if __name__ == '__main__':
    dir_path = '/Users/alan/databak/mop'
    process(dir_path)