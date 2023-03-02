# read file in chunks
CHUNK_SIZE = 500

# 正则判断中文标点符号,标点符号包含 。 ； ， ： “ ”（ ） 、 ？ 《 》 空格
REGEX_FEATURE = r'[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u3000]'

# 正则判断中文标点符号和常见汉字,标点符号包含 。 ； ， ： “ ”（ ） 、 ？ 《 》 空格
# 常见汉字包含 的一是不了在人有我他这个们中来上大为和国地到以说时要就出会可也你对生
REGEX_FEATURE_ALL = r'[\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b\u3000' \
                    r'\u7684\u4e00\u662f\u4e0d\u4e86\u5728\u4eba\u6709\u6211\u4ed6\u8fd9\u4e2a\u4eec' \
                    r'\u4e2d\u6765\u4e0a\u5927\u4e3a\u548c\u56fd\u5730\u5230\u4ee5\u8bf4\u65f6\u8981' \
                    r'\u5c31\u51fa\u4f1a\u53ef\u4e5f\u4f60\u5bf9\u751f\u80fd\u800c\u5b50\u90a3\u5f97' \
                    r'\u4e8e\u7740\u4e0b\u81ea\u4e4b\u5e74\u8fc7\u53d1\u540e\u4f5c\u91cc\u7528\u9053' \
                    r'\u884c\u6240\u7136\u5bb6\u79cd\u4e8b\u6210\u65b9\u591a\u7ecf\u4e48\u53bb\u6cd5' \
                    r'\u5b66\u5982\u90fd\u540c\u73b0\u5f53\u6ca1\u52a8\u9762\u8d77\u770b\u5b9a\u5929' \
                    r'\u5206\u8fd8\u8fdb\u597d\u5c0f\u90e8\u5176\u4e9b\u4e3b\u6837\u7406\u5fc3\u5979' \
                    r'\u672c\u524d\u5f00\u4f46\u56e0\u53ea\u4ece\u60f3\u5b9e]'

ENCODINGS = [
    'utf_8',
    'utf_16',
    'gb18030',
    'big5',
]

CCHARDECT_ENCODING_MAP = {
    "BIG5": "big5",
    "UTF-8": "utf_8",
    "UTF-8-SIG": "utf_8",
    "UTF-16BE": "utf_16",
    "UTF-16LE": "utf_16",
    "GB18030": "gb18030",
}
