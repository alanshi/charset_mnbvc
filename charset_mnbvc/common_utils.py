import os


def get_file_paths(dir_path, suffix='.txt'):
    """
    获取文件夹下所有文件路径
    """
    file_paths = []
    for root, dirs, files in os.walk(dir_path):
        for f in files:
            if f.endswith(suffix):
                file_paths.append(os.path.join(root, f))
    return file_paths


if __name__ == '__main__':
    dir_path = '/Users/alan/databak/mop'
    file_paths = get_file_paths(dir_path)
    print(file_paths)