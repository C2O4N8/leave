-- ========================================================================
-- 请假系统 - 数据库完整初始化脚本
-- ========================================================================
-- 版本: 3.0
-- 更新日期: 2026-01-17
-- 说明: 包含所有表创建、字段、索引和初始管理员账户
-- ========================================================================

-- ========================================================================
-- 1. 创建数据库
-- ========================================================================

CREATE DATABASE IF NOT EXISTS leave_system 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE leave_system;

-- ========================================================================
-- 2. 创建 users 表（用户信息表）
-- ========================================================================

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(100) UNIQUE NOT NULL COMMENT '用户名（唯一）',
    password VARCHAR(255) NOT NULL COMMENT '密码（SHA256加密）',
    name VARCHAR(100) DEFAULT NULL COMMENT '姓名',
    gender VARCHAR(10) DEFAULT NULL COMMENT '性别',
    department VARCHAR(200) DEFAULT NULL COMMENT '院系/部门',
    major VARCHAR(200) DEFAULT NULL COMMENT '专业',
    student_id VARCHAR(50) DEFAULT NULL COMMENT '学号',
    year VARCHAR(20) DEFAULT NULL COMMENT '年级',
    class_name VARCHAR(200) DEFAULT NULL COMMENT '班级',
    phone VARCHAR(50) DEFAULT NULL COMMENT '联系电话',
    role VARCHAR(20) DEFAULT 'student' COMMENT '角色: student(学生) 或 admin(管理员)',
    status VARCHAR(20) DEFAULT 'verified' COMMENT 'verified(已验证), pending(待验证), rejected(已拒绝/锁定)',
    verification_key VARCHAR(255) DEFAULT NULL COMMENT '用户验证秘钥',
    verified_at DATETIME DEFAULT NULL COMMENT '验证完成时间',
    profile_completed TINYINT DEFAULT 0 COMMENT '个人信息是否完善 (0=未完善, 1=已完善)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '账户创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
    
    UNIQUE INDEX ux_username (username),
    INDEX idx_role (role),
    INDEX idx_status (status),
    INDEX idx_profile_completed (profile_completed)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ========================================================================
-- 3. 创建 leaves 表（请假申请表）
-- ========================================================================

