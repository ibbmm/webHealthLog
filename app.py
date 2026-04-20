from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import sqlite3
from datetime import datetime, timedelta
import os
import hashlib

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# 系统数据库（存储用户信息和系统设置）
SYSTEM_DATABASE = 'health_system.db'
# 高级设置默认密码
DEFAULT_ADVANCED_PASSWORD = 'Cdfle1898'

# 密码文件（存储登录密码）
PASSWORD_FILE = 'password.txt'

# 生成用户数据库文件名
def get_user_database(user_id):
    return f'health_data_user{user_id}.db'

# 加密密码
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 从文件读取登录密码
def get_password():
    """从文件读取密码"""
    if os.path.exists(PASSWORD_FILE):
        try:
            with open(PASSWORD_FILE, 'r') as f:
                return f.read().strip()
        except:
            pass
    return '123456'  # 默认密码

# 保存登录密码
def save_password(password):
    """保存密码到文件"""
    try:
        with open(PASSWORD_FILE, 'w') as f:
            f.write(password)
        return True
    except:
        return False

# 初始化系统数据库
def init_system_db():
    conn = sqlite3.connect(SYSTEM_DATABASE)
    cursor = conn.cursor()
    
    # 创建系统用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建系统设置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL UNIQUE,
            value TEXT NOT NULL
        )
    ''')
    
    # 插入默认系统用户
    cursor.execute('SELECT COUNT(*) FROM system_users')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO system_users (username, password) VALUES (?, ?)', ('admin', hash_password('123456')))
    
    # 插入默认高级设置密码
    cursor.execute('SELECT COUNT(*) FROM system_settings WHERE key = ?', ('advanced_password',))
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO system_settings (key, value) VALUES (?, ?)', ('advanced_password', hash_password(DEFAULT_ADVANCED_PASSWORD)))
    
    conn.commit()
    conn.close()

# 初始化用户数据库
def init_user_db(user_id):
    db_file = get_user_database(user_id)
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 创建用户表（归属人）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建血压表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blood_pressure (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            systolic INTEGER NOT NULL,
            diastolic INTEGER NOT NULL,
            heart_rate INTEGER,
            measure_time TEXT NOT NULL,
            remark TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # 创建血尿酸表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uric_acid (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            value REAL NOT NULL,
            measure_time TEXT NOT NULL,
            remark TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # 创建血糖表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blood_sugar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            value REAL NOT NULL,
            fasting INTEGER NOT NULL,
            measure_time TEXT NOT NULL,
            remark TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # 插入默认归属人
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO users (name) VALUES (?)', ('默认用户',))
    
    conn.commit()
    conn.close()

# 获取系统数据库连接
def get_system_db():
    conn = sqlite3.connect(SYSTEM_DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# 获取用户数据库连接
def get_user_db():
    user_id = session.get('user_id')
    if not user_id:
        return None
    db_file = get_user_database(user_id)
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

# 验证高级设置密码
def verify_advanced_password(password):
    conn = get_system_db()
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM system_settings WHERE key = ?', ('advanced_password',))
    row = cursor.fetchone()
    conn.close()
    if row:
        return hash_password(password) == row['value']
    return False

# 更新高级设置密码
def update_advanced_password(new_password):
    conn = get_system_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE system_settings SET value = ? WHERE key = ?', (hash_password(new_password), 'advanced_password'))
    conn.commit()
    conn.close()

# 验证系统用户密码
def verify_system_user(username, password):
    conn = get_system_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM system_users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return hash_password(password) == row['password']
    return False

# 添加系统用户
def add_system_user(username, password):
    conn = get_system_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO system_users (username, password) VALUES (?, ?)', (username, hash_password(password)))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# 更新系统用户密码
def update_system_user_password(user_id, new_password):
    conn = get_system_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE system_users SET password = ? WHERE id = ?', (hash_password(new_password), user_id))
    conn.commit()
    conn.close()

# 删除系统用户
def delete_system_user(user_id):
    conn = get_system_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM system_users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

# 获取所有系统用户
def get_system_users():
    conn = get_system_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM system_users ORDER BY id')
    rows = cursor.fetchall()
    conn.close()
    return rows

@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        
        if verify_system_user(username, password):
            # 验证成功，获取用户ID
            conn = get_system_db()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM system_users WHERE username = ?', (username,))
            user_id = cursor.fetchone()['id']
            conn.close()
            
            # 设置会话
            session['logged_in'] = True
            session['username'] = username
            session['user_id'] = user_id
            
            # 记住登录状态
            if remember:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=30)
            
            # 保存上次登录的用户名
            import json
            try:
                with open('last_login.json', 'w') as f:
                    json.dump({'username': username}, f)
            except:
                pass
            
            # 初始化用户数据库
            init_user_db(user_id)
            
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='用户名或密码错误')
    
    # 加载上次登录的用户名
    username = ''
    import json
    try:
        with open('last_login.json', 'r') as f:
            data = json.load(f)
            username = data.get('username', '')
    except:
        pass
    
    return render_template('login.html', username=username)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/advanced-settings', methods=['GET', 'POST'])
def advanced_settings():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if verify_advanced_password(password):
            session['advanced_logged_in'] = True
            return redirect(url_for('advanced_settings_panel'))
        else:
            return render_template('advanced_login.html', error='密码错误')
    return render_template('advanced_login.html')

@app.route('/advanced-settings-panel')
def advanced_settings_panel():
    if 'advanced_logged_in' not in session:
        return redirect(url_for('advanced_settings'))
    return render_template('advanced_settings.html')

@app.route('/api/advanced/logout')
def advanced_logout():
    session.pop('advanced_logged_in', None)
    return redirect(url_for('advanced_settings'))

# 初始化系统
init_system_db()

@app.route('/api/users', methods=['GET'])
def get_users():
    if 'logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    conn = get_user_db()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
    
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY id')
    rows = cursor.fetchall()
    
    result = []
    for row in rows:
        result.append({
            'id': row['id'],
            'name': row['name']
        })
    
    conn.close()
    return jsonify(result)

@app.route('/api/users', methods=['POST'])
def add_user():
    if 'logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    data = request.json
    conn = get_user_db()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
    
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name) VALUES (?)', (data['name'],))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'id': cursor.lastrowid})

@app.route('/api/users/<int:id>', methods=['PUT'])
def update_user(id):
    if 'logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    data = request.json
    conn = get_user_db()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
    
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET name = ? WHERE id = ?', (data['name'], id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    if 'logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    conn = get_user_db()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
    
    cursor = conn.cursor()
    
    # 检查是否有相关的健康记录
    cursor.execute('SELECT COUNT(*) FROM blood_pressure WHERE user_id = ?', (id,))
    if cursor.fetchone()[0] > 0:
        return jsonify({'error': '该用户有健康记录，无法删除'}), 400
    
    cursor.execute('SELECT COUNT(*) FROM uric_acid WHERE user_id = ?', (id,))
    if cursor.fetchone()[0] > 0:
        return jsonify({'error': '该用户有健康记录，无法删除'}), 400
    
    cursor.execute('SELECT COUNT(*) FROM blood_sugar WHERE user_id = ?', (id,))
    if cursor.fetchone()[0] > 0:
        return jsonify({'error': '该用户有健康记录，无法删除'}), 400
    
    cursor.execute('DELETE FROM users WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/blood-pressure', methods=['POST'])
def add_blood_pressure():
    if 'logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    data = request.json
    conn = get_user_db()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
    
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO blood_pressure (user_id, systolic, diastolic, heart_rate, measure_time, remark)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['user_id'], data['systolic'], data['diastolic'], data.get('heart_rate'), 
          data['measure_time'], data.get('remark')))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'id': cursor.lastrowid})

@app.route('/api/uric-acid', methods=['POST'])
def add_uric_acid():
    if 'logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    data = request.json
    conn = get_user_db()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
    
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO uric_acid (user_id, value, measure_time, remark)
        VALUES (?, ?, ?, ?)
    ''', (data['user_id'], data['value'], data['measure_time'], data.get('remark')))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'id': cursor.lastrowid})

