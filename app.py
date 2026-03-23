from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
import json
import os
from urllib.parse import urljoin, urlencode
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
import hashlib
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
LOG_DIR = os.getenv('LOG_DIR', 'logs')
LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10485760))
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))

os.makedirs(LOG_DIR, exist_ok=True)
_log_file = os.path.join(LOG_DIR, 'app.log')
_handler = RotatingFileHandler(_log_file, maxBytes=LOG_MAX_BYTES, backupCount=LOG_BACKUP_COUNT)
_formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s')
_handler.setFormatter(_formatter)
_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

app.logger.addHandler(_handler)
app.logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
logging.getLogger().addHandler(_handler)
logging.getLogger().setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

# 控制是否在控制台输出日志（默认True，可在.env中设为False）
LOG_TO_CONSOLE = os.getenv('LOG_TO_CONSOLE', 'True').lower() == 'true'
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

if not LOG_TO_CONSOLE:
    # 移除控制台输出的StreamHandler，仅保留文件日志
    for logger in (app.logger, werkzeug_logger, logging.getLogger()):
        try:
            logger.handlers = [h for h in logger.handlers if not isinstance(h, logging.StreamHandler)]
            if _handler not in logger.handlers:
                logger.addHandler(_handler)
            logger.propagate = False
        except Exception:
            pass

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3310)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '123456'),
    'database': os.getenv('DB_NAME', 'leave_system'),
    'auth_plugin': 'mysql_native_password'
}

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"数据库连接错误: {e}")
        return None

def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_verification_key(salt, username):
    """根据盐值和用户名生成验证秘钥"""
    combined = f"{salt}{username}"
    return hashlib.sha256(combined.encode()).hexdigest()

def generate_salt(length=32):
    """生成随机盐值"""
    return os.urandom(length).hex()

def is_logged_in():
    """检查用户是否已登录"""
    return 'user_id' in session

def get_current_user():
    """获取当前用户信息，如果用户被锁定则自动清除会话"""
    if not is_logged_in():
        return None
    
    connection = get_db_connection()
    if not connection:
        return None
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
        user = cursor.fetchone()
        
        # 检查用户是否被锁定（status='rejected'），如果被锁定则自动登出
        if user and user.get('status') == 'rejected':
            session.clear()  # 清除会话，强制用户重新登录
            return None
        
        return user
    finally:
        cursor.close()
        connection.close()

@app.before_request
def _log_request():
    try:
        app.logger.info(f"REQ {request.method} {request.path} ip={request.remote_addr}")
    except Exception:
        pass

@app.after_request
def _log_response(resp):
    try:
        app.logger.info(f"RES {resp.status_code} {request.path}")
    except Exception:
        pass
    return resp

def init_db_schema():
    """初始化或升级users表，确保包含学生信息字段"""
    connection = get_db_connection()
    if not connection:
        print("无法连接数据库，跳过schema初始化")
        return
    cursor = connection.cursor()
    try:
        # 尝试创建users表（如果不存在）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            password VARCHAR(255) DEFAULT NULL,
            name VARCHAR(100) DEFAULT NULL,
            role VARCHAR(20) DEFAULT 'student',
            status VARCHAR(20) DEFAULT 'verified' COMMENT 'pending(待验证), verified(已验证), rejected(已拒绝)',
            verification_key VARCHAR(255) DEFAULT NULL COMMENT '用户验证秘钥',
            verified_at DATETIME DEFAULT NULL COMMENT '验证时间',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ''')
        connection.commit()

        # 添加/确保字段存在（MySQL 8 支持 IF NOT EXISTS）
        alter_statements = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS gender VARCHAR(10) DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS department VARCHAR(200) DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS major VARCHAR(200) DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS student_id VARCHAR(50) DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS year VARCHAR(20) DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS class_name VARCHAR(200) DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(50) DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_completed TINYINT DEFAULT 0",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'verified'",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_key VARCHAR(255) DEFAULT NULL",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS verified_at DATETIME DEFAULT NULL",
        ]
        for stmt in alter_statements:
            try:
                cursor.execute(stmt)
            except Exception:
                # 在不支持 IF NOT EXISTS 的MySQL版本上，忽略错误
                pass
        connection.commit()

        # 创建registration_keys表（如果不存在）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS registration_keys (
            id INT AUTO_INCREMENT PRIMARY KEY,
            salt VARCHAR(255) NOT NULL COMMENT '随机盐值',
            username VARCHAR(100) NOT NULL COMMENT '用户名',
            generated_key VARCHAR(255) NOT NULL COMMENT '生成的秘钥 (SHA256)',
            generated_by INT COMMENT '生成秘钥的管理员用户ID',
            generated_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '生成时间',
            used_at DATETIME DEFAULT NULL COMMENT '被使用的时间',
            used_by INT DEFAULT NULL COMMENT '使用该秘钥的用户ID',
            is_used TINYINT DEFAULT 0 COMMENT '是否已被使用',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_username (username),
            INDEX idx_generated_key (generated_key)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT '注册秘钥表';
        ''')
        connection.commit()

        # 尝试创建 username 唯一索引（如果不存在）
        try:
            cursor.execute("ALTER TABLE users ADD UNIQUE INDEX ux_users_username (username)")
            connection.commit()
        except Exception:
            # 如果索引已存在或命令不支持，忽略
            connection.rollback()
    finally:
        cursor.close()
        connection.close()

