# main.py

from dictionary import load_dictionary
from threading_module import thread_scan

def main():
    # 用户输入要扫描的 URL 和字典文件路径
    url = input("Enter the URL to scan for sensitive files (e.g., http://example.com): ").strip()
    
    dict_file = input("Enter the path to the dictionary file (default: dic.txt): ").strip()
    
    # 如果用户没有输入字典文件路径，则使用默认字典文件
    if len(dict_file) == 0:
        dict_file = "dic.txt"
        
    # 加载敏感文件列表
    sensitive_terms = load_dictionary(dict_file)

    if not sensitive_terms:
        #print("No sensitive terms found in the dictionary file.")
        return

    # 执行扫描
    thread_scan(url, sensitive_terms)

if __name__ == "__main__":
    main()
