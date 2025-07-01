import sqlite3
from datetime import datetime
from Data.crypto import encrypt

class SystemLogger:
    def __init__(self):
        self.db_path = "data/urban_mobility.db"
        
    def log_activity(self, username, action, details=None, is_suspicious=False):
        """Log system activity with automatic encryption"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create logs table if not exists
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
            
            cursor.execute("""
                INSERT INTO system_logs 
                (timestamp, username, action, details, is_suspicious)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, enc_username, enc_action, enc_details, int(is_suspicious)))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database logging error: {e}")
            return False
        except Exception as e:
            print(f"Logging error: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()