import os
from re import compile

import cchardet
import tqdm

from .constant import (
    REGEX_FEATURE_ALL,
    REGEX_FEATURE,
    CHUNK_SIZE,
    ENCODINGS,
    CCHARDECT_ENCODING_MAP
)


# compile makes it more efficient
re_char_check = compile(REGEX_FEATURE_ALL)


def from_file(file_path, mode):
    coding_name = get_cn_charset(file_path, mode=mode)
    return file_path, coding_name


def from_dir(folder_path, mode):
    results = []
    sub_folders, files = scan_dir(folder_path)
    file_count = len(files)
    for idx in tqdm.tqdm(range(file_count), "编码检测进度"):
        file_path = files[idx]

        coding_name = get_cn_charset(file_path, mode=mode)
        if not coding_name:
            coding_name = "None"

        results.append(
            (file_path, coding_name)
        )

    return file_count, results


def scan_dir(folder_path, ext='.txt'):
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
    encoding = cchardet.detect(data).get("encoding")

    converted_encoding = CCHARDECT_ENCODING_MAP.get(encoding)

    # if the encoding is not in the list, try to use utf-8 to decode
    if converted_encoding in ["ascii", "windows_1252", "utf_8"]:
        try:
            ret = data.decode("utf-8")
            if ret:
                converted_encoding = "utf_8"
        except Exception as e:
            converted_encoding = converted_encoding

    return converted_encoding


def check_by_mnbvc(data):
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


def get_cn_charset(file_path, mode=1):
    try:
        with open(file_path, 'rb') as fp:
            data = fp.read()
            if not data:
                return None

            if mode == 1:
                final_encoding = check_by_mnbvc(data=data)
            else:
                final_encoding = check_by_cchardect(data=data)

    except Exception as e:
        final_encoding = None
        print(e)

    return final_encoding
