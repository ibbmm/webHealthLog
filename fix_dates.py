import sqlite3
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')

# 更新所有数据库中的日期
dbs = ['health_data_user1.db', 'health_data_user3.db']

for db in dbs:
    print(f"更新数据库: {db}")
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    
    # 更新血压
    cursor.execute('UPDATE blood_pressure SET measure_time = ?', (f'{today}T12:00',))
    print(f"  更新了 {cursor.rowcount} 条血压记录")
    
    # 更新血尿酸
    cursor.execute('UPDATE uric_acid SET measure_time = ?', (f'{today}T12:00',))
    print(f"  更新了 {cursor.rowcount} 条血尿酸记录")
    
    # 更新血糖
    cursor.execute('UPDATE blood_sugar SET measure_time = ?', (f'{today}T12:00',))
    print(f"  更新了 {cursor.rowcount} 条血糖记录")
    
    conn.commit()
    conn.close()

print("完成！")
