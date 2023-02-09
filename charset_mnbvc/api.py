import os
import re

from .constant import (
    REGEX_FEATURE_ALL,
    CHUNK_SIZE,
    ENCODINGS
)


def from_dir(folder_path):
    results = []
    sub_folders, files = scandir(folder_path)
    file_count = 0
    for file_path in files:
        file_count += 1
        coding_name = get_cn_charset(file_path)
        results.append(
            (file_path, coding_name)
        )
    return file_count, results


def scandir(folder_path, ext=".txt"):
    sub_folders, files = [], []
    for f in os.scandir(folder_path):
        if f.is_dir():
            sub_folders.append(f.path)

        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                files.append(f.path)

    for directory in list(sub_folders):
        sf, f = scandir(directory, ext)
        sub_folders.extend(sf)
        files.extend(f)
    return sub_folders, files


def get_cn_charset(file_path):
    try:
        with open(file_path, "rb") as fp:
            data = fp.read(CHUNK_SIZE)
            if not data:
                return False

            # convert coding
            converted_info = {
                encoding: data.decode(encoding=encoding, errors="ignore")
                for encoding in ENCODINGS
            }

            # regex match
            final_encodings = [
                k
                for k, v in converted_info.items() if re.findall(REGEX_FEATURE_ALL, v)
            ]

            # returns the match condition
            if final_encodings:
                return final_encodings
    except Exception as e:
        print(e)
        return None
    return None