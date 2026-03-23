#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
请假管理系统 - Ubuntu部署后健康检查
检查系统各个组件的运行状态
"""

import os
import sys
import subprocess
import socket
import mysql.connector
from mysql.connector import Error
from pathlib import Path

class HealthCheck:
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
    
    def check(self, name, func):
        """执行检查并记录结果"""
        try:
            result = func()
            status = "✓" if result else "✗"
            symbol = "PASS" if result else "FAIL"
            self.results.append((name, status, symbol))
            if result:
                self.passed += 1
            else:
                self.failed += 1
        except Exception as e:
            self.results.append((name, "✗", f"ERROR: {e}"))
            self.failed += 1
    
    def print_results(self):
        """打印检查结果"""
        print("\n" + "="*70)
        print("请假管理系统 - Ubuntu部署健康检查")
        print("="*70 + "\n")
        
        for name, status, result in self.results:
            print(f"{status} {name:.<40} {result}")
        
        print("\n" + "="*70)
        print(f"检查结果: {self.passed} 通过, {self.failed} 失败")
        print("="*70 + "\n")
        
        return self.failed == 0
    
    # 检查函数
    def check_python(self):
        """检查Python版本"""
        version_info = sys.version_info
        if version_info.major >= 3 and version_info.minor >= 8:
            print(f"  Python {sys.version.split()[0]}")
            return True
        return False
    
    def check_mysql_service(self):
        """检查MySQL服务运行状态"""
        try:
            # 优先使用无sudo的systemctl快速检查
            result = subprocess.run(
                ['systemctl', 'is-active', '--quiet', 'mysql'],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                print("  MySQL服务运行正常")
                return True
        except:
            pass
        # 回退：通过端口探测MySQL是否在监听（默认3306或从.env读取）
        try:
            port = int(os.getenv('DB_PORT', 3306))
            with socket.create_connection((os.getenv('DB_HOST', '127.0.0.1'), port), timeout=2):
                print(f"  MySQL端口可连接 ({port})")
                return True
        except Exception:
            pass
        return False
    
    def check_mysql_connection(self):
        """检查MySQL数据库连接"""
        try:
            # 尝试从.env加载配置
            from dotenv import load_dotenv
            load_dotenv()
            
            config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', 3306)),
                'user': os.getenv('DB_USER', 'root'),
                'password': os.getenv('DB_PASSWORD', ''),
                'database': os.getenv('DB_NAME', 'leave_system')
            }
            
            connection = mysql.connector.connect(**config)
            if connection.is_connected():
                print(f"  数据库连接成功 ({config['user']}@{config['host']}:{config['port']})")
                connection.close()
                return True
        except Error as e:
            print(f"  连接失败: {e}")
        except Exception as e:
            print(f"  检查失败: {e}")
        return False
    
    def check_database_tables(self):
        """检查数据库表"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', 3306)),
                'user': os.getenv('DB_USER', 'root'),
                'password': os.getenv('DB_PASSWORD', ''),
                'database': os.getenv('DB_NAME', 'leave_system')
            }
            
            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()
            
            # 检查关键表
            tables = ['users', 'leaves', 'registration_keys']
            found_tables = []
            
            for table in tables:
                cursor.execute(f"SHOW TABLES LIKE '{table}'")
                if cursor.fetchone():
                    found_tables.append(table)
            
            cursor.close()
            connection.close()
            
            if len(found_tables) == len(tables):
                print(f"  所有关键表存在: {', '.join(tables)}")
                return True
            else:
                print(f"  缺少表: {set(tables) - set(found_tables)}")
                return False
        except Exception as e:
            print(f"  检查失败: {e}")
            return False
    
    def check_flask_app(self):
        """检查Flask应用文件"""
        if Path('app.py').exists():
            print("  app.py 文件存在")
            return True
        print("  app.py 文件不存在")
        return False
    
    def check_virtual_env(self):
        """检查虚拟环境"""
        # 检测是否有激活的虚拟环境
        is_active = (sys.prefix != sys.base_prefix) or (os.getenv('VIRTUAL_ENV') is not None)
        if is_active:
            active_path = os.getenv('VIRTUAL_ENV') or sys.prefix
            print(f"  虚拟环境已激活: {active_path}")
            return True
        # 提示本地venv（未激活）
        if Path('venv').exists():
            print("  发现本地虚拟环境venv，建议运行: source venv/bin/activate")
            return False
        print("  未检测到激活的虚拟环境")
        return False
    
    def check_dependencies(self):
        """检查Python依赖"""
        try:
            import flask
            import mysql.connector
            import dotenv
            import requests
            
            print("  Flask, mysql-connector-python, python-dotenv, requests")
            return True
        except ImportError as e:
            print(f"  缺少依赖: {e}")
            return False
    
    def check_env_file(self):
        """检查.env配置文件"""
        if Path('.env').exists():
            print("  .env 文件存在")
            
            # 检查必要字段
            with open('.env', 'r', encoding='utf-8') as f:
                content = f.read()
                required_keys = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME', 'SECRET_KEY']
                missing = [key for key in required_keys if key not in content]
                
                if missing:
                    print(f"  警告: 缺少配置项 {missing}")
                    return False
                return True
        
        print("  .env 文件不存在")
        return False
    
    def check_templates(self):
        """检查模板文件"""
        template_dir = Path('templates')
        if template_dir.exists():
            html_files = list(template_dir.glob('*.html'))
            if len(html_files) > 5:
                print(f"  模板文件完整 ({len(html_files)} 个HTML文件)")
                return True
            else:
                print(f"  模板文件不完整 (只有 {len(html_files)} 个)")
                return False
        
        print("  templates 目录不存在")
        return False
    
    def check_static_files(self):
        """检查静态文件"""
        static_dir = Path('static')
        if static_dir.exists():
            files = list(static_dir.glob('*'))
            if len(files) > 10:
                print(f"  静态文件完整 ({len(files)} 个文件)")
                return True
            else:
                print(f"  静态文件可能不完整 (只有 {len(files)} 个)")
                return True  # 不严格要求
        
        print("  static 目录不存在")
        return False
    
    def check_port_available(self, port=5000):
        """检查端口是否可用"""
        try:
            # 尝试连接到端口：成功表示已占用；连接失败表示空闲或未开启
            with socket.create_connection(('127.0.0.1', port), timeout=2):
                print(f"  端口 {port} 已被占用")
                return False
        except Exception:
            print(f"  端口 {port} 可用")
            return True
    
    def check_nginx(self):
        """检查Nginx是否安装"""
        try:
            result = subprocess.run(
                ['which', 'nginx'],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                print("  Nginx 已安装 (生产环境配置)")
                return True
        except:
            pass
        print("  Nginx 未安装 (可选)")
        return True
    
    def run_all_checks(self):
        """运行所有检查"""
        print("\n正在执行系统检查...\n")
        
        print("基础环境检查:")
        self.check("Python版本 (3.8+)", self.check_python)
        
        print("\n数据库检查:")
        self.check("MySQL服务状态", self.check_mysql_service)
        self.check("MySQL数据库连接", self.check_mysql_connection)
        self.check("数据库表完整性", self.check_database_tables)
        
        print("\n应用环境检查:")
        self.check("Flask应用文件", self.check_flask_app)
        self.check("Python虚拟环境", self.check_virtual_env)
        self.check("Python依赖包", self.check_dependencies)
        self.check(".env配置文件", self.check_env_file)
        
        print("\n项目文件检查:")
        self.check("模板文件完整性", self.check_templates)
        self.check("静态文件完整性", self.check_static_files)
        
        print("\n系统资源检查:")
        self.check("Flask端口 (5000) 可用性", self.check_port_available)
        self.check("Nginx安装检查", self.check_nginx)
        
        # 打印结果
        success = self.print_results()
        
        # 提供建议
        if success:
            print("✓ 所有检查通过！系统已准备就绪")
            print("\n启动应用:")
            print("  source venv/bin/activate")
            print("  python3 app.py")
        else:
            print("✗ 检查发现问题，请查看上面的失败项")
            print("\n参考:")
            print("  - Ubuntu24部署指南.md (详细部署步骤)")
            print("  - 管理员手册.md (故障排查)")
        
        return success

def main():
    check = HealthCheck()
    success = check.run_all_checks()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()

