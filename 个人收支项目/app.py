from flask import Flask, render_template, request, jsonify
import sqlite3
import os

# 初始化Flask应用
app = Flask(__name__)


# 初始化数据库（首次运行自动创建表）
def init_db():
    # 连接SQLite数据库（文件不存在则自动创建）
    conn = sqlite3.connect('expense.db')
    cursor = conn.cursor()
    # 创建收支表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        amount FLOAT NOT NULL, 
        description TEXT, 
        create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
    )
    ''')
    conn.commit()
    conn.close()


# 首页路由：返回前端页面
@app.route('/')
def index():
    return render_template('index.html')


# 新增收支记录接口
@app.route('/add_record', methods=['POST'])
def add_record():
    try:
        # 获取前端提交的数据
        data = request.get_json()
        record_type = data.get('type')
        amount = float(data.get('amount'))
        description = data.get('description', '')

        # 插入数据库
        conn = sqlite3.connect('expense.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO records (type, amount, description) VALUES (?, ?, ?)',
            (record_type, amount, description)
        )
        conn.commit()
        conn.close()

        return jsonify({'code': 200, 'msg': '记录添加成功'})
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'添加失败：{str(e)}'})


# 获取所有收支记录接口
@app.route('/get_records', methods=['GET'])
def get_records():
    try:
        conn = sqlite3.connect('expense.db')
        cursor = conn.cursor()
        # 查询所有记录并按时间倒序排列
        cursor.execute('SELECT * FROM records ORDER BY create_time DESC')
        # 获取字段名（方便前端解析）
        columns = [desc[0] for desc in cursor.description]
        # 转换为字典列表
        records = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()

        # 计算总收入、总支出、余额
        total_income = sum([r['amount'] for r in records if r['type'] == '收入'])
        total_expense = sum([r['amount'] for r in records if r['type'] == '支出'])
        balance = total_income - total_expense

        return jsonify({
            'code': 200,
            'data': records,
            'summary': {
                'income': total_income,
                'expense': total_expense,
                'balance': balance
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'查询失败：{str(e)}'})


# 程序入口
if __name__ == '__main__':
    init_db()
    # 适配部署平台的端口和地址
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)  # 关闭debug模式，避免安全风险