# -*- coding:utf-8 -*
"""
@Time ： 2024/1/13 12:21
@Auth ： Lingeo
api使用过程中发现的bug需要记录下来，并添加相应的测试用例。
后续修复bug或新增api都需要通过单元测试后才可以发布。
"""
import unittest
from charset_mnbvc import api


class TestAPI(unittest.TestCase):

    def test_is_perceivable(self):
        case = "两个意达\r\n作者：松谷美代子"
        self.assertTrue(api.is_perceivable(case))
        case = b"\xc1\xbd\x00\xd7\xf7".decode("gbk")
        self.assertEqual(str, type(api.is_perceivable(case)))

    def test_has_control_characters(self):
        case = "两个意达\r\n作者：松谷美代子".encode("unicode_escape").decode()
        self.assertFalse(api.has_control_characters(case))

    def test_check_by_cchardect(self):  # 函数待优化
        pass

    def test_check_by_mnbvc(self):
        pass

    def test_check_disorder_chars(self):
        pass

    def test_get_cn_charset(self):
        pass

    def test_convert_encoding(self):
        case = "松谷美代子".encode("gbk")
        self.assertEqual(api.convert_encoding(case, "gbk", "utf-8").encode("utf-8"), "松谷美代子".encode("utf-8"))
        case = "碁恒".encode("cp950")
        self.assertEqual(api.convert_encoding(case, "big5").encode("cp950"), "碁恒".encode("cp950"))

    def test_decode_check(self):
        with self.assertRaises(UnicodeDecodeError) as context:
            case = b'\xc1\xbd\xb8\xf6\xd2\xe2\xb4\xef\r\n\xd7\xf7\xd5\xdf\xa3\xba\xcb\xc9\xb9\xc8\xc3\xc0\xb4' \
                   b'\xfa\xd7\xd3\xa3\xa0\xa3\xa0'
            encoding = "gbk"
            api.decode_check(case, encoding)
        self.assertEqual(context.exception.start, 26)
        self.assertEqual(context.exception.end, 27)
        self.assertEqual(context.exception.object, b'\xa3')
        # 通过异常提示异常字节索引截取正常字节再进行解码测试
        result = api.decode_check(case[:context.exception.start], encoding)
        self.assertEqual(result, "两个意达\r\n作者：松谷美代子")


if __name__ == '__main__':
    unittest.main()
