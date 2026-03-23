# Ubuntu 24 移植方案总结

## 📋 您已获得以下工具和文档

### 📚 详细部署指南
1. **[Ubuntu24部署指南.md](Ubuntu24部署指南.md)** - 12部分完整指南
   - 系统要求和前置条件
   - 环境准备（Python、MySQL等）
   - 项目部署全过程
   - 生产环境配置（Gunicorn + Nginx）
   - 数据库备份和恢复
   - 监控和日志配置
   - 常见问题解决

2. **[Ubuntu24快速部署.md](Ubuntu24快速部署.md)** - 三步快速启动
   - 仅需5分钟快速部署
   - 常见问题速查表
   - 验证部署成功
   - 生产环境配置简化版

### 🔧 自动化部署脚本

1. **[deploy_ubuntu.sh](deploy_ubuntu.sh)** - 完全自动化部署脚本 ⭐ 推荐使用
   ```bash
   # 使用方法
   bash deploy_ubuntu.sh
   ```
   - 自动更新系统
   - 自动安装依赖（Python、MySQL等）
   - 自动转换文件格式
   - 自动创建虚拟环境
   - 自动初始化数据库
   - 自动测试连接

2. **[convert_files.py](convert_files.py)** - 文件格式转换工具
   ```bash
   # 转换当前目录
   python3 convert_files.py .
   
   # 转换特定文件
   python3 convert_files.py ~/leaves --pattern "*.py"
   
   # 显示详细信息
   python3 convert_files.py . -v
   ```
   - 转换行尾符（CRLF → LF）
   - 转换编码格式（GBK/ANSI → UTF-8）
   - 支持通配符和递归处理

3. **[health_check.py](health_check.py)** - 部署后系统检查工具
   ```bash
   # 运行完整检查
   python3 health_check.py
   ```
   - 检查Python版本
   - 检查MySQL服务
   - 检查数据库连接和表
   - 检查Flask应用文件
   - 检查虚拟环境和依赖
   - 检查配置文件
   - 检查文件完整性
   - 检查端口可用性

---

## 🚀 快速部署方案（推荐）

### 方案A：全自动部署（最简单）⭐⭐⭐

```bash
# 1. 上传文件到Ubuntu
scp -r "d:\Downloads\请假网站\leaves" username@your_ubuntu_ip:~/leaves

# 2. SSH连接到Ubuntu
ssh username@your_ubuntu_ip

# 3. 进入项目目录
cd ~/leaves

# 4. 运行自动部署脚本
bash deploy_ubuntu.sh

# 5. 启动应用
source venv/bin/activate
python3 app.py
```

**优点**: 一键部署，全自动配置  
**缺点**: 需要输入数据库密码  
**耗时**: 约5-10分钟

### 方案B：手动部署（更灵活）

```bash
# 详见 Ubuntu24快速部署.md 的"第1步-第3步"
```

---

## 🔍 部署后验证

### 快速验证
```bash
# 运行健康检查
python3 health_check.py

# 应该显示 "✓ 所有检查通过"
```

### 详细验证
```bash
# 测试数据库连接
mysql -u leaves_user -p leave_system
SHOW TABLES;

# 测试应用启动
source venv/bin/activate
python3 app.py

# 在另一个终端测试
curl http://127.0.0.1:5000/
```

---

## 📁 文件对应关系

| Windows | Ubuntu | 说明 |
|---------|--------|------|
| `app.py` | `~/leaves/app.py` | Flask主应用 |
| `requirements.txt` | `~/leaves/requirements.txt` | Python依赖 |
| `init.sql` | `~/leaves/init.sql` | 数据库初始化 |
| `.env.example` | `~/leaves/.env` | 配置文件 |
| `templates/` | `~/leaves/templates/` | HTML模板 |
| `static/` | `~/leaves/static/` | 静态资源 |

---

## ⚙️ 关键配置说明

### MySQL配置（在.env中）
```env
# 重要：Ubuntu默认MySQL端口是3306，不是Windows的3310
DB_HOST=localhost
DB_PORT=3306
DB_USER=leaves_user
DB_PASSWORD=your_secure_password
DB_NAME=leave_system
```

### Flask配置（在.env中）
```env
FLASK_HOST=0.0.0.0      # 接受所有网卡
FLASK_PORT=5000         # 服务端口
FLASK_DEBUG=False       # 生产环境关闭
SECRET_KEY=your_secret_key
```

---

## 🔒 安全建议

### 部署前必做
- [ ] 修改默认管理员密码（默认: admin/CZM170826czm）
- [ ] 生成安全的SECRET_KEY
  ```bash
  python3 -c "import secrets; print(secrets.token_hex(32))"
  ```
- [ ] 设置强数据库密码
- [ ] 限制MySQL远程访问权限

