import time
import sys
import getopt
from charset_mnbvc import api


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
    file_count, results = api.from_dir(
        folder_path=ifolder_path,
    )
    for result in results:
        print(f"文件名: {result[0]}, 编码: {result[1]}")
    print(f"总文件数: {file_count}")


    end = time.time()
    print(f"总耗时长: {end - start}")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as e:
        print('chinese_charset_detect.py -i <inputDirectory> inputDirectory为需要检测的目录')
        sys.exit(2)
