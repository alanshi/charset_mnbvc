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

#### 编码转换使用范例:
NOTICE: 文件默认转换为utf-8格式, 文件转换前后会将原始文件原地复制为raw格式用于备份, 并用utf-8格式覆盖原始文件, 操作流程如下:

1: 原地复制test.txt 到 test.raw

2: 将文本使用utf-8格式覆盖到test.txt

```
usage: convert_files.py [-h] [-p PROCESS_NUM] [-c] -i inputDirectory [-step PROCESS_STEP] -r result_file_name [-u]

对大量文本文件进行快速编码检测以辅助mnbvc语料集项目的数据清洗工作

optional arguments:
  -h, --help            show this help message and exit
  -p PROCESS_NUM, --process_num PROCESS_NUM
                        指定进程数，默认为4
  -c, --cchardet        使用cchardet方案
  -i inputDirectory     inputDirectory为需要检测的目录
  -step PROCESS_STEP    执行步骤,1为编码检测,2为编码转换
  -r result_file_name   指定编码检测结果文件名
  -u                    恢复文件
```
编码检测范例:
`python convert_files.py -i /Downloads/20230109 -step 1 -r check_result.csv`

```
编码检测进度: 100%|████████████████████████████| 5609/5609 [00:00<00:00, 9462.80it/s]
已将检测结果保存至check_results.csv文件中,请查阅!
```

编码转换 范例:
`python convert_files.py -i /Downloads/20230101 -step 2 -r check_result.csv`
```
编码转换进度: 100%|████████████████████████████| 5621/5621 [00:33<00:00, 169.93it/s]
总文件数: 5621
转换成功文件数: 5609
转换失败文件数: 12
/Users/alan/Downloads/20230109/zlibrary.20230109.1.杂书/5695175.txt 转换失败, 编码格式错误: 可能是文件内容为空!
/Users/alan/Downloads/20230109/zlibrary.20230109.1.杂书/5753250.txt 转换失败, 编码格式错误: 可能是文件内容为空!
......
```

测试环境说明（开发测试用机):
* MacBook Air Apple M2, 内存:16 GB, 硬盘:512G, 系统版本:13.2 (22D49)**, Python 3.9.6
* 默认使用charset_mnbvc方案, 可切换使用cchardet方案