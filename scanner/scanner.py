import aiohttp
import asyncio
from typing import List, Dict, Optional
import random
import time
from dataclasses import dataclass
from aiohttp import ClientTimeout
import logging
import re
from asyncio import Queue

@dataclass
class ScanResult:
    url: str
    status: int
    length: int
    response_time: float
    title: Optional[str] = None
    error: Optional[str] = None
    flag_found: bool = False

class AsyncScanner:
    def __init__(self, urls: List[str], concurrency: int = 100, timeout: int = 10):
        self.urls = urls
        self.concurrency = concurrency
        self.timeout = ClientTimeout(total=timeout)
        self.session = None
        self.results = []
        self.request_manager = RequestManager()
        self.total_requests = len(urls)
        self.completed_requests = 0
        self.start_time = None
        self.queue = Queue()
        self.retry_count = 2  # 重试次数
        self.last_update_time = 0
        self.update_interval = 0.1  # 更新间隔（秒）
        
    async def init_session(self):
        # 优化连接池设置
        connector = aiohttp.TCPConnector(
            limit=self.concurrency,
            ttl_dns_cache=300,
            ssl=False,
            force_close=False,  # 保持连接复用
            enable_cleanup_closed=True,  # 自动清理关闭的连接
            keepalive_timeout=60  # 保持连接活跃时间
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout,
            headers=self.request_manager.generate_headers()
        )
        self.start_time = time.time()
        
        # 将所有URL加入队列
        for url in self.urls:
            await self.queue.put(url)

    async def extract_title(self, text: str) -> Optional[str]:
        """从HTML响应中提取标题"""
        try:
            import re
            title_match = re.search(r'<title>(.*?)</title>', text, re.I)
            return title_match.group(1) if title_match else None
        except:
            return None

    async def scan_url(self, url: str, retry: int = 0) -> ScanResult:
        start_time = time.time()
        try:
            # 使用HEAD请求先检查资源是否存在
            async with self.session.head(url, allow_redirects=True) as response:
                if response.status == 404:
                    return ScanResult(
                        url=url,
                        status=404,
                        length=0,
                        response_time=time.time() - start_time
                    )
                
                # 对于非404响应，使用GET请求获取完整内容
                async with self.session.get(url, allow_redirects=True) as response:
                    text = await response.text()
                    flag_found = bool(re.search(r'flag{[^}]*}', text, re.I))
                    title = await self.extract_title(text) if response.status == 200 else None
                    
                    result = ScanResult(
                        url=url,
                        status=response.status,
                        length=len(text),
                        response_time=time.time() - start_time,
                        title=title,
                        flag_found=flag_found
                    )
                    
                    if flag_found:
                        print(f"\n[!] Potential flag found at: {url}")
                    
                    return result
                    
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if retry < self.retry_count:
                await asyncio.sleep(1)  # 等待1秒后重试
                return await self.scan_url(url, retry + 1)
            return ScanResult(
                url=url,
                status=0,
                length=0,
                response_time=time.time() - start_time,
                error=str(e)
            )

    # 添加颜色和样式常量
    COLORS = {
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'red': '\033[31m',
        'reset': '\033[0m',
        'bold': '\033[1m',
        'dim': '\033[2m'
    }

    def format_size(self, size: int) -> str:
        """格式化响应大小"""
        for unit in ['B', 'KB', 'MB']:
            if size < 1024:
                return f"{size:.1f}{unit}"
            size /= 1024
        return f"{size:.1f}GB"

    def print_banner(self):
        """打印启动横幅"""
        banner = f"""
{self.COLORS['blue']}{self.COLORS['bold']}
╔══════════════════════════════════════════════╗
║             Web Directory Scanner            ║
╚══════════════════════════════════════════════╝
{self.COLORS['reset']}
[*] Target URLs: {self.total_requests}
[*] Threads: {self.concurrency}
[*] Starting scan...
"""
        print(banner)

    def print_result(self, result: ScanResult):
        """打印单个扫描结果"""
        if not self.should_display_result(result.status):
            return

        # 清除当前进度条
        print('\r' + ' ' * 100 + '\r', end='')

        # 状态码颜色
        if 200 <= result.status < 300:
            status_color = self.COLORS['green']
        else:
            status_color = self.COLORS['yellow']

        # 格式化输出
        status = f"{status_color}[{result.status}]{self.COLORS['reset']}"
        size = f"{self.COLORS['dim']}[{self.format_size(result.length)}]{self.COLORS['reset']}"
        time = f"{self.COLORS['dim']}[{result.response_time:.2f}s]{self.COLORS['reset']}"
        
        # 构建标题部分
        title_part = ""
        if result.title:
            title = result.title[:50] + ('...' if len(result.title) > 50 else '')
            title_part = f" {self.COLORS['blue']}- {title}{self.COLORS['reset']}"

        # 打印结果（不带换行符）
        print(f"{status} {result.url} {size} {time}{title_part}")
        
        # 重新打印进度条
        self.print_progress()

    def print_progress(self):
        """打印进度信息到状态行"""
        current_time = time.time()
        if current_time - self.last_update_time < self.update_interval:
            return

        self.last_update_time = current_time
        elapsed_time = current_time - self.start_time
        progress = (self.completed_requests / self.total_requests) * 100
        req_per_second = self.completed_requests / elapsed_time if elapsed_time > 0 else 0
        
        # 创建进度条
        bar_width = 30
        filled = int(bar_width * progress / 100)
        bar = '█' * filled + '░' * (bar_width - filled)
        
        # 清除当前行并打印进度信息
        print(f"\r{self.COLORS['blue']}[*]{self.COLORS['reset']} "
              f"Progress: {self.COLORS['bold']}{progress:.1f}%{self.COLORS['reset']} "
              f"[{bar}] "
              f"({self.completed_requests}/{self.total_requests}) "
              f"Speed: {self.COLORS['bold']}{req_per_second:.1f}{self.COLORS['reset']} req/s", 
              end='', flush=True)

    def print_summary(self, total_time: float):
        """打印扫描总结"""
        summary = f"""
{self.COLORS['blue']}{self.COLORS['bold']}
╔══════════════════ Summary ══════════════════╗
║{self.COLORS['reset']}
  Total Requests: {self.total_requests}
  Total Time: {total_time:.2f}s
  Average Speed: {self.total_requests/total_time:.1f} req/s
{self.COLORS['blue']}{self.COLORS['bold']}║
╚═════════════════════════════════════════════╝
{self.COLORS['reset']}"""
        print(summary)

    def should_display_result(self, status: int) -> bool:
        """判断是否应该显示该状态码的结果"""
        return 200 <= status < 400

    async def worker(self):
        while True:
            try:
                url = await self.queue.get()
                result = await self.scan_url(url)
                self.results.append(result)
                self.completed_requests += 1
                
                # 只打印2xx和3xx的响应
                if not result.error and self.should_display_result(result.status):
                    self.print_result(result)
                else:
                    self.print_progress()
                
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                #print(f"\nError processing {url}: {str(e)}")
                self.print_progress()

    async def scan_all(self):
        self.print_banner()
        await self.init_session()
        try:
            workers = [asyncio.create_task(self.worker()) 
                      for _ in range(self.concurrency)]
            
            await self.queue.join()
            
            for w in workers:
                w.cancel()
            
            await asyncio.gather(*workers, return_exceptions=True)
            
            # 清除进度行
            print('\033[K', end='')
            print()  # 添加一个空行作为结束
            
            return self.results
            
        finally:
            await self.close()

    async def close(self):
        if self.session:
            await self.session.close()

class RequestManager:
    def __init__(self):
        self.user_agents = self.load_user_agents()

    def load_user_agents(self) -> List[str]:
        try:
            with open('user-agents.txt', 'r') as f:
                return [ua.strip() for ua in f if ua.strip()]
        except FileNotFoundError:
            return ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36']

    def generate_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': random.choice(self.user_agents),
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Cache-Control': 'no-cache'
        }
