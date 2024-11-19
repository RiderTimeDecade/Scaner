# Scaner

一个高性能的 Web 目录扫描工具。

## 特性

- 高性能异步扫描
- 智能请求重试
- 自动标题提取
- 实时进度显示
- 自定义并发控制
- 支持自定义字典
- 结果导出功能
- 智能响应分析

## 演示截图

![演示截图](screenshot.png)  <!-- 确保 screenshot.png 文件在同一目录下 -->

## 安装

1. 克隆仓库：
```
git clone https://github.com/RiderTimeDecade/Scaner.git
cd Scaner
```

2. 安装依赖：
```
pip install aiohttp
```

## 使用方法

基本用法：
```
python main.py -u http://example.com -t 50
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| -u, --url | 目标 URL（必需） | - |
| -t, --threads | 并发线程数 | 50 |
| -d, --dict | 字典文件路径 | dic.txt |
| -o, --output | 输出文件路径（JSON） | - |
| --timeout | 请求超时时间（秒） | 10 |

### 示例

1. 基本扫描：
```
python main.py -u http://example.com
```

2. 高并发扫描：
```
python main.py -u http://example.com -t 100
```

3. 使用自定义字典：
```
python main.py -u http://example.com -d custom_dict.txt
```

4. 导出结果：
```
python main.py -u http://example.com -o results.json
```

## 项目结构

```
.
├── README.md           # 项目说明文档
├── main.py            # 主程序入口
├── scanner.py         # 扫描器核心实现
├── dictionary.py      # 字典处理模块
├── dic.txt            # 默认字典文件
├── sensitive.txt      # 敏感路径字典
├── user-agents.txt    # User-Agent 列表
└── screenshot.png      # 演示截图
```

## 注意事项

1. 合理设置并发数
2. 谨慎使用高并发
3. 确保网络稳定

## 免责声明

本工具仅用于安全测试，使用本工具造成的任何后果由使用者自行承担。

## 许可证

MIT License