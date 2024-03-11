# -*- coding:utf-8 -*
"""
@Time ： 2024/3/11 16:04
@Auth ： Lingeo
"""
import multiprocessing as mp
import os
import time
from charset_mnbvc import api
import json

# 不满载调用cpu,避免其他进程抢占资源影响结果
cpu_count = os.cpu_count() - 1

case_root = r"E:\BaiduNetdiskDownload\test_case"  # 待测试文本集路径
exclude_list = {'links.txt'}  # 排除的文件
suffix = {".json", ".txt"}  # 测试文本的文件后缀

# 输出文件
cchardect_output = r"cchardect_check.json"
mnbvc_output = r"mnbvc_check.json"


def process(group):
    result = {}
    use_time = 0
    for file, func in group:
        with open(file, "rb") as rf:
            start = time.time()
            codec = func(rf.read())
            use_time += (time.time() - start)
            result[file] = codec
    return result, use_time


def mnbvc_work(total_files: [str]):
    results = dict()
    use_time = 0
    # 多进程任务分组
    group_list = [[] for _ in range(cpu_count)]
    for i, file_path in enumerate(total_files):
        group_list[i % cpu_count].append([file_path, api.check_by_mnbvc])
    pool = mp.Pool(cpu_count)
    total_results = pool.map(process, group_list)
    pool.close()
    pool.join()
    for item_res, item_time in total_results:
        results.update(item_res)
        use_time += item_time
    return results, use_time


def cchardect_work(total_files: [str]):
    results = dict()
    use_time = 0
    # 多进程任务分组
    group_list = [[] for _ in range(cpu_count)]
    for i, file_path in enumerate(total_files):
        group_list[i % cpu_count].append([file_path, api.check_by_cchardect])
    pool = mp.Pool(cpu_count)
    total_results = pool.map(process, group_list)
    pool.close()
    pool.join()
    for item_res, item_time in total_results:
        results.update(item_res)
        use_time += item_time
    return results, use_time


def compare_result():
    with open(mnbvc_output, "r", encoding='utf-8') as rf:
        mnbvc_result = json.load(rf)
    with open(cchardect_output, 'r', encoding='utf-8') as rf:
        cchardect_result = json.load(rf)
    difference = {k: (mnbvc_result[k], cchardect_result[k]) for k in mnbvc_result if
                  mnbvc_result[k] != cchardect_result[k]}
    # 随便打印
    print(difference.values(), len(difference), len(cchardect_result))


def main():
    total_files = []
    # 文件过滤
    for parent, dirs, files in os.walk(case_root):
        if dirs or not files:
            continue
        for file in files:
            if file in exclude_list or os.path.splitext(file)[-1] not in suffix:
                continue
            total_files.append(os.path.join(parent, file))
    mnbvc_result, mnbvc_usetime = mnbvc_work(total_files)
    cchardect_result, cchardect_usetime = cchardect_work(total_files)
    mnbvc_result['use_time'] = mnbvc_usetime
    cchardect_result['use_time'] = cchardect_usetime
    with open(mnbvc_output, "w", encoding="utf-8") as wf:
        json.dump(mnbvc_result, wf)
    with open(cchardect_output, "w", encoding="utf-8") as wf:
        json.dump(cchardect_result, wf)


if __name__ == '__main__':
    main()
    compare_result()