def format_leave_data(leave):
    """格式化请假数据，添加显示字段"""
    leave_type_map = {
        '病假': '病假',
        '事假': '事假',
        '公假（因学院任务或比赛外出）': '公假（因学院任务或比赛外出）',
        '其他': '其他',
        '节假日及寒暑假请假': '节假日及寒暑假请假'
    }
    status_map = {
        'pending': '待审核',
        'approved': '审核通过',
        'rejected': '已拒绝',
        'invalidated': '已销假'
    }
    leave['leave_type_display'] = leave_type_map.get(leave.get('leave_type', ''), '其他')
    leave['status_display'] = status_map.get(leave.get('status', ''), '待审核')
    
    # 分离日期和时间
    if isinstance(leave.get('start_time'), str):
        parts = leave['start_time'].split(' ')
        leave['start_date'] = parts[0] if parts else ''
        leave['start_time'] = parts[1] if len(parts) > 1 else ''
    
    if isinstance(leave.get('end_time'), str):
        parts = leave['end_time'].split(' ')
        leave['end_date'] = parts[0] if parts else ''
        leave['end_time'] = parts[1] if len(parts) > 1 else ''
    
    return leave

def check_and_update_leave_status(cursor, connection, leave):
    """检查leave是否应该更新为已销假，如果end_time已过期则更新"""
    from datetime import datetime
    try:
        if leave.get('status') in ['pending', 'rejected']:
            # 待审核和已拒绝的请假不自动转为已销假
            return
        
        if leave.get('status') == 'approved':
            # 只有审批通过的才可能转为已销假
            end_time = leave.get('end_time')
            if isinstance(end_time, str):
                end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            elif isinstance(end_time, datetime):
                pass
            else:
                return
            
            now = datetime.now()
            if now >= end_time:
                # 已过期，更新为已销假
                cursor.execute(
                    'UPDATE leaves SET status = %s WHERE id = %s',
                    ('invalidated', leave.get('id'))
                )
                connection.commit()
                leave['status'] = 'invalidated'
                leave['status_display'] = '已销假'
    except Exception as e:
        print(f"更新leave状态时出错: {e}")

@app.route('/')
def index():
    """首页 - 摆渡页面"""
    if is_logged_in():
        user = get_current_user()
        if user and user.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@app.route('/user_dashboard')
