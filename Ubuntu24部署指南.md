# 请假管理系统 - Ubuntu 24 部署指南

## 系统要求

- **操作系统**: Ubuntu 24.04 LTS
- **Python**: 3.12+ (Ubuntu 24预装)
- **MySQL**: 8.0+
- **磁盘空间**: 最少1GB
- **内存**: 最少512MB
- **网络**: 允许3310端口（MySQL）和5000端口（Flask）

---

## 第一部分：Windows到Linux的文件转换

### 1. 处理行尾符号

Windows使用CRLF（\r\n），Linux使用LF（\n）。需要转换关键文件：

```bash
# 在Linux上转换Python文件
cd /home/username/leaves
find . -name "*.py" -exec dos2unix {} \;

# 或使用sed转换
find . -name "*.py" -exec sed -i 's/\r$//' {} \;
```

### 2. 处理文件编码

Python文件需要UTF-8编码。检查并转换：

```bash
# 检查编码
file app.py

# 转换编码（如需要）
iconv -f GBK -t UTF-8 app.py -o app.py.utf8
mv app.py.utf8 app.py
```

---

## 第二部分：环境准备

### 1. 更新系统包

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. 安装Python开发工具

```bash
sudo apt install -y python3-pip python3-venv python3-dev
```

### 3. 安装MySQL服务器

```bash
sudo apt install -y mysql-server

# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 验证MySQL运行
sudo systemctl status mysql
```

### 4. 安装其他依赖

```bash
# dos2unix 用于转换行尾
sudo apt install -y dos2unix

# 其他可能需要的工具
sudo apt install -y curl wget git
```

---

## 第三部分：项目部署

### 1. 创建项目目录

```bash
# 创建项目目录
sudo mkdir -p /opt/leaves
cd /opt/leaves

# 或在home目录（推荐开发/测试）
mkdir -p ~/leaves
cd ~/leaves
```

### 2. 上传文件到Linux

使用以下方法之一：

**方法A: 使用SCP（推荐）**
```bash
# 从Windows上执行（Windows PowerShell）
scp -r "d:\Downloads\请假网站\leaves\*" username@your_ubuntu_ip:~/leaves/

# 或从Ubuntu上拉取
scp -r username@windows_ip:"/mnt/d/Downloads/请假网站/leaves/*" ~/leaves/
```

**方法B: 使用USB或文件共享**
- 挂载Windows共享或USB驱动器
- 复制文件到Linux

**方法C: 使用Git**
```bash
git clone your_repo_url ~/leaves
cd ~/leaves
```

### 3. 转换文件格式

```bash
cd ~/leaves

# 转换所有Python文件的行尾
dos2unix *.py
dos2unix app.py
dos2unix import_history.py

# 转换SQL文件
dos2unix init.sql

# 转换配置文件
dos2unix .env.example

# 转换模板（可选但推荐）
dos2unix templates/*.html
```

### 4. 创建Python虚拟环境

```bash
cd ~/leaves

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip
```

### 5. 安装Python依赖

```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 使用requirements.txt安装
pip install -r requirements.txt

# 或手动安装
pip install Flask==3.0.0
pip install mysql-connector-python==8.2.0
pip install python-dotenv==1.0.0
pip install requests==2.31.0
```

---

## 第四部分：数据库配置

### 1. 连接到MySQL

```bash
# 使用root用户登录MySQL
sudo mysql -u root

# 如果需要输入密码
sudo mysql -u root -p
```

### 2. 创建数据库和用户

```sql
-- 创建leave_system数据库
CREATE DATABASE leave_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建dedicated用户（推荐）
CREATE USER 'leaves_user'@'localhost' IDENTIFIED BY 'secure_password_here';

-- 授予权限
GRANT ALL PRIVILEGES ON leave_system.* TO 'leaves_user'@'localhost';
FLUSH PRIVILEGES;

-- 退出MySQL
EXIT;
```

### 3. 导入初始化脚本

```bash
# 使用root用户导入
sudo mysql -u root < init.sql

# 或使用专用用户
mysql -u leaves_user -p leave_system < init.sql
```

### 4. 验证数据库

```bash
# 登录验证
mysql -u leaves_user -p leave_system

# 在MySQL提示符中
SHOW TABLES;
SELECT COUNT(*) FROM users;
DESC users;
EXIT;
```

---

## 第五部分：配置环境变量

### 1. 创建.env文件

```bash
cd ~/leaves
cp .env.example .env
nano .env
```

### 2. 编辑.env文件

