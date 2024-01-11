### 项目描述
本项目旨在对大量文本文件进行快速编码检测以辅助mnbvc语料集项目的数据清洗工作


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
coding_name = api.get_cn_charset(file_path)
print(f"文件名: {file_path}, 编码: {coding_name}")

```

##### 获取二进制数据编码
```
from charset_mnbvc import api

with open("tests/fixtures/10.txt", "rb") as f:
    data = f.read()
    coding_name = api.from_data(data=data, mode=2)
    print(f"数据编码: {coding_name}")
```

###### 转换二进制数据编码
```
from charset_mnbvc import api

source_data = b'\xb5\xda\xcb\xc4\xd5\xc2' #gbk 编码

ret = api.convert_encoding(
    source_data=source_data,
    source_encoding="gbk",
    target_encoding="utf-8",
)
print(ret)
```

###### 尝试修复乱码数据
```
from charset_mnbvc import api
data_1 = "变巨"

result_1 = api.fix_data(s=data_1)
print(f"修复测试1: {result_1}")

from      | to        | origin | guess
-----------------------------------
utf-8     | gbk       | 变巨 | 鍙樺法
utf-8     | gb18030   | 变巨 | 鍙樺法
utf-8     | BIG5      | 变巨 | ���撌�
utf-8     | shift_jis | 变巨 | 蜿伜ｷｨ
utf-8     | euc_kr    | 变巨 | ���藥�
utf-8     | ascii     | 变巨 | ������
utf-8     | utf_16    | 变巨 | 迥ꢷ
utf-8     | cp1252    | 变巨 | å�˜å·¨
gbk       | utf-8     | 变巨 | ���
gbk       | gb18030   | 变巨 | 变巨
gbk       | BIG5      | 变巨 | 曹操
gbk       | shift_jis | 变巨 | ｱ萓ﾞ
gbk       | euc_kr    | 变巨 | 긴앵
gbk       | ascii     | 变巨 | ����
```

###### 乱码比例检测工具
```
from charset_mnbvc import api
file_path = "/Users/alan/mywork/mnbvc/tests/fixtures/errors/48.txt"
ret, ratio = api.check_disorder_chars(file_path=file_path, threshold=0.05)
print(f"包含乱码的字符拷锟斤等字符, 乱码比例约:{round(float(ratio)*100)}%" if ret else "未找到乱码的字符，请注意调节阈值")

结果:
包含乱码的字符拷锟斤等字符, 乱码比例约:28%

```

###### 指定检测编码范围
某些情况下，我们希望编码检测时只输出我们预期的编码格式，即可采用这种方法（目前仅对mode=1 有效），设计本模式的原因是大多数情况下，短文本的编码无法被正确的被识别出，可能会误报，本来是gbk的编码可能会误报为utf-8或者是别的编码。详情请查看 https://wiki.mnbvc.org/doku.php/%E7%9F%AD%E6%96%87%E6%9C%AC%E6%97%A0%E6%B3%95%E6%AD%A3%E7%A1%AE%E6%A3%80%E6%B5%8B%E7%BC%96%E7%A0%81%E7%9A%84%E9%97%AE%E9%A2%98
```
from charset_mnbvc import api
data = b'\xd6\xa7\xb3\xc5\xb2\xc4\xc1\xcf/Code/p_3_1.m'
coding_name = api.get_cn_charset(
    source_data=data,
    source_type="data",
    mode=1,
    special_encodings=["gbk"]
)
print(coding_name)
```

#### 测试数据:
开发测试时 请参考 tests/fixtures里的所有文本数据进行测试，或者使用更多的数据样本进行测试，以下是数据样本网盘地址：

20230101.zip 压缩包7.34GB，原始17.11GB
[百度网盘](https://pan.baidu.com/s/1TLEkczf5_pQlWcXwLPPcEw?pwd=78uq)

1_dir_need_check.zip 9.94GB，原始22.98GB
[百度网盘](https://pan.baidu.com/s/1IitNwAIbeZH9-Ah5eGCHfA?pwd=49yc)

20221224.zip 压缩包4.57GB，原始13.45GB
[百度网盘](https://pan.baidu.com/s/19DWSU68IukKWQqoEgjuVRQ?pwd=dh2n)

20221225.zip 压缩包7.53GB，原始17.68GB
[百度网盘](https://pan.baidu.com/s/1nTVNwayGfon8-R87TuCYfQ?pwd=76jy)


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
  -c, --cchardet        使用cchardet方案,
  -m, --mode            mode=1 mnbvc方案 , mode=2 cchardet方案(默认)
  -i inputDirectory     inputDirectory为需要检测的目录
  -step PROCESS_STEP    执行步骤,1为编码检测,2为编码转换
  -r result_file_name   指定编码检测结果文件名
  -u                    恢复文件
```
编码检测范例:
`python convert_files.py -i /Users/alan/temp_test -step 1 -r check_result.csv`

```
###################################### Step1 start ######################################
编码检测进度: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████| 2152/2152 [00:00<00:00, 3275.19it/s]
已将检测结果保存至check_result.csv文件中,请查阅!
###################################### Step1 end ######################################
```

编码转换 范例(转换完毕后自动加入step3 用于二次验证已转换为utf-8的文件是否正常):
`python convert_files.py -i /Users/alan/temp_test -step 2 -r check_result.csv`
```
###################################### Step2 start ######################################
编码转换进度: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████| 2152/2152 [00:00<00:00, 5229.08it/s]
总文件数: 2152
转换成功文件数: 2143
转换失败文件数: 9
/Users/alan/temp_test/mop/xxx.txt gb18030 转换到utf8失败, 'gb18030' codec can't decode byte 0xff in position 4567: illegal multibyte sequence
/Users/alan/temp_test/mop/larry vs psplayer.txt gb18030 转换到utf8失败, 'gb18030' codec can't
###################################### Step2 end ######################################
###################################### Step3 start ######################################
文件二次验证开始
检测目录: /Users/alan/temp_test
编码转换进度: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████| 2134/2134 [00:00<00:00, 27680.81it/s]
文件二次验证结束
所有已转换为utf-8的txt文件验证完成!
###################################### Step3 end ######################################
......
```

单独进行utf-8文件二次验证:
`python convert_files.py -i /Users/alan/temp_test -step 3 -r check_result.csv`

```
###################################### Step3 start ######################################
文件二次验证开始
检测目录: /Users/alan/temp_test
验证进度: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 2134/2134 [00:00<00:00, 8758.18it/s]
文件二次验证结束
所有已转换为utf-8的txt文件验证完成!
###################################### Step3 end ######################################
```

测试环境说明（开发测试用机):
* MacBook Air Apple M2, 内存:16 GB, 硬盘:512G, 系统版本:13.2 (22D49)**, Python 3.9.6
* 默认使用charset_mnbvc方案, 可切换使用cchardet方案

#### wiki地址:
https://wiki.mnbvc.org/doku.php/ylzq