def user_dashboard():
    """用户面板 - 摆渡页面"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = get_current_user()
    # get_current_user() 会自动检查并清除被锁定用户的会话
    if not user:
        return redirect(url_for('login'))
    
    if user.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    return render_template('user_dashboard.html', current_user=user)

@app.route('/home')
def home():
    """首页"""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    return render_template('home_index.html', current_user=user)

@app.route('/home_apps')
def home_apps():
    """应用页面"""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    return render_template('home_apps.html', current_user=user)

@app.route('/admin_dashboard')
def admin_dashboard():
    """管理员面板 - 摆渡页面"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = get_current_user()
    if not user or user.get('role') != 'admin':
        return redirect(url_for('user_dashboard'))
    
    return render_template('admin_dashboard.html', current_user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_hash = hash_password(password)
        
        connection = get_db_connection()
        if not connection:
            return render_template('login.html', error='数据库连接失败'), 500
        
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', 
                         (username, password_hash))
            user = cursor.fetchone()
            
            if user:
                # 检查用户是否被锁定（status='rejected' 表示被管理员锁定）
                if user.get('status') == 'rejected':
                    return render_template('login.html', error='您的账户已被锁定，请联系管理员解锁')
                
                # 检查用户是否已验证（仅对student角色检查，排除被锁定状态）
                if user.get('role') == 'student' and user.get('status') == 'pending':
                    # 如果是待验证状态，重定向到验证页面
                    return redirect(url_for('verify_registration', username=username))
                
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user.get('role', 'student')
                # 根据角色重定向到各自的面板
                if user.get('role') == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
            else:
                return render_template('login.html', error='用户名或密码错误')
        finally:
            cursor.close()
            connection.close()
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册页面 - 新用户注册后需要验证"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name', '')
        
        connection = get_db_connection()
        if not connection:
            return render_template('register.html', error='数据库连接失败'), 500
        
        cursor = connection.cursor()
        try:
            password_hash = hash_password(password)
            # 新用户默认为待验证状态 'pending'
            cursor.execute(
                'INSERT INTO users (username, password, name, role, status) VALUES (%s, %s, %s, %s, %s)',
                (username, password_hash, name, 'student', 'pending')
            )
            connection.commit()
            # 注册成功后重定向到验证页面
            return redirect(url_for('verify_registration', username=username))
        except Error as e:
            connection.rollback()
            error_msg = '用户名已存在或注册失败' if '1062' in str(e) else str(e)
            return render_template('register.html', error=error_msg), 400
        finally:
            cursor.close()
            connection.close()
    
    return render_template('register.html')


@app.route('/verify_registration', methods=['GET', 'POST'])
def verify_registration():
    """用户注册后验证页面 - 需要输入秘钥才能完成注册"""
    username = request.args.get('username') or request.form.get('username')
    
    if not username:
        return redirect(url_for('register'))
    
    if request.method == 'POST':
        verification_key = request.form.get('verification_key', '').strip()
        
        connection = get_db_connection()
        if not connection:
            return render_template('verify_registration.html', username=username, error='数据库连接失败'), 500
        
        cursor = connection.cursor(dictionary=True)
        try:
            # 检查秘钥是否存在且匹配
            cursor.execute(
                '''SELECT * FROM registration_keys 
                WHERE username = %s AND generated_key = %s AND is_used = 0''',
                (username, verification_key)
            )
            key_record = cursor.fetchone()
            
            if not key_record:
                return render_template('verify_registration.html', username=username, 
                                     error='秘钥不正确或已被使用'), 400
            
            # 获取用户ID并验证用户状态
            cursor.execute('SELECT id, status FROM users WHERE username = %s', (username,))
            user = cursor.fetchone()
            
            if not user:
                return render_template('verify_registration.html', username=username, 
                                     error='用户不存在'), 404
            
            if user['status'] != 'pending':
                return render_template('verify_registration.html', username=username, 
                                     error='用户已验证或已被拒绝'), 400
            
            # 标记秘钥为已使用
            cursor.execute(
                '''UPDATE registration_keys 
                SET is_used = 1, used_at = NOW(), used_by = %s 
                WHERE id = %s''',
                (user['id'], key_record['id'])
            )
            
            # 更新用户状态为已验证
            cursor.execute(
                '''UPDATE users 
                SET status = 'verified', verification_key = %s, verified_at = NOW() 
                WHERE id = %s''',
                (verification_key, user['id'])
            )
            connection.commit()
            
            return render_template('verify_registration_success.html', username=username)
        except Error as e:
            connection.rollback()
            print(f"验证错误: {e}")
            return render_template('verify_registration.html', username=username, 
                                 error=f'验证失败: {str(e)}'), 400
        finally:
            cursor.close()
            connection.close()
    
    return render_template('verify_registration.html', username=username)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    """用户信息完善页面：展示并允许更新当前用户的学生信息"""
    if not is_logged_in():
        return redirect(url_for('login'))

    user = get_current_user()
    # get_current_user() 会自动检查并清除被锁定用户的会话
    if not user:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    if not connection:
        return render_template('user_profile.html', current_user=user, error='数据库连接失败'), 500

    cursor = connection.cursor(dictionary=True)
    try:
        if request.method == 'POST':
            # 从表单读取字段并保存（更新）
            name = request.form.get('name')
            gender = request.form.get('gender')
            department = request.form.get('faculty')  # 页面上是 faculty，数据库是 department
            major = request.form.get('major')
            student_id = request.form.get('student_no')  # 页面上是 student_no，数据库是 student_id
            year = request.form.get('grade')  # 页面上是 grade，数据库是 year
            class_name = request.form.get('class_name')
            phone = request.form.get('phone')

            # 重新从数据库拉取用户信息以检查是否已完成个人信息
            cursor.execute('SELECT profile_completed FROM users WHERE id = %s', (user['id'],))
            status_row = cursor.fetchone()
            if status_row and status_row.get('profile_completed'):
                return render_template('user_profile.html', current_user=user, error='您已完成信息完善，不能再次修改。')

            # 学号唯一性检查
            if student_id:
                cursor.execute('SELECT id FROM users WHERE student_id = %s AND id != %s', (student_id, user['id']))
                dup = cursor.fetchone()
                if dup:
                    return render_template('user_profile.html', current_user=user, error='学号已被其他用户使用，请检查后重试。')

            try:
                cursor.execute(
                    '''UPDATE users SET name=%s, gender=%s, department=%s, major=%s, student_id=%s, year=%s, class_name=%s, phone=%s, profile_completed=1 WHERE id=%s''',
                    (name, gender, department, major, student_id, year, class_name, phone, user['id'])
                )
                connection.commit()
            except Error as e:
                connection.rollback()
                return render_template('user_profile.html', current_user=user, error=str(e))

            return redirect(url_for('user_dashboard'))

        # GET: 读取用户已有信息，用于表单预填
        cursor.execute('SELECT * FROM users WHERE id = %s', (user['id'],))
        user_info = cursor.fetchone()
        return render_template('user_profile.html', current_user=user, user_info=user_info)
    finally:
        cursor.close()
        connection.close()

