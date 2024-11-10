# scanner.py

import os
import requests

def scan_sensitive_files(url, sensitive_terms):
    """扫描指定 URL 以查找敏感文件."""
    sensitive_files = []
    
    for term in sensitive_terms:
        # 形成完整的 URL 地址
        full_url = f"{url}/{term}"
        
        try:
            # 发起 GET 请求
            response = requests.get(full_url)

            # 检查响应状态码
            if response.status_code == 200:
                sensitive_files.append(full_url)
                print(f"Found sensitive file: {full_url}")
        except requests.RequestException as e:
            pass
            #print(f"Error accessing {full_url}: {e}")
    
    return sensitive_files
