### 项目描述
本项目旨在对大量文本文件进行快速编码检测以辅助mnbvc语料集项目的数据清洗工作

#### 实现机制
1. 读取每个文件的前500个字符(长度可定义)
2. 尝试使用4种编码对字符进行decode ```utf_8```,```utf_16```,```gb18030```,```big5```
3. 将每一组decode的结果对中文字符串和常用中文字进行正则匹配,有匹配结果的表明符合编码要求
4. 当charset-mnbvc无法检测编码或检测到多个编码结果时,会自动调用cchardect进行备用检测机制

#### 模块安装
```
pip install charset-mnbvc
```

#### charset-mnbvc pypi url:
https://pypi.org/project/charset-mnbvc/

##### 根据文件夹获取所有文件编码
```
from charset_mnbvc import api

file_count, results = api.from_dir(
    folder_path=ifolder_path,
)

for result in results:
    print(f"文件名: {result[0]}, 编码: {result[1]}")

```

##### 获取单个文件编码
```
from charset_mnbvc import api

file_path = "test.txt"
coding_name = get_cn_charset(file_path)
print(f"文件名: {file_path}, 编码: {coding_name}")

```


#### 完整使用范例:
```
python chinese_charset_detect.py -i tests
```

测试环境说明（开发测试用机):
* MacBook Air Apple M2, 内存:16 GB, 硬盘:512G, 系统版本:13.2 (22D49)**
* 默认使用charset_mnbvc方案, 可切换使用cchardet方案


#### 测试结果1 使用charset_mnbvc方案:
`python chinese_charset_detect.py -i /Users/alan/Downloads/20230101`
```
.....
文件名: /Users/alan/Downloads/20230101/aliyun.20230101.15.中医/521.txt, 编码: ['gb18030', 'gb2312']
文件名: /Users/alan/Downloads/20230101/aliyun.20230101.15.中医/509.txt, 编码: ['gb18030', 'gb2312']
文件名: /Users/alan/Downloads/20230101/aliyun.20230101.15.中医/290.txt, 编码: ['gb18030', 'gb2312']
文件名: /Users/alan/Downloads/20230101/aliyun.20230101.15.中医/284.txt, 编码: ['gb18030', 'gb2312']
总文件数: 16363
总耗时长: 2.7584381103515625
```


#### 测试结果2 使用cchardet方案: 
`python chinese_charset_detect.py -i /Users/alan/Downloads/20230101 -c`

```
......
文件名: /Users/alan/Downloads/20230101/aliyun.20230101.15.中医/247.txt, 编码: ['GB18030']
文件名: /Users/alan/Downloads/20230101/aliyun.20230101.15.中医/521.txt, 编码: ['GB18030']
文件名: /Users/alan/Downloads/20230101/aliyun.20230101.15.中医/509.txt, 编码: ['GB18030']
文件名: /Users/alan/Downloads/20230101/aliyun.20230101.15.中医/290.txt, 编码: ['GB18030']
文件名: /Users/alan/Downloads/20230101/aliyun.20230101.15.中医/284.txt, 编码: ['GB18030']
总文件数: 16363
总耗时长: 4.429999113082886
```

chinese_charset_detect.py
```
import argparse
import time

from charset_mnbvc import api


def parse_args():
    parser = argparse.ArgumentParser(
        prog='charset_mnbvc',
        description='对大量文本文件进行快速编码检测以辅助mnbvc语料集项目的数据清洗工作'
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

    start = time.time()
    file_count, results = api.from_dir(
        folder_path=inputs.folder_path, mode=inputs.mode
    )

    print(f'总文件数: {file_count}')

    end = time.time()
    print(f'总耗时长: {end - start}')


if __name__ == '__main__':
    main()

```