@app.route('/apply_submit', methods=['POST'])
def apply_submit():
    """处理请假申请提交"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = get_current_user()
    # get_current_user() 会自动检查并清除被锁定用户的会话
    if not user:
        return redirect(url_for('login'))
    
    if user.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    # 获取表单数据
    leave_type = request.form.get('leave_type')
    destination = request.form.get('destination')  # 请假去向: 不离校、离校不离市、离市
    detail_address = request.form.get('address')  # 组合后的地址: 省-市-区-具体地址
    start_datetime = request.form.get('start_datetime')
    end_datetime = request.form.get('end_datetime')
    emergency_contact = request.form.get('emergency_contact')
    emergency_phone = request.form.get('contact_phone')  # 映射到 emergency_phone
    reason = request.form.get('reason')
    approver_name = request.form.get('approver_name')  # 审批人名字
    
    # 验证必填字段
    if not all([leave_type, destination, detail_address, start_datetime, end_datetime, 
                emergency_contact, emergency_phone, reason, approver_name]):
        return render_template('apply.html', current_user=user, error='所有字段都是必填的'), 400
    
    # 转换datetime-local格式为SQL格式
    try:
        start_time = start_datetime.replace('T', ' ') + ':00'
        end_time = end_datetime.replace('T', ' ') + ':00'
    except:
        return render_template('apply.html', current_user=user, error='时间格式错误'), 400
    
    connection = get_db_connection()
    if not connection:
        return render_template('apply.html', current_user=user, error='数据库连接失败'), 500
    
    cursor = connection.cursor()
    try:
        # 检查是否已存在未处理的请假申请
        cursor.execute('SELECT COUNT(1) AS cnt FROM leaves WHERE user_id = %s AND status = %s', (session['user_id'], 'pending'))
        row = cursor.fetchone()
        if row and row[0] > 0:
            return render_template('apply.html', current_user=user, error='已有一条待审核的请假申请，无法提交新的申请'), 400

        cursor.execute(
            '''INSERT INTO leaves 
            (user_id, leave_type, destination, detail_address, start_time, end_time, reason, 
             emergency_contact, emergency_phone, approver_name, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending', NOW())''',
            (session['user_id'], leave_type, destination, detail_address, start_time, end_time, 
             reason, emergency_contact, emergency_phone, approver_name)
        )
        connection.commit()
        return redirect(url_for('h_manage'))
    except Error as e:
        connection.rollback()
        print(f"错误: {e}")
        return render_template('apply.html', current_user=user, error=f'提交失败: {str(e)}'), 400
    finally:
        cursor.close()
        connection.close()

@app.route('/apply', methods=['GET'])
def apply():
    """请假申请页面"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = get_current_user()
    # get_current_user() 会自动检查并清除被锁定用户的会话
    if not user:
        return redirect(url_for('login'))
    
    # 管理员无法访问申请页面
    if user.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    return render_template('apply.html', current_user=user)

