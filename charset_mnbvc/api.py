import os
import re
import sys
from re import compile

import cchardet
import tqdm

from .common_utils import print_table
from .constant import (CCHARDECT_ENCODING_MAP, ENCODINGS, EXT_ENCODING,
                       REGEX_FEATURE_ALL, TIPS_CONTEXT_RANGE, MAX_INVALID_BYTES_SIZE)

# compile makes it more efficient
re_char_check = compile(REGEX_FEATURE_ALL)


def is_perceivable(s: str):
    """
    Checks if all characters in a string are perceivable by the user.
    Perceivable characters include printable characters, spaces, tabs, and newlines.

    Args:
    s (str): The string to check.

    Returns:
    bool: True if all characters are perceivable, False otherwise.
    """
    for char in s:
        # Check if the character is not perceivable
        if not (char.isprintable() or char in [' ', '\t', '\n']):
            return decode(char.encode('unicode_escape'))
    return True


def has_control_characters(text: str):
    """
    :param text: text
    :return: bool
    :ref: https://www.fileformat.info/info/unicode/category/Cc/list.htm
    """
    pattern = r'[\u0000-\u001f\u007f-\u009f]'
    match = re.search(pattern, text)
    return match is not None


def fix_data(s: str) -> list:
    """
    :param s: text
    :return: list
    """

    result = []

    for item in EXT_ENCODING:
        guess_text = s.encode(encoding=item, errors='replace')
        for target in EXT_ENCODING:
            if item == target:
                continue
            fixed_text = decode(guess_text, encoding=target, errors='replace')
            dic = {"origin": s, "guess": fixed_text,
                   "from": item, "to": target}
            result.append(dic)
    print_table(result)
    return result


def from_data(data, mode) -> str:
    """
    :param data: data
    :param mode: 1:cchardet 2:mnbvc
    :return: encoding
    """
    coding_name = get_cn_charset(
        source_data=data, mode=mode, source_type="data")
    return coding_name


def from_file(file_path, mode):
    """
    :param file_path: file path
    :param mode: 1: use mnbvc, 2: use cchardet
    :return: encoding
    """
    coding_name = get_cn_charset(
        source_data=file_path, mode=mode, source_type="file")
    return file_path, coding_name


def from_dir(folder_path, mode):
    """
    :param folder_path: folder path
    :param mode: 1: use mnbvc, 2: use cchardet
    :return: array
    """
    results = []
    sub_folders, files = scan_dir(folder_path)
    file_count = len(files)
    for idx in tqdm.tqdm(range(file_count), "编码检测进度"):
        file_path = files[idx]

        coding_name = get_cn_charset(
            source_data=file_path, mode=mode, source_type="file")
        if not coding_name:
            coding_name = "None"

        results.append(
            (file_path, coding_name)
        )

    return file_count, results


def scan_dir(folder_path, ext='.txt'):
    """
    :param folder_path: folder path
    :param ext: file extension
    :return: array
    """
    sub_folders, files = [], []
    for f in os.scandir(folder_path):
        if f.is_dir():
            sub_folders.append(f.path)

        if f.is_file():
            if os.path.splitext(f.name)[1] != "":
                if os.path.splitext(f.name)[1].lower() in ext:
                    files.append(f.path)

    for directory in list(sub_folders):
        sf, f = scan_dir(directory, ext)
        sub_folders.extend(sf)
        files.extend(f)
    return sub_folders, files


# def check_by_icu(data):
#     """
#     :param data:data
#     :return: encoding
#     """
#     encoding = icu.CharsetDetector(data).detect().getName()

#     converted_encoding = CCHARDECT_ENCODING_MAP.get(encoding)

#     return converted_encoding


def check_by_cchardect(data: bytes):
    """
    :param data: data
    :return: encoding
    """
    encoding = cchardet.detect(data).get("encoding")

    converted_encoding = CCHARDECT_ENCODING_MAP.get(encoding)

    # if the encoding is not in the list, try to use utf-8 to decode
    if converted_encoding in ["ascii", "windows_1252", "utf_8"]:
        try:
            ret = decode(data, "utf-8")
            if ret:
                converted_encoding = "utf_8"
        except Exception as err:
            converted_encoding = converted_encoding

    return converted_encoding


def check_by_mnbvc(data: bytes, special_encodings=None):
    """
    :param data: data
    :return: encoding
    """
    final_encoding = None
    # convert coding
    converted_info = {
        encoding: decode(data, encoding=encoding, errors='ignore')
        for encoding in ENCODINGS
    }

    # regex match
    final_encodings = [
        k
        for k, v in converted_info.items() if re_char_check.findall(v)
    ]

    # returns the match condition
    if not final_encodings:
        # try to use cchardet if the normal decoding does not work
        final_encodings = [check_by_cchardect(data=data)]

    if special_encodings:
        lower_special_encodings = [x.lower() for x in special_encodings]
        final_encodings = list(set(final_encodings) &
                               set(lower_special_encodings))

    final_encoding = final_encodings[0] if final_encodings else None
    return final_encoding


