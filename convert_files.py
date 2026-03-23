#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
请假管理系统 - Windows到Linux文件转换工具
功能: 转换行尾符、编码格式等
"""

import os
import sys
import argparse
from pathlib import Path
import chardet

class FileConverter:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.stats = {
            'converted': 0,
            'skipped': 0,
            'errors': 0
        }
    
    def log(self, msg, level='INFO'):
        if self.verbose or level == 'ERROR':
            print(f"[{level}] {msg}")
    
    def convert_line_endings(self, filepath):
        """转换行尾符从CRLF到LF"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            
            # 检测当前行尾类型
            has_crlf = b'\r\n' in content
            has_lf = b'\n' in content and not has_crlf
            
            if has_crlf:
                # 转换CRLF到LF
                new_content = content.replace(b'\r\n', b'\n')
                with open(filepath, 'wb') as f:
                    f.write(new_content)
                self.log(f"已转换行尾: {filepath}")
                self.stats['converted'] += 1
                return True
            else:
                self.log(f"已是LF格式: {filepath}")
                self.stats['skipped'] += 1
                return False
        
        except Exception as e:
            self.log(f"转换失败 {filepath}: {e}", 'ERROR')
            self.stats['errors'] += 1
            return False
    
    def convert_encoding(self, filepath, target_encoding='utf-8'):
        """转换文件编码"""
        try:
            # 检测当前编码
            with open(filepath, 'rb') as f:
                raw_data = f.read()
            
            detected = chardet.detect(raw_data)
            current_encoding = detected.get('encoding', 'utf-8')
            
            if current_encoding.lower() == target_encoding.lower():
                self.log(f"已是{target_encoding}编码: {filepath}")
                self.stats['skipped'] += 1
                return False
            
            # 转换编码
            try:
                content = raw_data.decode(current_encoding)
                with open(filepath, 'w', encoding=target_encoding) as f:
                    f.write(content)
                self.log(f"已转换编码 {current_encoding} -> {target_encoding}: {filepath}")
                self.stats['converted'] += 1
                return True
            except (UnicodeDecodeError, LookupError):
                # 如果解码失败，尝试用GBK
                try:
                    content = raw_data.decode('gbk')
                    with open(filepath, 'w', encoding=target_encoding) as f:
                        f.write(content)
                    self.log(f"已转换编码 GBK -> {target_encoding}: {filepath}")
                    self.stats['converted'] += 1
                    return True
                except:
                    self.log(f"编码转换失败: {filepath}", 'ERROR')
                    self.stats['errors'] += 1
                    return False
        
        except Exception as e:
            self.log(f"处理文件失败 {filepath}: {e}", 'ERROR')
            self.stats['errors'] += 1
            return False
    
    def process_directory(self, directory, patterns=None, line_endings=True, encoding=True):
        """处理目录中的文件"""
        if patterns is None:
            patterns = ['*.py', '*.html', '*.sql', '*.json', '*.md', '*.txt', '.env*']
        
        directory = Path(directory)
        
        if not directory.exists():
            self.log(f"目录不存在: {directory}", 'ERROR')
            return
        
        self.log(f"正在处理目录: {directory}")
        
        for pattern in patterns:
            for filepath in directory.rglob(pattern):
                if filepath.is_file():
                    if line_endings:
                        self.convert_line_endings(filepath)
                    if encoding:
                        self.convert_encoding(filepath)
        
        self.print_stats()
    
    def print_stats(self):
        """打印统计信息"""
        total = sum(self.stats.values())
        print("\n" + "="*50)
        print("转换统计:")
        print(f"  已转换: {self.stats['converted']}")
        print(f"  已跳过: {self.stats['skipped']}")
        print(f"  错误:   {self.stats['errors']}")
        print(f"  总计:   {total}")
        print("="*50)

def main():
    parser = argparse.ArgumentParser(
        description='Windows到Linux文件转换工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 转换当前目录所有Python文件
  python3 convert_files.py .
  
  # 转换指定目录，只修改行尾
  python3 convert_files.py ~/leaves --no-encoding
  
  # 显示详细信息
  python3 convert_files.py ~/leaves -v
  
  # 只转换SQL文件
  python3 convert_files.py ~/leaves --pattern "*.sql"
        """
    )
    
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='要处理的目录（默认: 当前目录）'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细处理信息'
    )
    
    parser.add_argument(
        '--no-line-endings',
        action='store_true',
        help='不转换行尾符'
    )
    
    parser.add_argument(
        '--no-encoding',
        action='store_true',
        help='不转换文件编码'
    )
    
    parser.add_argument(
        '--pattern',
        action='append',
        dest='patterns',
        help='文件匹配模式（可多次指定）'
    )
    
    args = parser.parse_args()
    
    # 创建转换器
    converter = FileConverter(verbose=args.verbose)
    
    # 设置默认模式
    patterns = args.patterns if args.patterns else None
    
    # 处理目录
    converter.process_directory(
        args.directory,
        patterns=patterns,
        line_endings=not args.no_line_endings,
        encoding=not args.no_encoding
    )

if __name__ == '__main__':
    main()

