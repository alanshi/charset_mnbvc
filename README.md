### 项目描述
本项目旨在对大量文本文件进行快速编码检测以辅助mnbvc语料集项目的数据清洗工作

#### 实现机制
1. 读取每个文件的前100个字符(长度可定义)
2. 尝试使用5种编码对字符进行decode ```utf_8```,```utf_16```,```gb18030```,```gb2312```,```big5```
3. 将每一组decode的结果对中文字符串和常用中文字进行正则匹配,有匹配结果的表明符合编码要求


#### 使用说明
* chinese_charset_detect.py -i <inputDirectory> inputDirectory为需要检测的目录
* dist目录包含macos下的可执行文件,windows环境下暂未打包,希望有朋友帮忙编译一下

#### 模块调用方法
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


#### 使用可执行文件范例:
```
./dist/chinese_charset_detect -i tests
or
python chinese_charset_detect.py -i tests
```

```
#### 测试结果:
文件名: tests/.DS_Store, 编码: unknow
文件名: tests/fixtures/test4.txt, 编码: gb18030
文件名: tests/fixtures/1045.txt, 编码: gb18030
文件名: tests/fixtures/10.txt, 编码: gb18030
文件名: tests/fixtures/test2.txt, 编码: unknow
文件名: tests/fixtures/test3.txt, 编码: unknow
文件名: tests/fixtures/test.txt, 编码: utf_8
文件名: tests/fixtures/18.txt, 编码: utf_8
总文件数: 8
总耗时长: 0.5920612812042236

```