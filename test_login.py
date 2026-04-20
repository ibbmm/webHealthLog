import hashlib
import sqlite3

def test_login():
    conn = sqlite3.connect('health_system.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM system_users WHERE username = ?', ('admin',))
    row = cursor.fetchone()
    print(f"用户信息: {row}")
    
    # 测试密码
    input_password = '123456'
    hashed_input = hashlib.sha256(input_password.encode()).hexdigest()
    print(f"输入密码哈希: {hashed_input}")
    print(f"数据库密码哈希: {row['password']}")
    print(f"密码匹配: {hashed_input == row['password']}")
    
    conn.close()

test_login()
