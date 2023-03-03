import os
from re import compile

import cchardet
import tqdm

from .constant import (
    REGEX_FEATURE_ALL,
    CHUNK_SIZE,
    ENCODINGS,
    CCHARDECT_ENCODING_MAP
)


# compile makes it more efficient
re_char_check = compile(REGEX_FEATURE_ALL)


def from_dir(folder_path, mode):
    results = []
    sub_folders, files = scan_dir(folder_path)
    file_count = len(files)
    for idx in tqdm.tqdm(range(file_count), "编码检测进度"):
        file_path = files[idx]
        coding_name = get_cn_charset(file_path, mode=mode)
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
    coding = cchardet.detect(data).get("encoding")
    converted_coding = CCHARDECT_ENCODING_MAP.get(coding)
    if not converted_coding:
        converted_coding = coding
    return [converted_coding]


def get_cn_charset(file_path, mode=1):
    final_encodings = []
    try:
        with open(file_path, 'rb') as fp:
            data = fp.read(CHUNK_SIZE)
            if not data:
                return False

            if mode == 1:
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

                if len(final_encodings) > 1 and 'gb18030' not in final_encodings:
                    final_encodings = check_by_cchardect(data=data)

                # returns the match condition
                if not final_encodings:
                    # try to use cchardet if the normal decoding does not work
                    final_encodings = check_by_cchardect(data=data)

                if 'gb18030' in final_encodings:
                    final_encodings = ['gb18030']
            else:
                final_encodings = check_by_cchardect(data=data)

    except Exception as e:
        print(e)

    return final_encodings
