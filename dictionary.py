# dictionary.py

def load_dictionary(file_path):
    """从字典文件加载敏感文件扩展名或名称"""
    try:
        with open(file_path, 'r') as f:
            # 去掉每行的空白字符并返回非空行
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        #print(f"Error: The file {file_path} was not found.")
        return []