对于Linux部署，更新以下内容：

```env
# 数据库配置 - 根据第四部分配置调整
DB_HOST=localhost
DB_PORT=3306              # Ubuntu MySQL默认端口3306，不是3310
DB_USER=leaves_user       # 使用专用用户
DB_PASSWORD=secure_password_here
DB_NAME=leave_system

# Flask配置
SECRET_KEY=your-secret-key-change-this-to-something-secure
FLASK_DEBUG=False         # 生产环境设为False
FLASK_HOST=0.0.0.0        # 接受所有网卡连接
FLASK_PORT=5000

# 安全模式默认目标网站
SAFE_MODE_DEFAULT_URL=https://lyxgqj.gdppla.edu.cn/ydxg
```

### 3. 保存文件

按Ctrl+O后回车，Ctrl+X退出（nano编辑器）

---

## 第六部分：测试应用

### 1. 测试数据库连接

```bash
cd ~/leaves
source venv/bin/activate

python3 << 'EOF'
import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host='localhost',
        user='leaves_user',
        password='secure_password_here',
        database='leave_system'
    )
    if connection.is_connected():
        print("✓ 数据库连接成功！")
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        result = cursor.fetchone()
        print(f"✓ 用户表记录数: {result[0]}")
        cursor.close()
        connection.close()
except Error as e:
    print(f"✗ 数据库连接失败: {e}")
EOF
```

### 2. 启动Flask应用

```bash
cd ~/leaves
source venv/bin/activate

# 测试启动
python3 app.py

# 输出应该显示:
# * Running on http://0.0.0.0:5000
# * Press CTRL+C to quit
```

### 3. 在另一个终端测试

```bash
# 打开新的SSH/terminal
curl http://127.0.0.1:5000/

# 应该返回登录页面的HTML
```

### 4. 使用默认管理员账户登录

- **用户名**: admin
- **密码**: CZM170826czm

### 5. 停止应用

按Ctrl+C停止Flask应用

---

## 第七部分：生产部署（可选）

### 1. 使用Gunicorn和Nginx

```bash
# 安装Gunicorn
source venv/bin/activate
pip install gunicorn

# 创建启动脚本
nano ~/leaves/run.sh
```

### 2. run.sh 脚本内容

```bash
#!/bin/bash
cd /home/username/leaves
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 3. 设置为Systemd服务

创建服务文件：
```bash
sudo nano /etc/systemd/system/leaves.service
```

添加以下内容：
```ini
[Unit]
Description=Leave Management System
After=network.target

[Service]
Type=notify
User=username
WorkingDirectory=/home/username/leaves
Environment="PATH=/home/username/leaves/venv/bin"
ExecStart=/home/username/leaves/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. 启用并启动服务

```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启用服务开机自启
sudo systemctl enable leaves

# 启动服务
sudo systemctl start leaves

# 查看状态
sudo systemctl status leaves

# 查看日志
sudo journalctl -u leaves -f
```

### 5. 配置Nginx反向代理

```bash
sudo nano /etc/nginx/sites-available/leaves
```

添加配置：
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/leaves /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

---

## 第八部分：常见问题解决

### 问题1: MySQL连接失败 - "Access denied for user"

```bash
# 检查MySQL是否运行
sudo systemctl status mysql

# 检查用户权限
sudo mysql -u root
SHOW GRANTS FOR 'leaves_user'@'localhost';
```

### 问题2: Python模块导入错误

```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt --upgrade

# 检查特定模块
python3 -c "import flask; print(flask.__version__)"
```

### 问题3: 端口已被占用

```bash
# 查看占用5000端口的进程
sudo lsof -i :5000

# 查看占用3306端口的进程
sudo lsof -i :3306

# 杀死进程（如需要）
sudo kill -9 PID
```

### 问题4: 权限问题

```bash
# 修改文件权限
chmod -R 755 ~/leaves
chmod 600 ~/leaves/.env

# 修改目录权限
chmod 755 ~/leaves/templates
chmod 755 ~/leaves/static
```

### 问题5: 文件行尾转换问题

```bash
# 检查文件行尾类型
file app.py

# 完整转换（更彻底）
find . -type f -name "*.py" -exec sed -i 's/\r$//' {} \;
find . -type f -name "*.html" -exec sed -i 's/\r$//' {} \;
find . -type f -name "*.sql" -exec sed -i 's/\r$//' {} \;
```

---

## 第九部分：调试技巧

### 1. 启用Flask调试模式（仅开发）

