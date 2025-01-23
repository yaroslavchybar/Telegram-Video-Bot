import sqlite3
from datetime import datetime

from data.cfg import DATABASE


def initialize_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            usage_count INTEGER DEFAULT 0,
            registration_date TEXT
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS error_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            error_message TEXT,
            timestamp TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')
    conn.commit()


def add_user(user_id: int, username: str, first_name: str):
    registration_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, registration_date)
        VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, registration_date))
        conn.commit()


def usage(user_id):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE users SET usage_count = usage_count + 1
        WHERE user_id = ?
        ''', (user_id,))
        conn.commit()


def error(user_id, username, error_message):
    timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO error_logs (user_id, username, error_message, timestamp)
        VALUES (?, ?, ?, ?)
        ''', (user_id, username, error_message, timestamp))
        conn.commit()


def errors_count() -> int:
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM error_logs')
        count = cursor.fetchone()[0]
    return count


def statistics():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        total_users = cursor.fetchone()[0]
        cursor.execute('SELECT SUM(usage_count) FROM users')
        total_usage = cursor.fetchone()[0]
        return total_users, total_usage


def get_all_errors(limit: int = None):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        query = '''
        SELECT username, error_message, timestamp
        FROM error_logs
        ORDER BY timestamp DESC
        '''
        if limit:
            query += ' LIMIT ?'
            cursor.execute(query, (limit,))
        else:
            cursor.execute(query)

        errors = cursor.fetchall()
        return [
            {
                'username': error[0],
                'error_message': error[1],
                'timestamp': error[2]
            }
            for error in errors
        ]
