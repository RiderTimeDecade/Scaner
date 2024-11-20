# main.py
# Author: RiderTimeDecade

import asyncio
import argparse
import sys
from scanner.scanner import AsyncScanner
from dictionary.dictionary import Dictionary
from datetime import datetime
import json

class ScannerCLI:
    def __init__(self):
        self.parser = self.setup_argument_parser()

    def setup_argument_parser(self):
        parser = argparse.ArgumentParser(description='Advanced Web Directory Scanner')
        parser.add_argument('-u', '--url', required=True, help='Target URL')
        parser.add_argument('-t', '--threads', type=int, default=50, help='Number of concurrent requests')
        parser.add_argument('-d', '--dict', default='dictionary/dic.txt', help='Dictionary file path')
        parser.add_argument('-o', '--output', help='Output file path (JSON format)')
        parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds')
        return parser

    def save_results(self, results, output_file):
        """保存扫描结果到文件"""
        output_data = {
            'scan_time': datetime.now().isoformat(),
            'results': [
                {
                    'url': r.url,
                    'status': r.status,
                    'length': r.length,
                    'response_time': r.response_time,
                    'title': r.title,
                    'error': r.error
                } for r in results
            ]
        }
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

async def main():
    cli = ScannerCLI()
    args = cli.parser.parse_args()

    try:
        # 初始化字典
        dictionary = Dictionary(args.dict)
        urls = list(dictionary.generate_urls(args.url))

        if not urls:
            print("Error: No URLs generated from dictionary")
            sys.exit(1)
        
        # 初始化扫描器
        scanner = AsyncScanner(
            urls=urls,
            concurrency=args.threads,
            timeout=args.timeout
        )
        
        # 执行扫描
        results = await scanner.scan_all()
        
        # 保存结果（如果指定了输出文件）
        if args.output:
            cli.save_results(results, args.output)

    except KeyboardInterrupt:
        print("\nScan interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
