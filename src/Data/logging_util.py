import sqlite3
from datetime import datetime
from Data.crypto import encrypt

# In Data/logging_util.py
import sqlite3
from datetime import datetime
from Data.crypto import encrypt, decrypt  # Make sure these exist

class SystemLogger:
    def __init__(self):
        self.db_path = "data/urban_mobility.db"
        
    def log_activity(self, username, action, details=None, is_suspicious=False):
        """Log activity with automatic encryption"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    username TEXT,
                    action TEXT NOT NULL,
                    details TEXT,
                    is_suspicious INTEGER DEFAULT 0
                )
            ''')
            
            # Encrypt sensitive fields
            enc_username = encrypt(username) if username else None
            enc_action = encrypt(action)
            enc_details = encrypt(details) if details else None
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            cursor.execute('''
                INSERT INTO system_logs 
                (timestamp, username, action, details, is_suspicious)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, enc_username, enc_action, enc_details, int(is_suspicious)))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Logging error: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    def get_logs(self, limit=50):
        """Retrieve and decrypt logs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT log_id, timestamp, username, action, details, is_suspicious
                FROM system_logs
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            logs = []
            for log in cursor.fetchall():
                try:
                    logs.append({
                        'id': log[0],
                        'timestamp': log[1],
                        'username': decrypt(log[2]) if log[2] else "SYSTEM",
                        'action': decrypt(log[3]),
                        'details': decrypt(log[4]) if log[4] else "",
                        'suspicious': bool(log[5])
                    })
                except Exception as e:
                    print(f"Failed to decrypt log {log[0]}: {e}")
                    continue
            return logs
        except Exception as e:
            print(f"Error retrieving logs: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()