@app.route('/h_manage')
def h_manage():
    """学生请假列表页面 - 支持状态筛选"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = get_current_user()
    # get_current_user() 会自动检查并清除被锁定用户的会话
    if not user:
        return redirect(url_for('login'))
    
    # 管理员无法访问学生请假列表
    if user.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    # 获取状态筛选参数
    status_filter = request.args.get('status', 'all').lower()
    
    connection = get_db_connection()
    if not connection:
        return render_template('leave_list.html', leaves=[], error='数据库连接失败'), 500
    
    cursor = connection.cursor(dictionary=True)
    try:
        # 构建基础查询
        base_query = '''SELECT l.* FROM leaves l 
                       WHERE l.user_id = %s'''
        params = [session['user_id']]
        
        # 根据状态筛选添加条件
        if status_filter != 'all':
            base_query += ' AND l.status = %s'
            params.append(status_filter)
        
        base_query += ' ORDER BY l.created_at DESC'
        
        cursor.execute(base_query, params)
        leaves = cursor.fetchall()
        
        # 检查并更新每条记录的状态
        for leave in leaves:
            check_and_update_leave_status(cursor, connection, leave)
        
        # 格式化每条记录
        leaves = [format_leave_data(leave) for leave in leaves]
        
        return render_template('leave_list.html', 
                             current_user=user, 
                             leaves=leaves,
                             current_status=status_filter)
    finally:
        cursor.close()
        connection.close()

@app.route('/detail/<int:leave_id>', methods=['GET', 'POST'])
def detail(leave_id):
    """请假详情页面"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = get_current_user()
    # get_current_user() 会自动检查并清除被锁定用户的会话
    if not user:
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    if not connection:
        return render_template('leave_detail.html', leave=None, error='数据库连接失败'), 500
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            '''SELECT l.*, u.name as student_name FROM leaves l 
            JOIN users u ON l.user_id = u.id 
            WHERE l.id = %s''',
            (leave_id,)
        )
        leave = cursor.fetchone()
        
        if not leave:
            return render_template('leave_detail.html', leave=None, error='请假记录不存在'), 404
        
        # 检查权限：学生只能查看自己的，管理员可以查看所有
        if leave['user_id'] != session['user_id'] and (not user or user.get('role') != 'admin'):
            return render_template('leave_detail.html', leave=None, error='无权限查看此记录'), 403
        
        # 检查并自动更新leave状态
        check_and_update_leave_status(cursor, connection, leave)
        
        # 重新获取leave以获取最新状态
        cursor.execute(
            '''SELECT l.*, u.name as student_name FROM leaves l 
            JOIN users u ON l.user_id = u.id 
            WHERE l.id = %s''',
            (leave_id,)
        )
        leave = cursor.fetchone()
        
        # 获取审批人名称（优先使用approver_name字段，如果没有则查询approved_by）
        approve_user_name = leave.get('approver_name')
        if not approve_user_name and leave.get('approved_by'):
            cursor.execute('SELECT name FROM users WHERE id = %s', (leave['approved_by'],))
            approve_user = cursor.fetchone()
            if approve_user:
                approve_user_name = approve_user.get('name', 'admin')
        
        # 格式化数据
        leave = format_leave_data(leave)
        return render_template('leave_detail.html', current_user=user, leave=leave, approve_user_name=approve_user_name)
    finally:
        cursor.close()
        connection.close()