@app.route('/api/blood-sugar', methods=['POST'])
def add_blood_sugar():
    if 'logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    data = request.json
    conn = get_user_db()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
    
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO blood_sugar (user_id, value, fasting, measure_time, remark)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['user_id'], data['value'], data['fasting'], 
          data['measure_time'], data.get('remark')))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'id': cursor.lastrowid})

@app.route('/api/blood-pressure', methods=['GET'])
def get_blood_pressure():
    if 'logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    user_id = request.args.get('user_id')
    
    conn = get_user_db()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
    
    cursor = conn.cursor()
    
    query = 'SELECT * FROM blood_pressure'
    params = []
    
    conditions = []
    if user_id:
        conditions.append('user_id = ?')
        params.append(user_id)
    if start_date and end_date:
        conditions.append('measure_time BETWEEN ? AND ?')
        params.extend([start_date + 'T00:00:00', end_date + 'T23:59:59'])
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += ' ORDER BY measure_time DESC'
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    result = []
    for row in rows:
        result.append({
            'id': row['id'],
            'user_id': row['user_id'],
            'systolic': row['systolic'],
            'diastolic': row['diastolic'],
            'heart_rate': row['heart_rate'],
            'measure_time': row['measure_time'],
            'remark': row['remark']
        })
    
    conn.close()
    return jsonify(result)

