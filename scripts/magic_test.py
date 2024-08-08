import os
import magic

def scan_dir(folder_path):
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
                # if os.path.splitext(f.name)[1].lower() in ext:
                files.append(f.path)

    for directory in list(sub_folders):
        sf, f = scan_dir(directory)
        sub_folders.extend(sf)

        files.extend(f)
    return sub_folders, files

test_dir = '/Users/alan/Downloads/'
sub_folder, tests_paths = scan_dir(test_dir)

for test_path in tests_paths:
    ret = magic.from_file(test_path)
    if 'text' in ret:
        print(f'{test_path}, a text file')
    else:
        print(f'{test_path}, a binary file')
