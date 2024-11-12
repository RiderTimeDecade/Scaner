import os
import requests

# 读取用户代理文件
def load_user_agents(file_path):
    """从用户代理文件加载用户代理"""
    try:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def scan_sensitive_files(url, sensitive_terms, user_agents):
    """扫描指定 URL 以查找敏感文件."""
    sensitive_files = []
    
    for term in sensitive_terms:
        # 形成完整的 URL 地址
        full_url = f"{url}/{term}"
        
        try:
            # 从用户代理列表中随机选择一个用户代理
            headers = {
                'User-Agent': user_agents[0]  # 在这里选择实际的用户代理
            }
            # 发起 GET 请求
            response = requests.get(full_url, headers=headers, timeout=1)
            # 检查响应状态码
            if response.status_code == 200:
                sensitive_files.append(full_url)
                print(f"Found sensitive file: {full_url}")
        except requests.RequestException as e:
            pass
    
    return sensitive_files
