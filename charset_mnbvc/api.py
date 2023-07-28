import os
import sys
import re
from re import compile

import cchardet
import tqdm

from .constant import (
    REGEX_FEATURE_ALL,
    REGEX_FEATURE,
    CHUNK_SIZE,
    ENCODINGS,
    EXT_ENCODING,
    CCHARDECT_ENCODING_MAP
)

from .common_utils import (
    print_table
)

# compile makes it more efficient
re_char_check = compile(REGEX_FEATURE_ALL)


def has_control_characters(text):
    """
    :param text: text
    :return: bool
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
            fixed_text = guess_text.decode(encoding=target, errors='replace')
            dic = {"origin": s, "guess": fixed_text, "from": item, "to": target}
            result.append(dic)
    print_table(result)
    return result


def from_data(data, mode) -> str:
    """
    :param data: data
    :param mode: 1: use mnbvc, 2: use cchardet
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


def check_by_cchardect(data):
    """
    :param data: data
    :return: encoding
    """
    encoding = cchardet.detect(data).get("encoding")

    converted_encoding = CCHARDECT_ENCODING_MAP.get(encoding)

    # if the encoding is not in the list, try to use utf-8 to decode
    if converted_encoding in ["ascii", "windows_1252", "utf_8"]:
        try:
            ret = data.decode("utf-8")
            if ret:
                converted_encoding = "utf_8"
        except Exception as err:
            converted_encoding = converted_encoding

    return converted_encoding


def check_by_mnbvc(data):
    """
    :param data: data
    :return: encoding
    """
    final_encoding = None
    # convert coding
    converted_info = {
        encoding: data.decode(encoding=encoding, errors='ignore')
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

    if len(final_encodings) > 1:
        if "utf_8" in final_encodings:
            final_encoding = "utf_8"

        if "utf_16" in final_encodings:
            final_encoding = "utf_16"
    else:
        final_encoding = final_encodings[0]

    return final_encoding


def get_cn_charset(source_data, source_type="file", mode=1):
    """
    :param source_data: file path
    :param mode: 1: use mnbvc, 2: use cchardet
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

            if 'ufffd' in data.decode().encode("unicode_escape").decode():
                return "UNKNOWN"

            # 内容是否包含 unicode控制符
            # if has_control_characters(data.decode("unicode_escape")):
            #     return "UNKNOWN"

        except Exception as err:
            pass

        encoding = check_by_mnbvc(
            data=data) if mode == 1 else check_by_cchardect(data=data)

    except Exception as err:
        sys.stderr.write(f"Error: {str(err)}\n")

    return encoding


def convert_encoding(source_data, source_encoding, target_encoding="utf-8"):
    """
    :param source_data: data
    :param source_encoding: input encoding
    :param target_encoding: output encoding
    :return: data
    """
    try:
        data = source_data.decode(encoding=source_encoding)
        data = data.encode(encoding=target_encoding).decode(
            encoding=target_encoding)
    except Exception as err:
        if source_encoding == "big5":
            try:
                source_encoding = "cp950"
                data = source_data.decode(encoding=source_encoding)
                data = data.encode(encoding=target_encoding).decode(
                    encoding=target_encoding)
            except Exception as err:
                sys.stderr.write(f"Error: {str(err)}\n")
                data = source_data
        else:
            sys.stderr.write(f"Error: {str(err)}\n")
            data = source_data

    return data


def test():
    print("test")
