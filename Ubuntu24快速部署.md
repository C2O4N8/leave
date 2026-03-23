# Ubuntu 24 快速部署指南

## 三步快速启动（仅需5分钟）

### 第1步：上传文件到Ubuntu

在Windows上运行（PowerShell）:
```powershell
# 上传整个项目到Ubuntu
scp -r "d:\Downloads\请假网站\leaves" username@your_ubuntu_ip:~/leaves

# 或从Ubuntu拉取（在Ubuntu上运行）
cd ~
scp -r username@windows_ip:"d:\\Downloads\\请假网站\\leaves" ~/leaves
```

### 第2步：运行自动部署脚本

在Ubuntu上运行:
```bash
# 进入项目目录
cd ~/leaves

# 运行部署脚本
bash deploy_ubuntu.sh

# 脚本会自动:
# ✓ 更新系统
# ✓ 安装Python/MySQL/依赖
# ✓ 转换文件格式
# ✓ 创建虚拟环境
# ✓ 安装Python包
# ✓ 初始化数据库
# ✓ 测试连接
```

### 第3步：启动应用

```bash
cd ~/leaves
source venv/bin/activate
python3 app.py

# 输出：
# * Running on http://0.0.0.0:5000
# * Press CTRL+C to quit
```

访问: `http://your_ubuntu_ip:5000`
账号: `admin` / `CZM170826czm`

---

## 常见问题速查表

| 问题 | 解决方案 |
|------|--------|
| scp命令不工作 | 确保Ubuntu已安装SSH服务: `sudo apt install openssh-server` |
| MySQL权限错误 | 使用带密码: `sudo mysql -u root -p` |
| 找不到Python模块 | 确保激活虚拟环境: `source venv/bin/activate` |
| 端口5000被占用 | 查看进程: `sudo lsof -i :5000` 或修改.env中的FLASK_PORT |
| 文件权限问题 | 修复权限: `chmod -R 755 ~/leaves` |
| 数据库导入失败 | 检查.env文件中的数据库密码是否正确 |

---

## 验证部署成功

```bash
# 1. 检查进程运行
ps aux | grep python

# 2. 检查端口监听
sudo netstat -tulpn | grep 5000

# 3. 测试连接
curl http://127.0.0.1:5000/

# 4. 查看日志
# Ctrl+C停止后查看错误信息
```

---

## 生产环境部署

部署完成后，按以下步骤配置为生产环境:

### 1. 安装Gunicorn
```bash
source venv/bin/activate
pip install gunicorn
```

### 2. 创建systemd服务
```bash
sudo nano /etc/systemd/system/leaves.service
```

粘贴以下内容：
```ini
[Unit]
Description=Leave Management System
After=network.target

[Service]
Type=simple
User=username
WorkingDirectory=/home/username/leaves
Environment="PATH=/home/username/leaves/venv/bin"
ExecStart=/home/username/leaves/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3. 启动服务
```bash
sudo systemctl daemon-reload
sudo systemctl enable leaves
sudo systemctl start leaves
sudo systemctl status leaves
```

---

## 备份和恢复

### 定时备份（每天凌晨2点）
```bash
# 编辑crontab
crontab -e

# 添加这一行
0 2 * * * mysqldump -u leaves_user -p'password' leave_system > /home/username/backups/leave_system_$(date +\%Y\%m\%d).sql
```

### 紧急恢复
```bash
mysql -u leaves_user -p leave_system < backup.sql
```

---

## 更多信息

- 详细部署: 见 `Ubuntu24部署指南.md`
- 系统管理: 见 `管理员手册.md`
- 功能使用: 见 `用户手册.md`
- 技术细节: 见 `系统运行逻辑.md`

---

## 故障排查联系

如遇到问题，按以下顺序检查：

1. **查看错误日志**
   ```bash
   tail -50 app.log  # 如有日志文件
   ```

2. **重启应用**
   ```bash
   sudo systemctl restart leaves
   sudo journalctl -u leaves -f
   ```

3. **检查数据库**
   ```bash
   mysql -u leaves_user -p leave_system
   SHOW TABLES;
   ```

4. **查看完整部署指南**
   打开 `Ubuntu24部署指南.md` 第八部分