编辑.env：
```env
FLASK_DEBUG=True
```

### 2. 查看详细日志

```bash
# 启动时显示日志
FLASK_ENV=development python3 app.py

# 或使用logging模块
python3 << 'EOF'
import logging
logging.basicConfig(level=logging.DEBUG)
import app
EOF
```

### 3. 测试数据库查询

```bash
mysql -u leaves_user -p leave_system

# 查看用户
SELECT * FROM users LIMIT 5;

# 查看请假记录
SELECT * FROM leaves LIMIT 5;

# 查看验证秘钥
SELECT * FROM registration_keys LIMIT 5;
```

### 4. 监控进程

```bash
# 实时监控CPU和内存
top

# 或查看Python进程
ps aux | grep python

# 监控网络连接
netstat -tulpn | grep 5000
```

---

## 第十部分：备份和恢复

### 1. 备份数据库

```bash
# 备份整个数据库
mysqldump -u leaves_user -p leave_system > backup.sql

# 备份包含结构和数据
mysqldump -u leaves_user -p --all-databases > full_backup.sql

# 定时备份（crontab）
0 2 * * * mysqldump -u leaves_user -p123456 leave_system > /home/username/backups/leave_system_$(date +\%Y\%m\%d).sql
```

### 2. 恢复数据库

```bash
# 恢复单个数据库
mysql -u leaves_user -p leave_system < backup.sql

# 恢复所有数据库
mysql -u root -p < full_backup.sql
```

### 3. 备份应用文件

```bash
# 备份整个项目
tar -czf leaves_backup_$(date +%Y%m%d).tar.gz ~/leaves

# 恢复备份
tar -xzf leaves_backup_20260117.tar.gz -C ~/
```

---

## 第十一部分：性能优化

### 1. 数据库优化

```sql
-- 添加索引（如未添加）
ALTER TABLE users ADD INDEX idx_username (username);
ALTER TABLE users ADD INDEX idx_status (status);
ALTER TABLE leaves ADD INDEX idx_user_id (user_id);
ALTER TABLE leaves ADD INDEX idx_status (status);
```

### 2. MySQL配置优化

编辑 `/etc/mysql/mysql.conf.d/mysqld.cnf`：

```ini
# 连接池
max_connections=100
max_allowed_packet=16M

# 缓存
query_cache_size=16M
query_cache_type=1

# 日志
slow_query_log=1
long_query_time=2
```

重启MySQL：
```bash
sudo systemctl restart mysql
```

### 3. Flask应用优化

修改app.py中的Gunicorn启动：
```bash
gunicorn -w 8 -b 0.0.0.0:5000 --timeout 60 app:app
```

---

## 第十二部分：监控和日志

### 1. 设置应用日志

创建logging配置（logging_config.py）：
```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    handler = RotatingFileHandler(
        'app.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    return handler
```

### 2. MySQL慢查询日志

```bash
# 查看慢查询
sudo tail -f /var/log/mysql/slow-query.log
```

### 3. 系统监控

```bash
# 监控磁盘使用
df -h

# 监控内存使用
free -h

# 监控进程
htop
```

---

## 总结检查清单

部署完成后的检查清单：

- [ ] Python虚拟环境已创建并激活
- [ ] 所有依赖已安装（pip list验证）
- [ ] 文件行尾已转换为LF格式
- [ ] 数据库已创建并初始化
- [ ] 专用数据库用户已创建
- [ ] .env文件已正确配置
- [ ] 数据库连接测试成功
- [ ] Flask应用能成功启动
- [ ] 默认管理员账户能正常登录
- [ ] 所有主要功能已测试
- [ ] Nginx/Gunicorn已配置（生产环境）
- [ ] 备份策略已实施
- [ ] 监控告警已配置

---

## 快速参考命令

```bash
# 虚拟环境
source ~/leaves/venv/bin/activate
deactivate

# 启动应用
cd ~/leaves && source venv/bin/activate && python3 app.py

# 启动生产环境
sudo systemctl start leaves

# 查看日志
sudo journalctl -u leaves -f

# 数据库连接
mysql -u leaves_user -p leave_system

# 重启MySQL
sudo systemctl restart mysql

# 备份
mysqldump -u leaves_user -p leave_system > backup.sql

# 查看进程
ps aux | grep python

# 端口检查
sudo lsof -i :5000
sudo lsof -i :3306
```

---

**部署完成后联系方式**: 如有问题，参考 [管理员手册.md](管理员手册.md) 的故障排查章节。