@app.route('/api/uric-acid', methods=['GET'])
def get_uric_acid():
    if 'logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    user_id = request.args.get('user_id')
    
    conn = get_user_db()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
    
    cursor = conn.cursor()
    
    query = 'SELECT * FROM uric_acid'
    params = []
    
    conditions = []
    if user_id:
        conditions.append('user_id = ?')
        params.append(user_id)
    if start_date and end_date:
        conditions.append('measure_time BETWEEN ? AND ?')
        params.extend([start_date + 'T00:00:00', end_date + 'T23:59:59'])
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += ' ORDER BY measure_time DESC'
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    result = []
    for row in rows:
        result.append({
            'id': row['id'],
            'user_id': row['user_id'],
            'value': row['value'],
            'measure_time': row['measure_time'],
            'remark': row['remark']
        })
    
    conn.close()
    return jsonify(result)

@app.route('/api/blood-sugar', methods=['GET'])
def get_blood_sugar():
    if 'logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    user_id = request.args.get('user_id')
    
    conn = get_user_db()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
    
    cursor = conn.cursor()
    
    query = 'SELECT * FROM blood_sugar'
    params = []
    
    conditions = []
    if user_id:
        conditions.append('user_id = ?')
        params.append(user_id)
    if start_date and end_date:
        conditions.append('measure_time BETWEEN ? AND ?')
        params.extend([start_date + 'T00:00:00', end_date + 'T23:59:59'])
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += ' ORDER BY measure_time DESC'
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    result = []
    for row in rows:
        result.append({
            'id': row['id'],
            'user_id': row['user_id'],
            'value': row['value'],
            'fasting': row['fasting'],
            'measure_time': row['measure_time'],
            'remark': row['remark']
        })
    
    conn.close()
    return jsonify(result)

@app.route('/api/blood-pressure/<int:id>', methods=['DELETE'])
def delete_blood_pressure(id):
    if 'logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    conn = get_user_db()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
    
    cursor = conn.cursor()
    cursor.execute('DELETE FROM blood_pressure WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/uric-acid/<int:id>', methods=['DELETE'])
def delete_uric_acid(id):
    if 'logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    conn = get_user_db()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
    
    cursor = conn.cursor()
    cursor.execute('DELETE FROM uric_acid WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/blood-sugar/<int:id>', methods=['DELETE'])
def delete_blood_sugar(id):
    if 'logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    conn = get_user_db()
    if not conn:
        return jsonify({'error': '数据库连接失败'}), 500
    
    cursor = conn.cursor()
    cursor.execute('DELETE FROM blood_sugar WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/change-password', methods=['POST'])
def change_password():
    if 'logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if current_password != get_password():
        return jsonify({'error': '当前密码错误'}), 400
    
    if not new_password or len(new_password) < 6:
        return jsonify({'error': '新密码长度至少6位'}), 400
    
    if save_password(new_password):
        return jsonify({'success': True, 'message': '密码修改成功'})
    else:
        return jsonify({'error': '密码保存失败'}), 500

@app.route('/api/backup')
def backup_data():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    import os
    from flask import send_file
    
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '用户未登录'}), 401
    
    db_file = get_user_database(user_id)
    if os.path.exists(db_file):
        return send_file(db_file, as_attachment=True, download_name=f'health_data_user{user_id}.db')
    else:
        return jsonify({'error': '数据库文件不存在'}), 404

# 高级设置API
@app.route('/api/advanced/users', methods=['GET'])
def get_advanced_users():
    if 'advanced_logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    users = get_system_users()
    result = []
    for user in users:
        result.append({
            'id': user['id'],
            'username': user['username'],
            'created_at': user['created_at']
        })
    return jsonify(result)

@app.route('/api/advanced/users', methods=['POST'])
def add_advanced_user():
    if 'advanced_logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    if add_system_user(username, password):
        return jsonify({'success': True})
    else:
        return jsonify({'error': '用户名已存在'}), 400

@app.route('/api/advanced/users/<int:id>', methods=['PUT'])
def update_advanced_user(id):
    if 'advanced_logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    data = request.json
    new_password = data.get('password')
    
    if not new_password:
        return jsonify({'error': '密码不能为空'}), 400
    
    update_system_user_password(id, new_password)
    return jsonify({'success': True})

@app.route('/api/advanced/users/<int:id>', methods=['DELETE'])
def delete_advanced_user(id):
    if 'advanced_logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    delete_system_user(id)
    return jsonify({'success': True})

@app.route('/api/advanced/settings', methods=['PUT'])
def update_advanced_settings():
    if 'advanced_logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    data = request.json
    new_password = data.get('advanced_password')
    
    if not new_password:
        return jsonify({'error': '密码不能为空'}), 400
    
    update_advanced_password(new_password)
    return jsonify({'success': True})

@app.route('/api/advanced/backup')
def backup_system_data():
    if 'advanced_logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    import os
    from flask import send_file
    
    if os.path.exists(SYSTEM_DATABASE):
        return send_file(SYSTEM_DATABASE, as_attachment=True, download_name='health_system.db')
    else:
        return jsonify({'error': '系统数据库文件不存在'}), 404

if __name__ == '__main__':
    init_system_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
