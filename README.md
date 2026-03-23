# 请假管理系统

一个基于Flask的在线请假管理系统，支持学生请假申请、管理员审批、用户管理等功能。

## 功能特性

### 学生功能
- 用户注册与验证
- 完善个人信息
- 在线请假申请
- 查看请假记录和状态
- 导入历史请假记录
- 状态筛选和查询

### 管理员功能
- 请假审批管理
- 用户账户管理
- 验证秘钥生成
- 用户锁定/解锁
- 数据统计查看

### 系统特性
- 移动端适配
- SHA256密码加密
- 安全的会话管理
- 面包屑导航
- 状态实时更新

## 技术栈

- **后端**: Flask 3.0.0 (Python 3.8+)
- **数据库**: MySQL 8.0+
- **前端**: HTML5, CSS3, JavaScript
- **UI框架**: Ant Design Mobile
- **加密**: SHA256
- **配置管理**: python-dotenv

## 快速开始

### 1. 环境准备

#### Python环境
```bash
Python 3.8 或更高版本
```

#### MySQL数据库
```bash
MySQL 8.0 或更高版本
```

### 2. 安装依赖

```bash
cd d:\Downloads\请假网站\leaves
pip install -r requirements.txt
```

### 3. 配置系统

复制环境变量模板：
```bash
copy .env.example .env
```

编辑 `.env` 文件，修改数据库配置：
```env
DB_HOST=localhost
DB_PORT=3310
DB_USER=root
DB_PASSWORD=你的数据库密码
DB_NAME=leave_system
SECRET_KEY=生成一个随机字符串
```

### 4. 初始化数据库

使用MySQL客户端执行：
```bash
mysql -h 127.0.0.1 -P 3310 -u root -p < init.sql
```

或使用MySQL Workbench/Navicat打开 `init.sql` 并执行。

### 5. 启动系统

Windows:
```bash
启动系统.bat
```

或手动启动:
```bash
python app.py
```

### 6. 访问系统

浏览器打开: http://127.0.0.1:5000

默认管理员账户：
- 用户名: `admin`
- 密码: `CZM170826czm`

## 项目结构

```
leaves/
├── app.py                 # Flask应用主文件
├── import_history.py      # 历史记录导入模块
├── init.sql              # 数据库初始化脚本
├── requirements.txt       # Python依赖包
├── .env.example          # 环境变量模板
├── .env                  # 环境变量配置（需创建）
├── 启动系统.bat           # Windows启动脚本
├── 用户手册.md            # 用户使用手册
├── 管理员手册.md          # 管理员手册
├── README.md             # 项目说明文档
├── templates/            # HTML模板文件
│   ├── login.html        # 登录页面
│   ├── register.html     # 注册页面
│   ├── home.html         # 学生首页
│   ├── home_apps.html    # 应用列表
│   ├── profile.html      # 个人信息
│   ├── apply.html        # 请假申请
│   ├── leave_list.html   # 请假列表
│   ├── leave_detail.html # 请假详情
│   ├── admin_dashboard.html      # 管理员仪表板
│   ├── approve_list.html         # 审批列表
│   ├── admin_users.html          # 用户管理
│   ├── admin_registration_keys.html  # 秘钥管理
│   └── ...
└── static/               # 静态资源文件
    ├── *.css            # 样式文件
    ├── *.js             # JavaScript文件
    └── *.png            # 图片资源
```

## 使用说明

### 学生用户

1. **注册账户**: 访问注册页面，填写用户名和密码
2. **验证账户**: 联系管理员获取验证秘钥，完成验证
3. **完善信息**: 首次登录填写个人信息（姓名、学号、班级等）
4. **提交请假**: 填写请假信息并提交审批
5. **查看状态**: 在请假列表查看审批状态

### 管理员用户

1. **审批请假**: 在审批列表查看待审批申请，批准或拒绝
2. **管理用户**: 查看所有用户，锁定/解锁/删除账户
3. **生成秘钥**: 为新注册用户生成验证秘钥
4. **系统维护**: 定期备份数据库，检查系统运行状态

详细说明请查看：
- 学生用户：[用户手册.md](用户手册.md)
- 管理员：[管理员手册.md](管理员手册.md)

## 数据库说明

### 主要表结构

#### users表（用户表）
存储用户基本信息和认证信息

#### leaves表（请假表）
存储所有请假申请记录

#### registration_keys表（验证秘钥表）
存储用户验证秘钥记录

详细字段说明见 `init.sql` 文件

## 安全性

- 密码使用SHA256加密存储
- 支持环境变量配置敏感信息
- Session安全管理
- SQL注入防护
- XSS攻击防护

⚠️ **生产环境建议**:
- 修改默认管理员密码
- 使用强密码策略
- 启用HTTPS
- 配置防火墙
- 定期备份数据

## 常见问题

### Q: 无法连接数据库？
A: 检查MySQL服务是否启动，确认 `.env` 中的数据库配置正确。

### Q: 用户无法登录？
A: 确认账户已验证（status='verified'），未被锁定。

### Q: 忘记管理员密码？
A: 使用SQL重置密码：
```sql
UPDATE users 
SET password='fe92795d0d48538dfe88e715ac0b896fd2d0fca22630466d18273b574e0e7657'
WHERE username='admin';
-- 密码重置为: CZM170826czm
```

### Q: 如何备份数据？
A: 使用mysqldump命令：
```bash
mysqldump -h 127.0.0.1 -P 3310 -u root -p leave_system > backup.sql
```

更多问题请查看手册或联系技术支持。

## 维护与更新

### 数据库备份
建议每天自动备份数据库，保留最近7天的备份文件。

### 日志监控
定期检查系统日志，关注异常登录和错误信息。

### 性能优化
- 定期清理历史数据
- 优化数据库索引
- 监控服务器资源

## 版本历史

### v3.0 (2026-01-17)
- 添加 `.env` 环境变量支持
- 优化数据库连接管理
- 完善面包屑导航系统
- 添加用户锁定功能
- 改进安全性和稳定性
- 完善文档和手册

### v2.0 (2026-01-16)
- 初始版本发布
- 基础功能实现

## 许可证

本项目仅用于学习和教育目的。

## 技术支持

如有问题或建议，请联系系统管理员。

## 贡献指南

欢迎提交问题报告和功能建议。

---

**开发者**: 系统开发团队  
**版本**: 3.0  
**更新日期**: 2026-01-17
