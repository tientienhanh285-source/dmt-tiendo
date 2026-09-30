import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'kpi_system.db')

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.username, u.full_name, u.role, d.name as department_name, d.id as department_id 
        FROM Users u
        LEFT JOIN Departments d ON u.department_id = d.id
    ''')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.id, u.username, u.full_name, u.role, d.name as department_name, d.id as department_id
        FROM Users u
        LEFT JOIN Departments d ON u.department_id = d.id
        WHERE u.username = ?
    ''', (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_master_plans_by_dept(department_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM MasterPlans WHERE department_id = ?', (department_id,))
    plans = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return plans

def get_indicators_by_plan(plan_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Indicators WHERE master_plan_id = ?', (plan_id,))
    indicators = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return indicators

def create_task(task_name, indicator_id, assignee_id, deadline):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Tasks (task_name, indicator_id, assignee_id, status, deadline)
        VALUES (?, ?, ?, 'Đang làm', ?)
    ''', (task_name, indicator_id, assignee_id, deadline))
    conn.commit()
    conn.close()
    return True

def get_tasks_by_assignee(assignee_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT t.*, i.name as indicator_name 
        FROM Tasks t
        LEFT JOIN Indicators i ON t.indicator_id = i.id
        WHERE t.assignee_id = ?
    ''', (assignee_id,))
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tasks