@app.route('/admin/registration_keys', methods=['GET', 'POST'])
def admin_registration_keys():
    """管理员秘钥管理页面 - 生成和管理注册秘钥"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = get_current_user()
    if not user or user.get('role') != 'admin':
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        
        if not username:
            return render_template('admin_registration_keys.html', current_user=user, 
                                 error='请输入用户名'), 400
        
        connection = get_db_connection()
        if not connection:
            return render_template('admin_registration_keys.html', current_user=user, 
                                 error='数据库连接失败'), 500
        
        cursor = connection.cursor(dictionary=True)
        try:
            # 检查用户是否存在
            cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
            user_exists = cursor.fetchone()
            
            if not user_exists:
                return render_template('admin_registration_keys.html', current_user=user, 
                                     error=f'用户"{username}"不存在'), 404
            
            # 生成新的盐值和秘钥
            salt = generate_salt()
            generated_key = generate_verification_key(salt, username)
            
            # 保存到数据库
            cursor.execute(
                '''INSERT INTO registration_keys 
                (salt, username, generated_key, generated_by) 
                VALUES (%s, %s, %s, %s)''',
                (salt, username, generated_key, session['user_id'])
            )
            connection.commit()
            
            # 返回成功信息并显示秘钥
            return render_template('admin_registration_keys.html', current_user=user, 
                                 success=True, username=username, generated_key=generated_key, 
                                 salt=salt)
        except Error as e:
            connection.rollback()
            print(f"生成秘钥错误: {e}")
            return render_template('admin_registration_keys.html', current_user=user, 
                                 error=f'生成秘钥失败: {str(e)}'), 400
        finally:
            cursor.close()
            connection.close()
    
    # GET: 显示秘钥历史
    connection = get_db_connection()
    if not connection:
        return render_template('admin_registration_keys.html', current_user=user, 
                             error='数据库连接失败'), 500
    
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(
            '''SELECT id, username, generated_at, is_used, used_at 
            FROM registration_keys 
            ORDER BY generated_at DESC 
            LIMIT 50'''
        )
        keys_history = cursor.fetchall()
        return render_template('admin_registration_keys.html', current_user=user, 
                             keys_history=keys_history)
    finally:
        cursor.close()
        connection.close()

@app.route('/approve_list')
def approve_list():
    """管理员审批页面"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = get_current_user()
    if not user or user.get('role') != 'admin':
        return redirect(url_for('user_dashboard'))
    
    connection = get_db_connection()
    if not connection:
        return render_template('approve_list.html', leaves=[], error='数据库连接失败'), 500
    
    cursor = connection.cursor(dictionary=True)
    try:
        # 获取所有请假申请（按状态排序）
        cursor.execute(
            '''SELECT l.*, u.name as student_name, u.id as student_id 
            FROM leaves l 
            JOIN users u ON l.user_id = u.id 
            ORDER BY l.status='pending' DESC, l.created_at DESC'''
        )
        leaves = cursor.fetchall()
        leaves = [format_leave_data(leave) for leave in leaves]
        return render_template('approve_list.html', current_user=user, leaves=leaves)
    finally:
        cursor.close()
        connection.close()

@app.route('/approve', methods=['POST'])
def approve():
    """审批请假申请"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = get_current_user()
    if not user or user.get('role') != 'admin':
        return jsonify({'error': '无权限'}), 403
    
    leave_id = request.form.get('leave_id')
    status = request.form.get('status')  # 'approved' 或 'rejected'
    remarks = request.form.get('remarks', '')
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': '数据库连接失败'}), 500
    
    cursor = connection.cursor()
    try:
        cursor.execute(
            '''UPDATE leaves 
            SET status = %s, approved_at = NOW(), approved_by = %s 
            WHERE id = %s''',
            (status, session['user_id'], leave_id)
        )
        connection.commit()
        return jsonify({'success': True})
    except Error as e:
        connection.rollback()
        print(f"审批错误: {e}")
        return jsonify({'error': str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@app.route('/admin/users')
def admin_users():
    """管理员用户管理页面"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = get_current_user()
    if not user or user.get('role') != 'admin':
        return redirect(url_for('user_dashboard'))
    
    connection = get_db_connection()
    if not connection:
        return render_template('admin_users.html', current_user=user, users=[], error='数据库连接失败'), 500
    
    cursor = connection.cursor(dictionary=True)
    try:
        # 获取搜索和筛选参数
        search_query = request.args.get('search', '').strip()
        status_filter = request.args.get('status', '')
        
        # 构建查询
        query = '''SELECT id, username, name, gender, department, major, student_id, 
                          year, class_name, phone, role, status, created_at, updated_at 
                   FROM users WHERE 1=1'''
        params = []
        
        if search_query:
            query += ''' AND (username LIKE %s OR name LIKE %s OR student_id LIKE %s 
                            OR phone LIKE %s OR department LIKE %s)'''
            search_pattern = f'%{search_query}%'
            params.extend([search_pattern] * 5)
        
        if status_filter:
            query += ' AND status = %s'
            params.append(status_filter)
        
        query += ' ORDER BY created_at DESC'
        
        cursor.execute(query, params)
        users = cursor.fetchall()
        
        return render_template('admin_users.html', current_user=user, users=users, 
                             search_query=search_query, status_filter=status_filter)
    finally:
        cursor.close()
        connection.close()