### 部署后必做
- [ ] 启用HTTPS（生产环境）
- [ ] 配置防火墙规则
- [ ] 启用自动备份
- [ ] 配置监控告警

---

## 📞 故障快速排查

| 错误 | 原因 | 解决方案 |
|------|------|--------|
| MySQL连接失败 | 密码错误/端口错误 | 检查.env文件中的DB_PORT是否为3306 |
| 找不到Python模块 | 虚拟环境未激活 | `source venv/bin/activate` |
| 5000端口被占用 | 应用已运行或被占用 | `sudo lsof -i :5000` 查看 |
| 文件编码错误 | 行尾符或编码问题 | `python3 convert_files.py .` |
| 权限错误 | 文件权限不足 | `chmod -R 755 ~/leaves` |

详细排查见: **Ubuntu24部署指南.md** 第八部分

---

## 🎯 部署流程图

```
Windows (d:\Downloads\请假网站\leaves)
    ↓
    ├─ app.py (已配置.env支持)
    ├─ requirements.txt
    ├─ init.sql (已整理)
    ├─ .env.example
    ├─ templates/
    ├─ static/
    └─ 部署脚本和文档
    
    ↓ (scp上传)
    
Ubuntu (~/leaves)
    ↓
    bash deploy_ubuntu.sh (自动部署)
    ↓
    ├─ 更新系统
    ├─ 安装依赖
    ├─ 转换文件格式
    ├─ 创建虚拟环境
    ├─ 安装Python包
    ├─ 初始化数据库
    └─ 测试连接
    ↓
    python3 health_check.py (验证)
    ↓
    source venv/bin/activate && python3 app.py
    ↓
    http://your_ubuntu_ip:5000 (访问应用)
```

---

## 📊 对比：Windows vs Ubuntu

| 方面 | Windows | Ubuntu |
|------|---------|--------|
| MySQL端口 | 3310 | 3306 |
| 行尾符 | CRLF (\r\n) | LF (\n) |
| 文件权限 | 简单 | 严格 (755/644) |
| Python位置 | C:\Python\... | /usr/bin/python3 |
| 虚拟环境 | venv\Scripts | venv/bin |
| 包管理 | pip (Windows) | apt + pip (Ubuntu) |
| 启动脚本 | .bat | .sh |
| 后台运行 | 任务管理器 | systemd/screen |

---

## 💾 备份策略

### 初始备份（部署后立即做）
```bash
# 备份整个项目
tar -czf leaves_initial_backup.tar.gz ~/leaves

# 备份数据库
mysqldump -u leaves_user -p leave_system > leaves_initial.sql
```

### 定期备份（日常维护）
```bash
# 编辑crontab
crontab -e

# 添加每天凌晨2点自动备份
0 2 * * * mysqldump -u leaves_user -p'password' leave_system > /home/username/backups/leave_system_$(date +\%Y\%m\%d).sql
```

---

## 🎓 学习资源

- **Flask官方文档**: https://flask.palletsprojects.com/
- **MySQL官方文档**: https://dev.mysql.com/doc/
- **Ubuntu官方指南**: https://ubuntu.com/server/docs
- **Nginx配置指南**: https://nginx.org/en/docs/

---

## 📱 支持和反馈

遇到问题？按以下步骤解决：

1. **查看日志**
   ```bash
   tail -50 ~/leaves/app.log
   ```

2. **查看错误信息**
   ```bash
   python3 app.py  # 直接运行查看输出
   ```

3. **运行健康检查**
   ```bash
   python3 health_check.py
   ```

4. **查阅文档**
   - 快速部署: [Ubuntu24快速部署.md](Ubuntu24快速部署.md)
   - 详细指南: [Ubuntu24部署指南.md](Ubuntu24部署指南.md)
   - 系统管理: [管理员手册.md](管理员手册.md)
   - 技术细节: [系统运行逻辑.md](系统运行逻辑.md)

---

## ✅ 最终检查清单

部署完成后检查：

- [ ] `bash deploy_ubuntu.sh` 运行成功
- [ ] `python3 health_check.py` 显示全部通过
- [ ] 能使用 admin/CZM170826czm 登录
- [ ] 能进行请假申请
- [ ] 能进行请假审批
- [ ] 数据库备份已配置
- [ ] 密码已修改
- [ ] 监控告警已配置

---

## 🎉 部署完成！

现在您的请假管理系统已准备好在Ubuntu 24上运行。

**下一步**: 
1. 上传项目文件到Ubuntu
2. 运行 `bash deploy_ubuntu.sh`
3. 运行 `python3 health_check.py` 验证
4. 启动应用: `python3 app.py`
5. 访问: `http://your_ubuntu_ip:5000`

祝部署顺利！🚀

