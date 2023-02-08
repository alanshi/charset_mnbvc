import time
import sys
import getopt
import re
import os

from charset_normalizer import from_path

# read file in chunks
CHUNK_SIZE = 100

# 正则判断中文标点符号,标点符号包含 。 ； ， ： “ ”（ ） 、 ？ 《 》 空格
REGEX_FEATURE = r"[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u3000]"

# 正则判断中文标点符号和常见汉字,标点符号包含 。 ； ， ： “ ”（ ） 、 ？ 《 》 空格
# 常见汉字包含 的一是不了在人有我他这个们中来上大为和国地到以说时要就出会可也你对生
REGEX_FEATURE_ALL = r"[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u3000\u7684\u4e00\u662f\u4e0d\u4e86\u5728\u4eba\u6709\u6211\u4ed6\u8fd9\u4e2a\u4eec\u4e2d\u6765\u4e0a\u5927\u4e3a\u548c\u56fd\u5730\u5230\u4ee5\u8bf4\u65f6\u8981\u5c31\u51fa\u4f1a\u53ef\u4e5f\u4f60\u5bf9\u751f\u80fd\u800c\u5b50\u90a3\u5f97\u4e8e\u7740\u4e0b\u81ea\u4e4b\u5e74\u8fc7\u53d1\u540e\u4f5c\u91cc\u7528\u9053\u884c\u6240\u7136\u5bb6\u79cd\u4e8b\u6210\u65b9\u591a\u7ecf\u4e48\u53bb\u6cd5\u5b66\u5982\u90fd\u540c\u73b0\u5f53\u6ca1\u52a8\u9762\u8d77\u770b\u5b9a\u5929\u5206\u8fd8\u8fdb\u597d\u5c0f\u90e8\u5176\u4e9b\u4e3b\u6837\u7406\u5fc3\u5979\u672c\u524d\u5f00\u4f46\u56e0\u53ea\u4ece\u60f3\u5b9e]"

ENCODINGS = [
    "utf_8",
    "utf_16",
    "gb18030",
    "gb2312",
    "big5",
]

def check_chinese_charset_v1(file_path):
    try:
        with open(file_path, "rb") as fp:
            data = fp.read(CHUNK_SIZE)
            if not data:
                return False

            # 编码转换
            converted_info = {
                encoding: data.decode(encoding=encoding, errors="ignore")
                for encoding in ENCODINGS
            }

            # 正则匹配
            final_encodings = [
                k
                for k, v in converted_info.items() if re.findall(REGEX_FEATURE_ALL, v)
            ]

            # 判断有任意一个匹配结果
            if final_encodings:
                return final_encodings[0]
    except Exception as e:
        print(e)
        return e
    return "unknow"


def check_chinese_charset_v2(file_path):
    # by charset_normalizer library
    result = from_path(file_path, chunk_size=CHUNK_SIZE)
    result = result.first()
    if not result:
        return False
    return result.encoding


def check_files_encoding(folder_path):
    sub_folders, files = run_fast_scandir(folder_path)
    file_count = 0
    for file_path in files:
        file_count += 1
        coding_name = check_chinese_charset_v1(file_path)
        print(f"文件名: {file_path}, 编码: {coding_name}")
    print(f"总文件数: {file_count}")


def run_fast_scandir(folder_path, ext=".txt"):
    subfolders, files = [], []
    for f in os.scandir(folder_path):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                files.append(f.path)

    for directory in list(subfolders):
        sf, f = run_fast_scandir(directory, ext)
        subfolders.extend(sf)
        files.extend(f)
    return subfolders, files


def main(argv):
    ifolder_path = ""
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifolder_path="])
    except getopt.GetoptError:
        print('test.py -i <inputDirectory>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('chinese_charset_detect.py -i <inputDirectory> inputDirectory为需要检测的目录')
            sys.exit()
        elif opt in ("-i", "--ifolder_path"):
         ifolder_path = arg

    start = time.time()
    check_files_encoding(
        folder_path=ifolder_path,
    )
    end = time.time()
    print(f"总耗时长: {end - start}")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as e:
        print('chinese_charset_detect.py -i <inputDirectory> inputDirectory为需要检测的目录')
        sys.exit(2)
