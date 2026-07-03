import sqlite3
import os
from datetime import datetime
from config import DB_PATH

class Database:
    """کلاس برای مدیریت پایگاه داده SQLite"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        """اتصال به پایگاه داده"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """ایجاد جداول پایگاه داده"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # جدول کاربران
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                family_name TEXT NOT NULL,
                age INTEGER,
                job TEXT,
                phone TEXT,
                email TEXT,
                image_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول دسترسی‌ها
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                status TEXT,
                emotion TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                image_path TEXT,
                confidence REAL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, name, family_name, age, job, phone, email, image_path):
        """اضافه کردن کاربر جدید"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (name, family_name, age, job, phone, email, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, family_name, age, job, phone, email, image_path))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id, True, "کاربر با موفقیت ثبت شد"
        except sqlite3.IntegrityError:
            return None, False, "این نام قبلاً ثبت شده است"
        except Exception as e:
            return None, False, f"خطا: {str(e)}"
    
    def get_user_by_name(self, name):
        """دریافت کاربر بر اساس نام"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE name = ?', (name,))
        user = cursor.fetchone()
        conn.close()
        
        return dict(user) if user else None
    
    def get_all_users(self):
        """دریافت تمام کاربران"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        conn.close()
        
        return [dict(user) for user in users]
    
    def log_access(self, user_id, status, emotion, image_path, confidence):
        """ثبت دسترسی"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO access_logs (user_id, status, emotion, image_path, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, status, emotion, image_path, confidence))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"خطا در ثبت دسترسی: {str(e)}")
            return False
    
    def log_unauthorized_access(self, status, emotion, image_path, confidence):
        """ثبت دسترسی غیرمجاز"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO access_logs (user_id, status, emotion, image_path, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (None, status, emotion, image_path, confidence))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"خطا در ثبت دسترسی غیرمجاز: {str(e)}")
            return False
    
    def get_access_logs(self, days=7):
        """دریافت لاگ دسترسی‌های اخیر"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM access_logs 
            WHERE datetime(timestamp) >= datetime('now', '-' || ? || ' days')
            ORDER BY timestamp DESC
        ''', (days,))
        
        logs = cursor.fetchall()
        conn.close()
        
        return [dict(log) for log in logs]
    
    def delete_user(self, user_id):
        """حذف کاربر"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True, "کاربر با موفقیت حذف شد"
        except Exception as e:
            return False, f"خطا: {str(e)}"
    
    def update_user(self, user_id, **kwargs):
        """بروزرسانی اطلاعات کاربر"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            allowed_fields = ['family_name', 'age', 'job', 'phone', 'email', 'image_path']
            update_fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
            
            if not update_fields:
                return False, "هیچ فیلدی برای بروزرسانی نیست"
            
            set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
            values = list(update_fields.values()) + [user_id]
            
            cursor.execute(f'UPDATE users SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?', values)
            conn.commit()
            conn.close()
            return True, "کاربر با موفقیت بروزرسانی شد"
        except Exception as e:
            return False, f"خطا: {str(e)}"

# نمونه استفاده
if __name__ == "__main__":
    db = Database()
    print("پایگاه داده آماده است!")
