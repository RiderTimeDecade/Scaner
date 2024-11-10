# threading_module.py

import threading
from scanner import scan_sensitive_files

def thread_scan(directory, sensitive_terms, max_threads=5):
    """为每个敏感文件扩展名创建线程进行扫描，最多同时运行 max_threads 个线程"""
    threads = []
    active_threads = 0
    
    # 在每个文件扩展名或名称上创建线程
    for term in sensitive_terms:
        t = threading.Thread(target=scan_sensitive_files, args=(directory, [term]))
        threads.append(t)
        
        # 启动线程并增加活动线程计数
        t.start()
        active_threads += 1

        # 如果活动线程数达到最大线程数，则等待任意一个线程完成
        if active_threads >= max_threads:
            for t in threads:
                t.join()  # 等待所有线程完成
            threads = []  # 清空线程列表
            active_threads = 0  # 重置活动线程计数

    # 等待最后剩余的线程完成
    for t in threads:
        t.join()
