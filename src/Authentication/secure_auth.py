import sqlite3
import bcrypt
import os
import json
from datetime import datetime
from cryptography.fernet import Fernet
from Data import *
from Data.input_validation import *
from config import DB_FILE, LOG_FILE
from session import *

# Hardcoded super admin credentials
SUPER_ADMIN_USERNAME = "super_admin"
SUPER_ADMIN_PASSWORD = "Admin_123?"

# Hardcoded super admin user data
SUPER_ADMIN_USER = {
    "username": "super_admin",
    "role": "Super Administrator",
    "user_id": 1,
    "first_name": "System",
    "last_name": "Administrator"
}

class SecureAuth:
    def __init__(self):
        self.db_file = DB_FILE
        self.log_file = LOG_FILE
        self._ensure_database()
        self._ensure_log_file()
        self._load_key()

    def _ensure_database(self):
        """Create database and users table if they don't exist"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                registration_date TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def _ensure_log_file(self):
        """Create encrypted log file if it doesn't exist"""
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'wb') as f:
                f.write(b'')

    def _load_key(self):
        """Load or generate encryption key for logs"""
        key_file = 'encryption_key.key'
        if not os.path.exists(key_file):
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
        else:
            with open(key_file, 'rb') as f:
                key = f.read()
        self.fernet = Fernet(key)


    def verify_password(self, password, hashed):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode(), hashed)

    def login(self, username, password):
        """Authenticate user and set session if successful."""
        # Hardcoded super admin login
        if username == SUPER_ADMIN_USERNAME and password == SUPER_ADMIN_PASSWORD:
            set_current_user(SUPER_ADMIN_USER)
            self.log_activity(username, "LOGIN_SUCCESS")
            return True, "Super Administrator login successful"

        conn = None
        cur = None
        try:
            conn = sqlite3.connect(self.db_file)
            cur = conn.cursor()
            cur.execute("SELECT user_id, password_hash, role, first_name, last_name FROM users WHERE username = ?", (username,))
            result = cur.fetchone()
            if not result:
                self._log_activity(username, "LOGIN_FAILED")
                return False, "User not found"

            user_id, password_hash, role, first_name, last_name = result
            if self.verify_password(password, password_hash):
                set_current_user({
                    "username": username,
                    "role": role,
                    "user_id": user_id,
                    "first_name": first_name,
                    "last_name": last_name
                })
                self._log_activity(username, "LOGIN_SUCCESS")
                return True, "Login successful"
            else:
                self._log_activity(username, "LOGIN_FAILED")
                return False, "Incorrect password"
        except Exception as e:
            return False, f"Login error: {str(e)}"
        finally:
            if cur: cur.close()
            if conn: conn.close()

    def log_activity(self, username, action):
        """Log user activity with encryption"""
        log_entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'username': username,
            'action': action
        }
        
        # Initialize logs as empty list first
        logs = []
        
        # Check for suspicious activity
        try:
            with open(self.log_file, 'rb') as f:
                encrypted_data = f.read()
            if encrypted_data:
                decrypted_data = self._decrypt_log(encrypted_data)
                logs = json.loads(decrypted_data)
                
                # Count failed attempts in last 10 minutes
                now = datetime.now()
                failed_count = sum(1 for log in logs[-10:] 
                                if log['username'] == username and
                                log['action'] == 'LOGIN_FAILED' and
                                (now - datetime.fromisoformat(log['timestamp'])).total_seconds() < 600)
                
                if failed_count >= 5:
                    self.log_activity(username, "SUSPICIOUS_ACTIVITY")
        except Exception as e:
            print(f"Error reading logs: {str(e)}")
            logs = []

        logs.append(log_entry)
        encrypted_data = self._encrypt_log(json.dumps(logs))
        
        with open(self.log_file, 'wb') as f:
            f.write(encrypted_data)
        
                
def reset_service_engineer_password():
    """Reset password for a service engineer."""
    print("\n=== Reset Service Engineer Password ===")
    
    # Get list of service engineers
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, first_name, last_name FROM users WHERE role = 'Service Engineer'")
    engineers = cur.fetchall()
    
    if not engineers:
        print("❌ No service engineers found.")
        return False
    
    print("\nAvailable Service Engineers:")
    for i, (user_id, username, first, last) in enumerate(engineers, 1):
        print(f"{i}. {first} {last} ({username})")
    
    choice = input("\nChoose engineer to reset password (1-{}): ".format(len(engineers))).strip()
    if not choice.isdigit() or int(choice) not in range(1, len(engineers) + 1):
        print("❌ Invalid choice.")
        return False
    
    selected_engineer = engineers[int(choice) - 1]
    user_id = selected_engineer[0]
    
    # Generate new password
    new_password = input("Enter new password (12-30 chars): ")
    while not validate_password(new_password):
        new_password = input("❌ Invalid. Enter valid password (12-30 chars): ")
    
    # Update password in database
    password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    cur.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", 
               (password_hash, user_id))
    conn.commit()
    conn.close()
    
    print("✅ Password reset successfully.")
    return True
    