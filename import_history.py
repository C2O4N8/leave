"""
请假历史记录导入脚本
从HTML文件中提取请假信息并导入到数据库
"""
import re
import os
from datetime import datetime
from bs4 import BeautifulSoup
import mysql.connector
from mysql.connector import Error


def get_db_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            database='leave_system',
            auth_plugin='mysql_native_password'
        )
        return connection
    except Error as e:
        print(f"数据库连接失败: {e}")
        return None


def extract_leave_records_from_html(html_content):
    """
    从HTML内容中提取请假记录
    支持两种格式:
    1. 表格格式（tbody中的tr和td）
    2. List页面格式（div结构）
    
    返回格式:
    [
        {
            'leave_type': '病假',
            'start_time': '2024-01-01 09:00:00',
            'end_time': '2024-01-02 17:00:00',
            'destination': '家里',
            'detail_address': '福建',
            'reason': '生病',
            'approver_name': '班主任',
            'status': 'approved'  # 已通过的历史记录
        }
    ]
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
    except Exception as e:
        print(f"HTML解析失败: {e}")
        return []
    
    records = []
    
    # 先尝试从List页面div结构中提取
    records = extract_from_list_page(soup)
    
    # 如果没有找到，尝试从表格中提取
    if not records:
        records = extract_from_table_page(soup)
    
    return records


def extract_from_list_page(soup):
    """
    从List页面的div结构中提取请假记录
    结构: <div class="item___37i3A">
        <div class="titleBox___3KXB9">
            <div class="title___3htHa">请假类型<div class="status_X___Xxxx"></div></div>
            <div class="applyTime___2GhJ_">申请时间</div>
        </div>
        <div class="scale___35nrk"></div>
        <div class="content___3-k09">
            <div class="startTime___2mv8D">开始时间:XXXX</div>
            <div class="endTime___6BX9O">结束时间:XXXX</div>
            <div class="context___2eK4Z">请假理由：XXXX</div>
            <div class="pass___2c7ga">审核状态</div>
        </div>
    </div>
    """
    records = []
    
    # 查找所有记录项
    items = soup.find_all('div', class_='item___37i3A')
    
    if not items:
        # 尝试用更通用的选择器
        items = soup.find_all('div', class_=re.compile(r'item.*'))
    
    for item in items:
        try:
            record = parse_list_item(item)
            if record:
                records.append(record)
        except Exception as e:
            print(f"List项解析失败: {e}")
            continue
    
    return records


def parse_list_item(item_div):
    """
    解析List页面中的单个请假记录项
    """
    try:
        # 提取标题和申请时间
        title_box = item_div.find('div', class_=re.compile(r'titleBox.*'))
        if not title_box:
            return None
        
        title_elem = title_box.find('div', class_=re.compile(r'title.*'))
        apply_time_elem = title_box.find('div', class_=re.compile(r'applyTime.*'))
        
        if not title_elem or not apply_time_elem:
            return None
        
        # 获取标题（请假类型）
        title_text = title_elem.get_text(strip=True)
        # 去掉可能的状态标签（如 <div class="status_X___Xxxx"></div>）
        leave_type = re.sub(r'[\s\u200b]*$', '', title_text).strip()
        
        # 提取内容信息
        content = item_div.find('div', class_=re.compile(r'content.*'))
        if not content:
            return None
        
        # 提取各字段
        start_time_elem = content.find('div', class_=re.compile(r'startTime.*'))
        end_time_elem = content.find('div', class_=re.compile(r'endTime.*'))
        reason_elem = content.find('div', class_=re.compile(r'context.*'))
        status_elem = content.find('div', class_=re.compile(r'pass.*'))
        
        # 解析时间字符串
        start_time = None
        if start_time_elem:
            start_text = start_time_elem.get_text(strip=True)
            # "开始时间:2025-12-31 12:30:00" -> "2025-12-31 12:30:00"
            start_time = re.sub(r'^开始时间[:：]', '', start_text)
            start_time = normalize_datetime(start_time)
        
        end_time = None
        if end_time_elem:
            end_text = end_time_elem.get_text(strip=True)
            # "结束时间:2026-01-03 17:00:00" -> "2026-01-03 17:00:00"
            end_time = re.sub(r'^结束时间[:：]', '', end_text)
            end_time = normalize_datetime(end_time)
        
        # 解析理由
        reason = ''
        if reason_elem:
            reason_text = reason_elem.get_text(strip=True)
            # "请假理由：元旦" -> "元旦"
            reason = re.sub(r'^请假理由[:：]', '', reason_text)
        
        # 解析状态
        status = 'approved'  # 历史记录默认为已通过
        if status_elem:
            status_text = status_elem.get_text(strip=True)
            if '通过' in status_text or '已批准' in status_text or '审核通过' in status_text:
                status = 'approved'
            elif '拒绝' in status_text or '不通过' in status_text:
                status = 'rejected'
            elif '待审' in status_text or '审核中' in status_text:
                status = 'pending'
        
        # 验证必要字段
        if not leave_type or not start_time or not end_time:
            return None
        
        record = {
            'leave_type': leave_type,
            'start_time': start_time,
            'end_time': end_time,
            'destination': '离校不离市',  # 默认值
            'detail_address': '',
            'reason': reason,
            'approver_name': '管理员',  # 默认值
            'status': status,
            'emergency_contact': '',
            'emergency_phone': ''
        }
        
        return record
        
    except Exception as e:
        print(f"解析List项失败: {e}")
        return None


def extract_from_table_page(soup):
    """
    从表格格式中提取请假记录
    """
    records = []
    
    # 查找所有表格
    tables = soup.find_all('table')
    
    for table in tables:
        tbody = table.find('tbody')
        if not tbody:
            continue
        
        rows = tbody.find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 5:  # 至少需要5列
                continue
            
            try:
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                # 尝试匹配各种可能的列布局
                # 常见格式: 请假类型, 开始时间, 结束时间, 去向/地址, 状态, 备注
                record = parse_leave_row(cell_texts)
                
                if record:
                    records.append(record)
            except Exception as e:
                print(f"行解析失败: {e}")
                continue
    
    return records


def parse_leave_row(cells):
    """
    解析单行请假记录
    支持多种可能的列顺序和格式
    """
    if len(cells) < 5:
        return None
    
    record = {
        'leave_type': None,
        'start_time': None,
        'end_time': None,
        'destination': '离校不离市',  # 默认值
        'detail_address': '',
        'reason': '',
        'approver_name': '管理员',  # 默认值
        'status': 'approved',  # 历史记录默认为已通过
        'emergency_contact': '',
        'emergency_phone': ''
    }
    
    # 定义常见的列类型特征
    leave_types = ['病假', '事假', '年假', '婚假', '丧假', '产假', '陪产假', '调休']
    status_mapping = {'已通过': 'approved', '已批准': 'approved', '通过': 'approved',
                      '审核不通过': 'rejected', '不通过': 'rejected', '已拒绝': 'rejected',
                      '待审': 'pending', '审核中': 'pending'}
    destinations = ['不离校', '离校不离市', '离市', '离校']
    
    # 尝试识别各列
    for i, cell in enumerate(cells):
        cell_lower = cell.lower()
        
        # 识别请假类型
        if not record['leave_type']:
            for leave_type in leave_types:
                if leave_type in cell:
                    record['leave_type'] = leave_type
                    break
        
        # 识别时间（包含冒号或年月日的）
        if is_datetime(cell):
            if not record['start_time']:
                record['start_time'] = normalize_datetime(cell)
            elif not record['end_time']:
                record['end_time'] = normalize_datetime(cell)
        
        # 识别状态
        for status_key, status_val in status_mapping.items():
            if status_key in cell:
                record['status'] = status_val
                break
        
        # 识别去向
        for dest in destinations:
            if dest in cell:
                record['destination'] = dest
                break
        
        # 识别地址（包含省市区等地名的）
        if is_address(cell):
            record['detail_address'] = cell
        
        # 识别备注/理由
        if is_reason(cell) and not record['reason']:
            record['reason'] = cell
    
    # 验证必要字段
    if record['leave_type'] and record['start_time'] and record['end_time']:
        return record
    
    return None


def is_datetime(text):
    """判断文本是否为日期时间"""
    # 匹配格式: 2024-01-01 09:00, 2024/01/01 09:00, 2024-1-1 9:00 等
    datetime_pattern = r'(\d{4}[-/]\d{1,2}[-/]\d{1,2}\s+\d{1,2}:\d{2}|\d{4}[-/]\d{1,2}[-/]\d{1,2})'
    return bool(re.search(datetime_pattern, text))


def normalize_datetime(text):
    """
    标准化日期时间格式为 'YYYY-MM-DD HH:MM:SS'
    """
    # 清理文本
    text = text.strip()
    
    # 尝试多种格式
    formats = [
        r'(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{2}):(\d{2})',  # 2024-01-01 09:00:00
        r'(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{2})',          # 2024-01-01 09:00
        r'(\d{4})/(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2}):(\d{2})',  # 2024/01/01 09:00:00
        r'(\d{4})/(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2})',          # 2024/01/01 09:00
        r'(\d{4})-(\d{1,2})-(\d{1,2})',                               # 2024-01-01
        r'(\d{4})/(\d{1,2})/(\d{1,2})',                               # 2024/01/01
    ]
    
    for fmt in formats:
        match = re.search(fmt, text)
        if match:
            groups = match.groups()
            year = int(groups[0])
            month = int(groups[1])
            day = int(groups[2])
            
            hour = int(groups[3]) if len(groups) > 3 else 0
            minute = int(groups[4]) if len(groups) > 4 else 0
            second = int(groups[5]) if len(groups) > 5 else 0
            
            return f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
    
    return None


def is_address(text):
    """判断文本是否为地址（包含省市区等地名）"""
    # 常见的地名关键词
    address_keywords = ['省', '市', '县', '区', '街', '路', '号', '楼', '村', '镇',
                       '校', '宿', '舍', '家', '福建', '广东', '江西', '上海', '北京']
    return any(keyword in text for keyword in address_keywords) and len(text) >= 2


def is_reason(text):
    """判断文本是否为请假理由"""
    # 避免识别为列表头或特殊字段
    if any(x in text for x in ['状态', '类型', '开始', '结束', '审批', '原因', '备注', '去向']):
        return True
    return len(text) >= 3 and len(text) <= 100


def import_records_to_db(user_id, records):
    """
    导入请假记录到数据库
    
    参数:
        user_id: 用户ID
        records: 请假记录列表
    
    返回:
        (成功数, 失败数)
    """
    if not records:
        return 0, 0
    
    connection = get_db_connection()
    if not connection:
        return 0, len(records)
    
    cursor = connection.cursor()
    success_count = 0
    fail_count = 0
    
    try:
        for record in records:
            try:
                # 检查是否已存在相同的记录（防止重复导入）
                cursor.execute(
                    '''SELECT id FROM leaves 
                    WHERE user_id = %s AND start_time = %s AND leave_type = %s''',
                    (user_id, record['start_time'], record['leave_type'])
                )
                
                if cursor.fetchone():
                    print(f"记录已存在，跳过: {record['leave_type']} {record['start_time']}")
                    fail_count += 1
                    continue
                
                # 插入新记录
                cursor.execute(
                    '''INSERT INTO leaves 
                    (user_id, leave_type, destination, detail_address, 
                     start_time, end_time, reason, emergency_contact, 
                     emergency_phone, approver_name, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())''',
                    (user_id, record['leave_type'], record['destination'], 
                     record['detail_address'], record['start_time'], record['end_time'],
                     record['reason'], record.get('emergency_contact', ''),
                     record.get('emergency_phone', ''), record['approver_name'],
                     record['status'])
                )
                
                success_count += 1
                print(f"导入成功: {record['leave_type']} {record['start_time']} - {record['end_time']}")
                
            except Error as e:
                fail_count += 1
                print(f"插入记录失败: {e}")
                continue
        
        connection.commit()
    
    except Error as e:
        print(f"事务错误: {e}")
        connection.rollback()
    
    finally:
        cursor.close()
        connection.close()
    
    return success_count, fail_count


def import_from_file(user_id, file_path):
    """
    从HTML文件导入请假记录
    
    参数:
        user_id: 用户ID
        file_path: HTML文件路径
    
    返回:
        (成功数, 失败数, 错误信息)
    """
    if not os.path.exists(file_path):
        return 0, 0, f"文件不存在: {file_path}"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        return 0, 0, f"读取文件失败: {e}"
    
    # 提取记录
    records = extract_leave_records_from_html(html_content)
    
    if not records:
        return 0, 0, "HTML中未找到有效的请假记录"
    
    # 导入到数据库
    success, fail = import_records_to_db(user_id, records)
    
    return success, fail, None


# 测试函数
if __name__ == '__main__':
    # 测试导入
    test_file = 'd:\\Downloads\\请假网站\\leaves\\初始\\请假列表.html'
    
    if os.path.exists(test_file):
        print(f"开始测试，读取文件: {test_file}")
        with open(test_file, 'r', encoding='utf-8') as f:
            html = f.read()
        
        records = extract_leave_records_from_html(html)
        print(f"\n提取到 {len(records)} 条记录:\n")
        for i, record in enumerate(records, 1):
            print(f"{i}. {record}")
    else:
        print(f"测试文件不存在: {test_file}")
