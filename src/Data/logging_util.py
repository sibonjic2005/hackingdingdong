import sqlite3
from datetime import datetime
from Data.crypto import encrypt

class SystemLogger:
    def __init__(self):
        self.db_path = "data/urban_mobility.db"
        
    def log_activity(self, username, action, details=None, is_suspicious=False, ip=None):
        """Log system activity with automatic encryption"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Encrypt sensitive fields
            enc_username = encrypt(username) if username else None
            enc_action = encrypt(action)
            enc_details = encrypt(details) if details else None
            enc_ip = encrypt(ip) if ip else None
            
            cursor.execute("""
                INSERT INTO system_logs 
                (username, action, details, is_suspicious, ip_address)
                VALUES (?, ?, ?, ?, ?)
            """, (enc_username, enc_action, enc_details, int(is_suspicious), enc_ip))
            
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

# Example usage:
# logger = SystemLogger()
# logger.log_activity("admin_john", "User login", "Successful login")
# logger.log_activity(None, "Failed login", "3 attempts for admin_peter", is_suspicious=True)