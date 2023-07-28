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


def print_table(data: list):
    if not data:
        return

    headers = ["from", "to", "origin", "guess"]

    col_widths = [max(len(str(item[col])) for item in data) for col in headers]

    # 格式化字符串，设置每列的对齐方式
    left_aligned_format = " | ".join(
        "{{:<{}}}".format(width) for width in col_widths)

    print(left_aligned_format.format(*headers))
    print('-' * (sum(col_widths) + 3 * (len(col_widths) - 1)))

    # 打印数据行
    for item in data:
        print(left_aligned_format.format(
            item["from"], item["to"], item["origin"], item["guess"]))
