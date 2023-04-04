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

目前存在的问题:

1. cchardect 误报问题
    * 比如原本是gbk的可能会检测为ibm852 例如 20230102/aliyun.20230102.1.网络小说/35.txt(通过调整CHUNK_SIZE大小解决，文章开头包含大量英文或特殊字符容易被cchardet检测为其他编码格式)
    * 原本是gbk的可能会检测为utf-8 20230101/aliyun.20230101.6.网络小说/48.txt，其内容均为乱码，需要经过特殊处理才能检测为gb18030 (api.py 74行开始到85行)


```
     data.decode("gbk", errors="ignore")
'y==========================================================\r\n锟斤拷锟洁精校小说锟斤拷锟斤拷知锟斤拷锟斤拷锟斤拷锟斤拷锟截ｏ拷\r\n==========================================================\r\n1895锟皆斤拷锟斤拷锟 锟斤拷锟竭ｏ拷锟斤拷锟\r\n\r\n锟斤拷锟捷硷拷椋\r\n锟斤拷锟斤拷锟斤拷牛锟绞憋拷瞬锟斤拷茫锟斤拷锟斤拷洗锟皆斤拷锟斤拷锟斤拷锟饺达拷锟斤拷锟斤拷嗪之锟截★拷\r\n锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷锟斤拷贫锟斤拷锟竭讹拷远锟斤拷锟斤拷锟襟，达拷拼锟斤拷锟斤拷锟斤拷锟斤拷纭\r\n锟斤拷锟斤拷锟斤拷'
```


2. GB18030/GBK 与CP936兼容性问题，导致使用已检测的编码格式打开这段内容时出错，可以用errors="ignore" 跳过，但跳过这段内容会出现数据遗失。数据文件范例 224.txt, https://pan.baidu.com/s/1gBVBxv_WGie6W6hCIZxTXQ 提取码: stfs

经过测试,初步发现原因是因为GB18030和cp936，ms936几种编码格式在Python具体实现造成的。
以224.txt文件中出现的乱码情况为里，其出错的位置是2753行 的这部分内容 `"100～120RMB/80～90$/65～70?左右"` 这个?号原本应该是一个欧元符号€，但当Python代码用GB18030编码对该文件内容进行decode处理时，在这个欧元符号处就会到了解析错误。

通常情况下在Windows中简体中文用的是CP936代码页使用0x80来表示欧元符号，而在GB18030编码中没有使用0x80编码位来表示欧元符号。

以下是微软对这个问题的详细解释：

```
What is GB18030?
GB18030–2000 is a new Chinese character encoding standard. The standard contains many characters and has some tough new conformance requirements. GB18030-2000 encodes characters in sequences of one, two, or four bytes. These sequences are defined as follows:

 Single-byte: 00-0x7f
 Two-byte: 0x81-0xfe + 0x40-0x7e, 0x80-0xfe
 Four-byte: 0x81-0xfe + 0x30-0x39 + 0x81-0xfe + 0x30-0x39
The single-byte section applies the standard GB 11383 coding structure and principles by using the code points 0x00 through 0x7f. GB 11383 is identical to ISO 4873:1986

The two-byte section uses two eight-bit sequences -- much in the same manner as most DBCS (double-byte character sets) do -- to express a character. The leading byte code points range from 0x81 through 0xfe. The trailing byte code points ranges from 0x40 through 0x7e and 0x80 through 0xfe. This section has the same problem as most DBCS in as much as some code points can be either a leading or trailing byte, thus making character delimitation more complicated.

The four-byte section uses the code points 0x30 through 0x39 as a way to extend the two-byte encodings. Which means the four-byte code points range from 0x81308130 through 0xfe39fe39.

Is GB18030 replacing the Windows Simplified Chinese code page (CP936)?
No, Windows code pages must be either one byte (SBCS) or a mix of one and two bytes (DBCS). This requirement is reflected throughout our code e.g. in data structures, program interfaces, network protocols and applications. The existing code page for Simplified Chinese, CP936, is a double byte code page. GB18030 is a four–byte code page i.e. every character is represented by one, two or four bytes. To replace CP936 with GB18030 would require rewriting much of the system. Even if we were to do this, such a system would not run regular applications nor interoperate with regular Windows.
```


解决这个问题最简单的方式就是使用MS936来处理这种有问题的文件(Windows Code page 936 (abbreviated MS936, Windows-936 or (ambiguously) CP936))。不过遗憾的是Python语言暂时没有独立支持MS936或者CP936，而是把它们统一作为GBK处理了。https://docs.python.org/3/library/codecs.html。
因此目前单纯使用Python对文件内容进行decode无法正确处理这些特殊符号。

最后我用Java写了一段代码验证，可以顺利的用MS936解析出文件中的欧元符号。
![iZAjIJ.png](https://i.328888.xyz/2023/03/23/iZAjIJ.png)


```
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.Charset;

public class TextFileReader {
    public static void main(String[] argsm) {
        String filePath = "/Users/alan/Downloads/test/224.txt";
        String charsetName = "MS936";
        try {
            String fileContent = readTextFile(filePath, charsetName);
            System.out.println(fileContent);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static String readTextFile(String filePath, String charsetName) throws IOException {
        File file = new File(filePath);
        StringBuilder sb = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(new FileInputStream(file), Charset.forName(charsetName)))) {
            String line;
            while ((line = reader.readLine()) != null) {
                sb.append(line).append(System.lineSeparator());
            }
        }
        return sb.toString();
    }
}
```


现在解决这个问题的最简单的思路是换一种语言实现编码转换或者在Python中引入Java的库对MS936编码进行正确处理。





