import os

def read_files(dir_path):
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)
        if os.path.isdir(file_path):
            read_files(file_path)
        elif file_name.endswith('.txt'):
            try:
                with open(file_path, encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                # 编码错误的文件名(非utf-8编码)
                print(f"{file_name}, {e}")

read_files('/Users/alan/temp_test/20230108')