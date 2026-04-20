from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

DATABASE = 'health_data.db'
PASSWORD_FILE = 'password.txt'

def get_password():
    """从文件读取密码"""
    if os.path.exists(PASSWORD_FILE):
        try:
            with open(PASSWORD_FILE, 'r') as f:
                return f.read().strip()
        except:
            pass
    return '123456'  # 默认密码

def save_password(password):
    """保存密码到文件"""
    try:
        with open(PASSWORD_FILE, 'w') as f:
            f.write(password)
        return True
    except:
        return False

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
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
    
    # 插入默认用户
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO users (name) VALUES (?)', ('默认用户',))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == get_password():
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='密码错误')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/api/users', methods=['GET'])
def get_users():
    if 'logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    conn = get_db()
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
    conn = get_db()
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
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET name = ? WHERE id = ?', (data['name'], id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    if 'logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    conn = get_db()
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
    conn = get_db()
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
    conn = get_db()
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
    conn = get_db()
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
    
    conn = get_db()
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
    
    conn = get_db()
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
    
    conn = get_db()
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
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM blood_pressure WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/uric-acid/<int:id>', methods=['DELETE'])
def delete_uric_acid(id):
    if 'logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM uric_acid WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/blood-sugar/<int:id>', methods=['DELETE'])
def delete_blood_sugar(id):
    if 'logged_in' not in session:
        return jsonify({'error': '未登录'}), 401
    
    conn = get_db()
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
    
    if os.path.exists(DATABASE):
        return send_file(DATABASE, as_attachment=True, download_name='health_data.db')
    else:
        return jsonify({'error': '数据库文件不存在'}), 404

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)
