import sqlite3
from datetime import datetime
from cryptography.fernet import Fernet
import os

class Logger:
    def __init__(self, db_path='data/urban_mobility.db'):
        self.db_path = db_path
        self.key = self._load_encryption_key()
        self.cipher = Fernet(self.key)
        
    def _load_encryption_key(self):
        with open('data/log_key.key', 'rb') as key_file:
            return key_file.read()
    
    def _encrypt_data(self, data):
        if not data:
            return self.cipher.encrypt(b'')
        return self.cipher.encrypt(data.encode())
    
    def _decrypt_data(self, encrypted_data):
        if not encrypted_data:
            return ""
        return self.cipher.decrypt(encrypted_data).decode()
    
    def log_activity(self, username, description, additional_info="", suspicious=False):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            encrypted_user = self._encrypt_data(username)
            encrypted_desc = self._encrypt_data(description)
            encrypted_info = self._encrypt_data(additional_info)
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute('''
                INSERT INTO logs 
                (timestamp, username, action_description, additional_info, is_suspicious)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, encrypted_user, encrypted_desc, encrypted_info, int(suspicious)))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error logging activity: {e}")
            return False
        finally:
            conn.close()
    
    def get_recent_logs(self, limit=50):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT log_id, timestamp, username, action_description, additional_info, is_suspicious
                FROM logs
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            logs = []
            for log in cursor.fetchall():
                logs.append({
                    'id': log[0],
                    'timestamp': log[1],
                    'username': self._decrypt_data(log[2]),
                    'action': self._decrypt_data(log[3]),
                    'info': self._decrypt_data(log[4]),
                    'suspicious': bool(log[5])
                })
            
            return logs
        except Exception as e:
            print(f"Error retrieving logs: {e}")
            return []
        finally:
            conn.close()
    
    def check_suspicious_activity(self, username=None, time_window_minutes=5):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT COUNT(*) FROM logs 
                WHERE is_suspicious = 1
                AND timestamp > datetime('now', ?)
            '''
            params = (f'-{time_window_minutes} minutes',)
            
            if username:
                encrypted_user = self._encrypt_data(username)
                query += ' AND username = ?'
                params += (encrypted_user,)
            
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            
            return count
        except Exception as e:
            print(f"Error checking suspicious activity: {e}")
            return 0
        finally:
            conn.close()