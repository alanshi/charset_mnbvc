### 项目描述
本项目旨在对大量文本文件进行快速编码检测以辅助mnbvc语料集项目的数据清洗工作

#### 实现机制
1. 读取每个文件的前100个字符(长度可定义)
2. 尝试使用5种编码对字符进行decode ```utf_8```,```utf_16```,```gb18030```,```gb2312```,```big5```
3. 将每一组decode的结果对中文字符串和常用中文字进行正则匹配,有匹配结果的表明符合编码要求

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
* 默认使用charset_mnbvc方案, 可以用过修改api.py 19行,设置 mode=2切换至使用charset_normalizer方案
```
coding_name = get_cn_charset(file_path, mode=2)
```

#### 测试结果1 使用charset_mnbvc方案:
```
.....
文件名: /Users/alan/Downloads/1/mop/律师信，豪宅，及其他⋯⋯（豆腐脑自吹自擂兼自874⋯⋯）.txt, 编码: ['gb18030', 'gb2312']
文件名: /Users/alan/Downloads/1/mop/0426.txt, 编码: ['gb18030', 'gb2312']
文件名: /Users/alan/Downloads/1/mop/穷人！只能这样了.txt, 编码: ['gb18030', 'gb2312']
文件名: /Users/alan/Downloads/1/mop/大家作过最BT的事是什么？.txt, 编码: ['gb18030', 'gb2312']
文件名: /Users/alan/Downloads/1/mop/我的MOP历程.txt, 编码: ['gb18030', 'gb2312']
总文件数: 1919
总耗时长: 0.3409309387207031
```
#### 测试结果2 使用charset_normalizer方案:
```
......
文件名: /Users/alan/Downloads/1/mop/律师信，豪宅，及其他⋯⋯（豆腐脑自吹自擂兼自874⋯⋯）.txt, 编码: ['gbk']
文件名: /Users/alan/Downloads/1/mop/0426.txt, 编码: ['iso8859_5']
文件名: /Users/alan/Downloads/1/mop/穷人！只能这样了.txt, 编码: ['gbk']
文件名: /Users/alan/Downloads/1/mop/大家作过最BT的事是什么？.txt, 编码: ['cp949']
文件名: /Users/alan/Downloads/1/mop/我的MOP历程.txt, 编码: ['cp949']
总文件数: 1919
总耗时长: 3.112574815750122
```


chinese_charset_detect.py
```
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
```