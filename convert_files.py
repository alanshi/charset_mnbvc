import time
import sys
import getopt
from charset_mnbvc import api


def convert_to_utf8(file_path, old_encoding):
    try:
        BLOCKSIZE = 1024 * 1024
        with open(file_path, 'rb') as inf:
            with open(file_path, 'wb') as ouf:
                while True:
                    data = inf.read(BLOCKSIZE)
                    if not data: break
                    converted = data.decode(old_encoding).encode('utf-8')
                    ouf.write(converted)
        return True
    except Exception as e:
        print(e)
    return False

def main(argv):
    ifolder_path = ""
    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifolder_path="])
    except getopt.GetoptError:
        print('chinese_charset_detect.py -i <inputDirectory>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('chinese_charset_detect.py -i <inputDirectory> inputDirectory为需要检测的目录')
            sys.exit()
        elif opt in ("-i", "--ifolder_path"):
         ifolder_path = arg

    start = time.time()
    file_count, results = api.from_dir(
        folder_path=ifolder_path,
    )
    for result in results:
        file_path = result[0]
        encoding = result[1]
        if "utf_8" not in encoding or "utf_16" not in encoding:
            old_encoding = encoding[0]
            ret = convert_to_utf8(file_path=file_path, old_encoding=old_encoding)
            print(f"文件: {file_path} 转换为utf-8: {ret}")
    print(f"总文件数: {file_count}")
    end = time.time()
    print(f"总耗时长: {end - start}")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as e:
        print('convrt_files.py -i <inputDirectory> inputDirectory为需要转换的目录')
        sys.exit(2)
