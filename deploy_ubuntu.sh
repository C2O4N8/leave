#!/bin/bash

# 请假管理系统 - Ubuntu 24 自动部署脚本
# 使用方法: bash deploy_ubuntu.sh

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查权限
check_sudo() {
    if [[ $EUID -ne 0 ]]; then
        log_warning "此脚本需要sudo权限来安装系统包"
        read -p "继续执行? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 第一步：更新系统
step_update_system() {
    log_info "正在更新系统包..."
    sudo apt update -qq
    sudo apt upgrade -y -qq
    log_success "系统包已更新"
}

# 第二步：安装依赖
step_install_dependencies() {
    log_info "正在安装依赖..."
    
    # 检查是否已安装
    if ! command -v python3 &> /dev/null; then
        log_info "安装Python3..."
        sudo apt install -y python3 python3-pip python3-venv python3-dev
    else
        log_success "Python3已安装"
    fi
    
    if ! command -v mysql &> /dev/null; then
        log_info "安装MySQL服务器..."
        sudo DEBIAN_FRONTEND=noninteractive apt install -y mysql-server
    else
        log_success "MySQL已安装"
    fi
    
    if ! command -v dos2unix &> /dev/null; then
        log_info "安装dos2unix..."
        sudo apt install -y dos2unix
    else
        log_success "dos2unix已安装"
    fi
    
    log_success "所有依赖已安装"
}

# 第三步：设置MySQL服务
step_setup_mysql() {
    log_info "正在设置MySQL服务..."
    
    # 启动MySQL
    sudo systemctl start mysql || true
    sudo systemctl enable mysql
    
    log_success "MySQL服务已启动"
}

# 第四步：复制和转换文件
step_copy_convert_files() {
    log_info "正在转换文件格式..."
    
    if [ ! -f "app.py" ]; then
        log_error "未找到app.py文件，请确保在leaves项目目录中执行此脚本"
        exit 1
    fi
    
    # 转换Python文件
    find . -name "*.py" -exec dos2unix {} \; 2>/dev/null || \
        find . -name "*.py" -exec sed -i 's/\r$//' {} \;
    
    # 转换SQL文件
    if [ -f "init.sql" ]; then
        dos2unix init.sql 2>/dev/null || sed -i 's/\r$//' init.sql
    fi
    
    # 转换配置文件
    if [ -f ".env.example" ]; then
        dos2unix .env.example 2>/dev/null || sed -i 's/\r$//' .env.example
    fi
    
    log_success "文件格式已转换"
}

# 第五步：创建虚拟环境
step_create_venv() {
    log_info "正在创建Python虚拟环境..."
    
    if [ -d "venv" ]; then
        log_warning "虚拟环境已存在，跳过创建"
    else
        python3 -m venv venv
        log_success "虚拟环境已创建"
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip -q
    log_success "pip已升级"
}

# 第六步：安装Python依赖
step_install_python_packages() {
    log_info "正在安装Python依赖包..."
    
    source venv/bin/activate
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt -q
        log_success "Python依赖已安装"
    else
        log_error "未找到requirements.txt"
        exit 1
    fi
}

# 第七步：配置.env文件
step_configure_env() {
    log_info "正在配置环境变量..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            chmod 600 .env
            log_success ".env文件已创建"
            
            # 提示用户编辑.env
            log_warning "请编辑.env文件并设置以下内容:"
            echo "  DB_HOST=localhost"
            echo "  DB_PORT=3306"
            echo "  DB_USER=leaves_user"
            echo "  DB_PASSWORD=<输入安全密码>"
            echo "  DB_NAME=leave_system"
            echo "  SECRET_KEY=<生成的随机密钥>"
            
            read -p "按Enter继续..."
        else
            log_error ".env.example文件不存在"
            exit 1
        fi
    else
        log_success ".env文件已存在"
    fi
}

# 第八步：初始化数据库
step_init_database() {
    log_info "正在初始化数据库..."
    
    if [ ! -f "init.sql" ]; then
        log_error "未找到init.sql文件"
        exit 1
    fi
    
    read -p "输入MySQL root密码（按Enter如为空）: " -s MYSQL_ROOT_PASSWORD
    echo
    
    # 创建数据库
    if [ -z "$MYSQL_ROOT_PASSWORD" ]; then
        sudo mysql -u root < init.sql
    else
        sudo mysql -u root -p"$MYSQL_ROOT_PASSWORD" < init.sql
    fi
    
    log_success "数据库已初始化"
}

# 第九步：测试连接
step_test_connection() {
    log_info "正在测试数据库连接..."
    
    source venv/bin/activate
    
    python3 << 'PYEOF'
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

try:
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', '123456'),
        database=os.getenv('DB_NAME', 'leave_system')
    )
    
    if connection.is_connected():
        print("[SUCCESS] 数据库连接成功！")
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        result = cursor.fetchone()
        print(f"[SUCCESS] 用户表记录数: {result[0]}")
        cursor.close()
        connection.close()
except Error as e:
    print(f"[ERROR] 数据库连接失败: {e}")
    exit(1)
PYEOF
    
    if [ $? -ne 0 ]; then
        log_error "数据库连接测试失败"
        exit 1
    fi
    
    log_success "数据库连接测试通过"
}

# 第十步：测试应用启动
step_test_app() {
    log_info "正在测试Flask应用启动..."
    
    source venv/bin/activate
    
    # 后台启动应用
    timeout 5 python3 app.py > /dev/null 2>&1 &
    sleep 2
    
    # 测试连接
    if curl -s http://127.0.0.1:5000/ > /dev/null; then
        log_success "应用启动成功"
    else
        log_warning "应用启动测试超时或失败（但可能正常运行）"
    fi
    
    # 杀死测试进程
    pkill -f "python3 app.py" || true
}

# 完成
step_completion() {
    log_success "================================"
    log_success "部署完成！"
    log_success "================================"
    echo
    log_info "后续步骤:"
    echo "1. 编辑 .env 文件，设置数据库密码和SECRET_KEY"
    echo "2. 启动应用: source venv/bin/activate && python3 app.py"
    echo "3. 访问 http://your_ip:5000"
    echo "4. 使用默认账户登录: admin / CZM170826czm"
    echo
    log_info "更多信息请参考: Ubuntu24部署指南.md"
}

# 主函数
main() {
    log_info "================================"
    log_info "请假管理系统 Ubuntu 24 部署脚本"
    log_info "================================"
    echo
    
    # 检查当前目录
    if [ ! -f "app.py" ]; then
        log_error "错误: 请在leaves项目根目录执行此脚本"
        exit 1
    fi
    
    # 执行各步骤
    step_update_system
    echo
    
    step_install_dependencies
    echo
    
    step_setup_mysql
    echo
    
    step_copy_convert_files
    echo
    
    step_create_venv
    echo
    
    step_install_python_packages
    echo
    
    step_configure_env
    echo
    
    read -p "确认已编辑.env文件? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "请先编辑.env文件然后重新运行此脚本"
        exit 1
    fi
    
    step_init_database
    echo
    
    step_test_connection
    echo
    
    step_test_app
    echo
    
    step_completion
}

# 运行主函数
main