CREATE TABLE IF NOT EXISTS leaves (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '请假ID',
    user_id INT NOT NULL COMMENT '申请人用户ID',
    student_name VARCHAR(100) DEFAULT NULL COMMENT '学生姓名（冗余存储）',
    leave_type VARCHAR(50) NOT NULL COMMENT '请假类型: 病假/事假/公假等',
    in_class VARCHAR(10) DEFAULT NULL COMMENT '是否在班: yes/no',
    destination VARCHAR(100) DEFAULT NULL COMMENT '请假去向',
    detail_address VARCHAR(255) DEFAULT NULL COMMENT '详细地址',
    start_time DATETIME NOT NULL COMMENT '请假开始时间',
    end_time DATETIME NOT NULL COMMENT '请假结束时间',
    reason TEXT DEFAULT NULL COMMENT '请假理由',
    emergency_contact VARCHAR(100) DEFAULT NULL COMMENT '紧急联系人',
    emergency_phone VARCHAR(20) DEFAULT NULL COMMENT '紧急联系电话',
    attachment VARCHAR(255) DEFAULT NULL COMMENT '附件文件路径',
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending(待审核), approved(已批准), rejected(已拒绝), invalidated(已销假)',
    remarks TEXT DEFAULT NULL COMMENT '审批备注',
    approver_name VARCHAR(100) DEFAULT NULL COMMENT '审批人名字（由申请人填写）',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '申请提交时间',
    approved_at DATETIME DEFAULT NULL COMMENT '审批完成时间',
    approved_by INT DEFAULT NULL COMMENT '审批人ID',
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL,
    
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_approved_by (approved_by),
    INDEX idx_start_time (start_time),
    INDEX idx_created_at (created_at)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='请假申请表';

-- ========================================================================
-- 4. 创建 registration_keys 表（注册验证秘钥表）
-- ========================================================================

CREATE TABLE IF NOT EXISTS registration_keys (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '秘钥ID',
    salt VARCHAR(255) NOT NULL COMMENT '随机盐值（用于生成秘钥）',
    username VARCHAR(100) NOT NULL COMMENT '关联的用户名',
    generated_key VARCHAR(255) NOT NULL COMMENT '生成的秘钥（SHA256加密）',
    generated_by INT DEFAULT NULL COMMENT '生成秘钥的管理员用户ID',
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '秘钥生成时间',
    used_at DATETIME DEFAULT NULL COMMENT '秘钥被使用时间',
    used_by INT DEFAULT NULL COMMENT '使用该秘钥完成验证的用户ID',
    is_used TINYINT DEFAULT 0 COMMENT '是否已被使用 (0=未使用, 1=已使用)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间',
    
    INDEX idx_username (username),
    INDEX idx_generated_key (generated_key),
    INDEX idx_is_used (is_used),
    INDEX idx_generated_by (generated_by)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户注册验证秘钥表';

-- ========================================================================
-- 5. 插入初始管理员账户
-- ========================================================================

-- 默认管理员账户
-- 用户名: admin
-- 密码: CZM170826czm（已加密为SHA256哈希值）
INSERT INTO users (
    username, 
    password, 
    name, 
    gender, 
    department, 
    role, 
    status, 
    profile_completed,
    verified_at
) VALUES (
    'admin',
    'fe92795d0d48538dfe88e715ac0b896fd2d0fca22630466d18273b574e0e7657',
    '系统管理员',
    'male',
    '学工部',
    'admin',
    'verified',
    1,
    NOW()
) ON DUPLICATE KEY UPDATE 
    status='verified', 
    profile_completed=1,
    verified_at=NOW();

-- ========================================================================
-- 6. 验证脚本执行结果
-- ========================================================================

SELECT '========================================' as '';
SELECT '✓ 数据库初始化完成' as '执行结果';
SELECT '========================================' as '';

-- 确认创建的表
SELECT '' as '';
SELECT '=== 数据库表列表 ===' as '';
SELECT TABLE_NAME as '表名' FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'leave_system' 
ORDER BY TABLE_NAME;

-- 确认管理员账户
SELECT '' as '';
SELECT '=== 初始用户信息 ===' as '';
SELECT 
    id as '用户ID', 
    username as '用户名', 
    name as '姓名', 
    role as '角色', 
    status as '状态',
    profile_completed as '信息完善'
FROM users;

-- 统计数据
SELECT '' as '';
SELECT '=== 数据统计 ===' as '';
SELECT 
    (SELECT COUNT(*) FROM users) as '用户总数',
    (SELECT COUNT(*) FROM users WHERE role='admin') as '管理员数',
    (SELECT COUNT(*) FROM users WHERE role='student') as '学生数',
    (SELECT COUNT(*) FROM leaves) as '请假记录',
    (SELECT COUNT(*) FROM registration_keys) as '秘钥总数';

SELECT '' as '';
SELECT '========================================' as '';
SELECT '初始化完成！' as '状态';
SELECT '管理员账户: admin' as '提示';
SELECT '默认密码: CZM170826czm' as '提示';
SELECT '请访问: http://127.0.0.1:5000' as '提示';
SELECT '========================================' as '';

-- ========================================================================
-- 系统说明文档
-- ========================================================================

/*
【请假管理系统 - 数据库说明】

一、系统功能
  1. 用户注册与验证
     - 新用户注册后默认 status='pending'（待验证）
     - 管理员生成验证秘钥（SHA256加密）
     - 用户输入秘钥后 status 变为 'verified'
     - 只有 verified 状态的用户才能登录

  2. 请假申请流程
     - 学生提交请假申请（status='pending'）
     - 同时只能有一个 pending 状态的申请
     - 管理员审批：approved(通过) / rejected(拒绝)
     - 学生可查看历史记录

  3. 个人信息管理
     - profile_completed 字段标记信息完善状态
     - 学生首次登录需完善个人信息
     - 包括：姓名、性别、学号、班级、手机号等

  4. 用户权限管理
     - role='admin': 管理员（审批请假、管理用户、生成秘钥）
     - role='student': 学生（提交请假、查看记录）
     - status='rejected': 用户被锁定，自动登出

二、初始账户
  用户名: admin
  密码: CZM170826czm
  角色: 管理员
  权限: 全部功能

三、数据库特性
  - 字符集: UTF8MB4（支持中文和Emoji）
  - 引擎: InnoDB（支持事务和外键）
  - 外键约束: 级联删除和更新
  - 索引优化: 提升查询性能
  - 时间戳: 自动记录创建和更新时间

四、部署步骤

  方法一：命令行
    mysql -h 127.0.0.1 -P 3310 -u root -p < init.sql

  方法二：MySQL Workbench
    1. 打开 MySQL Workbench
    2. 连接到数据库（localhost:3310）
    3. 打开此脚本文件
    4. 点击执行（⚡图标）

  方法三：Navicat/phpMyAdmin
    1. 连接数据库
    2. 导入 SQL 文件
    3. 执行脚本

五、安全建议
  ⚠️ 生产环境部署前请务必：
    1. 修改管理员默认密码
    2. 更换 app.py 中的 SECRET_KEY
    3. 修改数据库密码
    4. 启用 HTTPS
    5. 配置防火墙
    6. 定期备份数据库

六、维护命令

  查看所有用户:
    SELECT id, username, name, role, status FROM users;

  查看请假统计:
    SELECT status, COUNT(*) as count FROM leaves GROUP BY status;

  重置管理员密码:
    UPDATE users 
    SET password='fe92795d0d48538dfe88e715ac0b896fd2d0fca22630466d18273b574e0e7657'
    WHERE username='admin';
    -- 密码重置为: CZM170826czm

  清空测试数据:
    TRUNCATE TABLE leaves;
    TRUNCATE TABLE registration_keys;
    DELETE FROM users WHERE role='student';

七、故障排查

  问题：无法连接数据库
  解决：检查 MySQL 服务是否启动
       检查端口 3310 是否正确
       检查用户名密码是否正确

  问题：用户无法登录
  解决：检查 status 是否为 'verified'
       检查 password 是否正确（SHA256）
       检查是否被锁定（status='rejected'）

  问题：请假申请失败
  解决：检查 profile_completed 是否为 1
       检查是否已有 pending 状态的申请
       检查外键关联是否正常

八、技术栈
  - 后端: Flask (Python 3.8+)
  - 数据库: MySQL 8.0+
  - 前端: HTML5, CSS3, JavaScript
  - UI框架: Ant Design Mobile
  - 加密: SHA256

九、联系支持
  如有问题，请联系系统管理员
  或查看项目文档

*/
