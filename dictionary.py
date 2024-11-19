# dictionary.py

from typing import Generator, Set
from pathlib import Path
import re
from urllib.parse import urljoin

class Dictionary:
    def __init__(self, dict_path: str):
        self.dict_path = Path(dict_path)
        self.processed_paths: Set[str] = set()

    def load_dict(self) -> Generator[str, None, None]:
        """使用生成器加载字典，避免一次性加载全部内容到内存"""
        try:
            # 使用缓冲读取
            with open(self.dict_path, 'r', encoding='utf-8', buffering=8192) as f:
                seen = set()  # 用于去重
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        path = self.normalize_path(line)
                        if path and path not in seen:
                            seen.add(path)
                            yield path
        except UnicodeDecodeError:
            with open(self.dict_path, 'r', encoding='latin-1', buffering=8192) as f:
                seen = set()
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        path = self.normalize_path(line)
                        if path and path not in seen:
                            seen.add(path)
                            yield path

    def normalize_path(self, path: str) -> str:
        """规范化路径"""
        # 移除首尾的斜杠
        path = path.strip('/')
        # 移除多余的斜杠
        path = re.sub(r'/+', '/', path)
        # 移除不安全的字符
        path = re.sub(r'[\s<>"|*?]', '', path)
        return path

    def generate_urls(self, base_url: str) -> Generator[str, None, None]:
        """生成完整的URL"""
        base_url = base_url.rstrip('/')
        for path in self.load_dict():
            # 使用urljoin来正确处理URL拼接
            yield urljoin(base_url + '/', path)