@app.route('/admin/users/<int:user_id>/toggle_status', methods=['POST'])
def toggle_user_status(user_id):
    """锁定/解锁用户账户"""
    if not is_logged_in():
        return jsonify({'error': '未登录'}), 401
    
    user = get_current_user()
    if not user or user.get('role') != 'admin':
        return jsonify({'error': '无权限'}), 403
    
    # 不能锁定自己
    if user_id == session['user_id']:
        return jsonify({'error': '不能锁定自己的账户'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': '数据库连接失败'}), 500
    
    cursor = connection.cursor(dictionary=True)
    try:
        # 获取当前用户状态
        cursor.execute('SELECT status, role FROM users WHERE id = %s', (user_id,))
        target_user = cursor.fetchone()
        
        if not target_user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 不能锁定其他管理员
        if target_user['role'] == 'admin':
            return jsonify({'error': '不能锁定管理员账户'}), 400
        
        # 切换状态
        current_status = target_user['status']
        new_status = 'rejected' if current_status == 'verified' else 'verified'
        
        cursor.execute(
            'UPDATE users SET status = %s, updated_at = NOW() WHERE id = %s',
            (new_status, user_id)
        )
        connection.commit()
        
        action = '锁定' if new_status == 'rejected' else '解锁'
        return jsonify({'success': True, 'message': f'用户已{action}', 'new_status': new_status})
    except Error as e:
        connection.rollback()
        print(f"切换用户状态错误: {e}")
        return jsonify({'error': str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """删除用户（硬删除）"""
    if not is_logged_in():
        return jsonify({'error': '未登录'}), 401
    
    user = get_current_user()
    if not user or user.get('role') != 'admin':
        return jsonify({'error': '无权限'}), 403
    
    # 不能删除自己
    if user_id == session['user_id']:
        return jsonify({'error': '不能删除自己的账户'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': '数据库连接失败'}), 500
    
    cursor = connection.cursor(dictionary=True)
    try:
        # 检查用户是否存在
        cursor.execute('SELECT role, name FROM users WHERE id = %s', (user_id,))
        target_user = cursor.fetchone()
        
        if not target_user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 不能删除管理员
        if target_user['role'] == 'admin':
            return jsonify({'error': '不能删除管理员账户'}), 400
        
        # 删除用户的所有请假记录
        cursor.execute('DELETE FROM leaves WHERE user_id = %s', (user_id,))
        
        # 删除用户
        cursor.execute('DELETE FROM users WHERE id = %s', (user_id,))
        
        connection.commit()
        
        return jsonify({
            'success': True, 
            'message': f'用户 {target_user["name"]} 及其所有数据已删除'
        })
    except Error as e:
        connection.rollback()
        print(f"删除用户错误: {e}")
        return jsonify({'error': str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@app.route('/logout')
def logout():
    """登出"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/import_history', methods=['GET', 'POST'])
def import_history():
    """导入历史请假记录"""
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    # 只允许学生导入，管理员不能导入
    if user.get('role') == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        # 检查是否提交了文件
        if 'html_file' not in request.files:
            return render_template('import_history.html', current_user=user, 
                                  error='没有选择文件')
        
        html_file = request.files['html_file']
        if not html_file or html_file.filename == '':
            return render_template('import_history.html', current_user=user, 
                                  error='没有选择文件')
        
        # 检查文件类型
        if not html_file.filename.endswith('.html'):
            return render_template('import_history.html', current_user=user, 
                                  error='请上传HTML文件')
        
        try:
            # 读取HTML内容
            html_content = html_file.read().decode('utf-8')
            
            # 导入记录
            from import_history import extract_leave_records_from_html, import_records_to_db
            
            records = extract_leave_records_from_html(html_content)
            
            if not records:
                return render_template('import_history.html', current_user=user, 
                                      error='HTML中未找到有效的请假记录，请确保文件格式正确')
            
            # 导入到数据库
            success, fail = import_records_to_db(session['user_id'], records)
            
            return render_template('import_history.html', current_user=user,
                                  success=True, success_count=success, fail_count=fail,
                                  total_count=len(records))
        
        except Exception as e:
            return render_template('import_history.html', current_user=user, 
                                  error=f'导入失败: {str(e)}')
    
    return render_template('import_history.html', current_user=user)


@app.route('/user_settings', methods=['GET'])
def user_settings():
    """用户设置页面"""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    return render_template('user_settings.html', current_user=user)


@app.route('/api/settings/get_safety_mode', methods=['GET'])
def get_safety_mode():
    """获取安全模式设置"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '未登录'}), 401
    
    # 从session中获取安全模式设置
    safety_mode_enabled = session.get(f'safety_mode_{user["id"]}', False)
    safe_url = session.get(f'safe_url_{user["id"]}', 'https://lyxgqj.gdppla.edu.cn/ydxg')
    
    return jsonify({
        'safety_mode_enabled': safety_mode_enabled,
        'safe_url': safe_url
    })


@app.route('/api/settings/set_safety_mode', methods=['POST'])
def set_safety_mode():
    """设置安全模式开关"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '未登录', 'success': False}), 401
    
    data = request.get_json()
    enabled = data.get('enabled', False)
    
    # 保存到session
    session[f'safety_mode_{user["id"]}'] = enabled
    session.modified = True
    
    return jsonify({'success': True})


@app.route('/api/settings/set_safe_url', methods=['POST'])
def set_safe_url():
    """设置安全地址"""
    user = get_current_user()
    if not user:
        return jsonify({'error': '未登录', 'success': False}), 401
    
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'success': False, 'message': '地址不能为空'}), 400
    
    # 基础URL验证
    if not (url.startswith('http://') or url.startswith('https://')):
        return jsonify({'success': False, 'message': '地址必须以 http:// 或 https:// 开头'}), 400
    
    # 保存到session
    session[f'safe_url_{user["id"]}'] = url
    session.modified = True
    
    return jsonify({'success': True})


@app.route('/api/get_safety_mode_for_page', methods=['GET'])
def get_safety_mode_for_page():
    """为页面获取安全模式信息（用于前端跳转）"""
    user = get_current_user()
    if not user:
        return jsonify({'safety_mode_enabled': False, 'target_url': None})
    
    safety_mode_enabled = session.get(f'safety_mode_{user["id"]}', False)
    # 固定目标网站首页
    target_url = 'https://lyxgqj.gdppla.edu.cn/ydxg'
    
    return jsonify({
        'safety_mode_enabled': safety_mode_enabled,
        'target_url': target_url
    })


# 简化版安全模式：直接打开目标网站，由浏览器管理 Cookie

@app.route('/safe_mode/start')
def safe_mode_start():
    """启用安全模式并打开目标网站登录页"""
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    # 启用安全模式
    session[f'safety_mode_{user["id"]}'] = True
    session.modified = True
    
    # 在新窗口打开目标网站（由前端处理，这里只负责启用安全模式）
    # 返回一个页面，告知用户目标网站将在新窗口打开
    return render_template('safe_mode_redirect.html', target_url='https://lyxgqj.gdppla.edu.cn/ydxg')


if __name__ == '__main__':
    # 初始化数据库 schema（创建 users 表及字段）
    try:
        init_db_schema()
    except Exception as e:
        print(f"初始化数据库schema时出错: {e}")
    
    # 从环境变量读取配置
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    app.run(debug=debug_mode, host=host, port=port, use_reloader=False)