def check_disorder_chars(file_path: str, threshold=0.1):
    """
    :param file_path: file_path
    :param threshold: threshold
    :return: bool
    """
    with open(file_path, 'rb') as fp:
        data = fp.read()

    total_chars = len(data)
    disorder_chars = decode(decode(data).encode("unicode_escape")).count('ufffd')
    ratio = disorder_chars / total_chars
    return ratio >= threshold, ratio


def get_cn_charset(source_data: str, source_type="file", mode=1, special_encodings=None):
    """
    :param source_data: file path
    :param mode: 1: mnbvc, 2: cchardet
    :param source_type: file or data
    :return: encoding
    """
    encoding = None
    try:
        data = ""
        if source_type == "file":
            with open(source_data, 'rb') as fp:
                data = fp.read()

                if not data:
                    return None
        else:
            data = source_data

        try:

            # 内容中是否包含 null 字符（二进制文件通常包含 null 字符）
            # if b'\x00' in data:
            #     return None

            if 'ufffd' in decode(decode(data).encode("unicode_escape")):
                return "UNKNOWN"

            # 内容是否包含 unicode控制符
            # if has_control_characters(data.decode("unicode_escape")):
            #     return "UNKNOWN"

            # return_is_perceivable = is_perceivable(data.decode("unicode_escape"))
            # if not return_is_perceivable:
            #     return "UNKNOWN: %s" % return_is_perceivable

        except Exception as err:
            pass

        if mode == 1:
            encoding = check_by_mnbvc(
                data=data, special_encodings=special_encodings)
        elif mode == 2:
            encoding = check_by_cchardect(data=data)
        else:
            sys.stderr.write(f'Error: mode {mode} is not supported.')

    except Exception as err:
        sys.stderr.write(f"Error: {str(err)}\n")

    return encoding


def convert_encoding(source_data: bytes, source_encoding, target_encoding="utf-8") -> str:
    """
    :param source_data: data
    :param source_encoding: input encoding
    :param target_encoding: output encoding
    :return: data
    """
    try:
        data = decode(source_data, source_encoding)
        data = decode(data.encode(encoding=target_encoding), target_encoding)
    except Exception as err:
        if source_encoding == "big5":
            try:
                source_encoding = "cp950"
                data = decode(source_data, source_encoding)
                data = decode(data.encode(encoding=target_encoding), target_encoding)
            except Exception as err:
                sys.stderr.write(f"Error: {str(err)}\n")
                data = source_data
        else:
            sys.stderr.write(f"Error: {str(err)}\n")
            data = source_data

    return data


def decode(byte_sequence: bytes, encoding='utf-8', errors='strict') -> str:
    """
    :param byte_sequence: input bytes
    :param encoding: input encoding
    :param errors: passed to bytes.decode()
    :return: decoded characters
    """
    try:
        decode_data = byte_sequence.decode(encoding, errors)
        return decode_data
    except UnicodeDecodeError as e:
        # 解码左侧有效字符
        e.object = byte_sequence[e.start:e.end]
        left_chars = byte_sequence[:e.start].decode(encoding)[TIPS_CONTEXT_RANGE * -1:]
        max_scan_bytes_size = min(MAX_INVALID_BYTES_SIZE, len(byte_sequence) - e.end)
        # 解码右侧有效字符
        for i in range(max_scan_bytes_size):
            try:
                right_chars = byte_sequence[e.end + i:].decode(encoding)[:TIPS_CONTEXT_RANGE]
                break
            except UnicodeDecodeError as right_e:
                if not right_e.start:
                    e.object += byte_sequence[e.end + i:e.end + i + 1]
                    e.end = e.start + len(e.object)
                else:
                    right_chars = byte_sequence[e.end + i:e.end + i + right_e.start].decode(encoding)[
                                  :TIPS_CONTEXT_RANGE]
                    break
        else:  # 超过最大异常字节数，提示更换解码方式
            e.reason = "There are too many invalid bytes, please change codec."
            raise e
        # 格式化非法字节输出
        invalid_str = "\\x" + '\\x'.join([hex(b)[2:].zfill(2) for b in e.object])
        e.reason = f"There are invalid bytes in the string \"{left_chars + invalid_str + right_chars}\""
        raise e


def test():
    print("test")
