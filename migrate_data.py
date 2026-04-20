import sqlite3
import os

# 旧数据库文件
old_db = 'health_data.db'

# 新数据库文件 - 我们迁移到用户1的数据库
new_db = 'health_data_user1.db'

print("开始数据迁移...")

# 检查旧数据库是否存在
if not os.path.exists(old_db):
    print(f"错误：找不到旧数据库文件 {old_db}")
    exit(1)

# 检查新数据库是否存在
if not os.path.exists(new_db):
    print(f"错误：找不到新数据库文件 {new_db}")
    exit(1)

print(f"从 {old_db} 迁移数据到 {new_db}")

# 连接到旧数据库
old_conn = sqlite3.connect(old_db)
old_conn.row_factory = sqlite3.Row
old_cursor = old_conn.cursor()

# 连接到新数据库
new_conn = sqlite3.connect(new_db)
new_cursor = new_conn.cursor()

# 迁移 users 表
print("\n迁移 users 表...")
old_cursor.execute('SELECT * FROM users')
users = old_cursor.fetchall()
for user in users:
    try:
        new_cursor.execute('''
            INSERT INTO users (id, name, created_at) VALUES (?, ?, ?)
        ''', (user['id'], user['name'], user['created_at']))
        print(f"  导入用户: {user['name']}")
    except Exception as e:
        print(f"  警告：用户 {user['name']} 可能已存在，跳过")

# 迁移 blood_pressure 表
print("\n迁移 blood_pressure 表...")
old_cursor.execute('SELECT * FROM blood_pressure')
blood_pressures = old_cursor.fetchall()
for bp in blood_pressures:
    try:
        new_cursor.execute('''
            INSERT INTO blood_pressure (user_id, systolic, diastolic, heart_rate, measure_time, remark)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (bp['user_id'], bp['systolic'], bp['diastolic'], bp['heart_rate'], 
              bp['measure_time'], bp['remark']))
        print(f"  导入血压记录: {bp['systolic']}/{bp['diastolic']}")
    except Exception as e:
        print(f"  错误：无法导入血压记录 - {e}")

# 迁移 uric_acid 表
print("\n迁移 uric_acid 表...")
old_cursor.execute('SELECT * FROM uric_acid')
uric_acids = old_cursor.fetchall()
for ua in uric_acids:
    try:
        new_cursor.execute('''
            INSERT INTO uric_acid (user_id, value, measure_time, remark)
            VALUES (?, ?, ?, ?)
        ''', (ua['user_id'], ua['value'], ua['measure_time'], ua['remark']))
        print(f"  导入血尿酸记录: {ua['value']}")
    except Exception as e:
        print(f"  错误：无法导入血尿酸记录 - {e}")

# 迁移 blood_sugar 表
print("\n迁移 blood_sugar 表...")
old_cursor.execute('SELECT * FROM blood_sugar')
blood_sugars = old_cursor.fetchall()
for bs in blood_sugars:
    try:
        new_cursor.execute('''
            INSERT INTO blood_sugar (user_id, value, fasting, measure_time, remark)
            VALUES (?, ?, ?, ?, ?)
        ''', (bs['user_id'], bs['value'], bs['fasting'], bs['measure_time'], bs['remark']))
        print(f"  导入血糖记录: {bs['value']}")
    except Exception as e:
        print(f"  错误：无法导入血糖记录 - {e}")

# 提交更改
new_conn.commit()

# 关闭连接
old_conn.close()
new_conn.close()

print("\n数据迁移完成！")

# 验证迁移结果
print("\n验证迁移结果:")
conn = sqlite3.connect(new_db)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM blood_pressure')
print(f"  血压记录数: {cursor.fetchone()[0]}")

cursor.execute('SELECT COUNT(*) FROM uric_acid')
print(f"  血尿酸记录数: {cursor.fetchone()[0]}")

cursor.execute('SELECT COUNT(*) FROM blood_sugar')
print(f"  血糖记录数: {cursor.fetchone()[0]}")

conn.close()
