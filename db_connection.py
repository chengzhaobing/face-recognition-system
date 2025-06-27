import mysql.connector
from mysql.connector import Error
from datetime import datetime
import hashlib

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'database': 'face_recognition_db',
    'user': 'root',
    'password': 'your_password'  # 请修改为你的MySQL密码
}

def get_connection():
    """获取数据库连接"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"数据库连接错误: {e}")
        return None

def init_database():
    """初始化数据库和表"""
    try:
        # 首先连接到MySQL服务器（不指定数据库）
        temp_config = DB_CONFIG.copy()
        temp_config.pop('database')
        
        connection = mysql.connector.connect(**temp_config)
        cursor = connection.cursor()
        
        # 创建数据库（如果不存在）
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # 创建用户表
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_users_table)
        
        # 创建登录记录表
        create_login_records_table = """
        CREATE TABLE IF NOT EXISTS login_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
        cursor.execute(create_login_records_table)
        
        # 创建识别记录表
        create_recognition_records_table = """
        CREATE TABLE IF NOT EXISTS recognition_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            person_name VARCHAR(100),
            recognition_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confidence FLOAT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
        cursor.execute(create_recognition_records_table)
        
        connection.commit()
        print("数据库初始化成功")
        
    except Error as e:
        print(f"数据库初始化错误: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_user(username, password):
    """验证用户登录"""
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        hashed_password = hash_password(password)
        
        query = "SELECT id FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, hashed_password))
        
        result = cursor.fetchone()
        return result is not None
        
    except Error as e:
        print(f"用户验证错误: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def register_user(username, password):
    """注册新用户"""
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        hashed_password = hash_password(password)
        
        query = "INSERT INTO users (username, password) VALUES (%s, %s)"
        cursor.execute(query, (username, hashed_password))
        
        connection.commit()
        print(f"用户 {username} 注册成功")
        return True
        
    except Error as e:
        if e.errno == 1062:  # 重复键错误
            print(f"用户名 {username} 已存在")
        else:
            print(f"用户注册错误: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def record_login(user_id):
    """记录用户登录"""
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        query = "INSERT INTO login_records (user_id) VALUES (%s)"
        cursor.execute(query, (user_id,))
        
        connection.commit()
        return True
        
    except Error as e:
        print(f"登录记录错误: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def record_recognition(user_id, person_name, confidence):
    """记录人脸识别结果"""
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        query = "INSERT INTO recognition_records (user_id, person_name, confidence) VALUES (%s, %s, %s)"
        cursor.execute(query, (user_id, person_name, confidence))
        
        connection.commit()
        return True
        
    except Error as e:
        print(f"识别记录错误: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_user_id(username):
    """获取用户ID"""
    connection = get_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        
        query = "SELECT id FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        
        result = cursor.fetchone()
        return result[0] if result else None
        
    except Error as e:
        print(f"获取用户ID错误: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_recognition_records(user_id=None, limit=100):
    """获取识别记录"""
    connection = get_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor()
        
        if user_id:
            query = """
            SELECT r.id, u.username, r.person_name, r.recognition_time, r.confidence
            FROM recognition_records r
            JOIN users u ON r.user_id = u.id
            WHERE r.user_id = %s
            ORDER BY r.recognition_time DESC
            LIMIT %s
            """
            cursor.execute(query, (user_id, limit))
        else:
            query = """
            SELECT r.id, u.username, r.person_name, r.recognition_time, r.confidence
            FROM recognition_records r
            JOIN users u ON r.user_id = u.id
            ORDER BY r.recognition_time DESC
            LIMIT %s
            """
            cursor.execute(query, (limit,))
        
        records = cursor.fetchall()
        return records
        
    except Error as e:
        print(f"获取识别记录错误: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_login_records(user_id=None, limit=100):
    """获取登录记录"""
    connection = get_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor()
        
        if user_id:
            query = """
            SELECT l.id, u.username, l.login_time
            FROM login_records l
            JOIN users u ON l.user_id = u.id
            WHERE l.user_id = %s
            ORDER BY l.login_time DESC
            LIMIT %s
            """
            cursor.execute(query, (user_id, limit))
        else:
            query = """
            SELECT l.id, u.username, l.login_time
            FROM login_records l
            JOIN users u ON l.user_id = u.id
            ORDER BY l.login_time DESC
            LIMIT %s
            """
            cursor.execute(query, (limit,))
        
        records = cursor.fetchall()
        return records
        
    except Error as e:
        print(f"获取登录记录错误: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    # 测试数据库连接和初始化
    print("初始化数据库...")
    init_database()
    
    # 测试用户注册
    print("\n测试用户注册...")
    register_user("test_user", "test_password")
    
    # 测试用户验证
    print("\n测试用户验证...")
    if verify_user("test_user", "test_password"):
        print("用户验证成功")
    else:
        print("用户验证失败")
    
    # 测试记录功能
    user_id = get_user_id("test_user")
    if user_id:
        print(f"\n用户ID: {user_id}")
        record_login(user_id)
        record_recognition(user_id, "张三", 85.5)
        
        print("\n登录记录:")
        login_records = get_login_records(user_id)
        for record in login_records:
            print(record)
        
        print("\n识别记录:")
        recognition_records = get_recognition_records(user_id)
        for record in recognition_records:
            print(record)