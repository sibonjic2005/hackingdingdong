import sqlite3
import bcrypt
import os
from datetime import datetime
from Data import *
from cryptography.fernet import Fernet
import json
from config import DB_FILE, LOG_FILE

class UserAuth:
    def __init__(self):
        self.db_file = DB_FILE
        self.log_file = LOG_FILE
        self._ensure_database()
        self._ensure_log_file()
        self._load_key()
        self._create_admin_user_if_not_exists()

    def _create_admin_user_if_not_exists(self):
        """Create admin user if it doesn't exist"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        
        # Check if admin user exists
        cur.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("super_admin",))
        if cur.fetchone()[0] == 0:
            # Admin user details
            username = "super_admin"
            password = "Admin_123?"
            role = "Super Administrator"
            first_name = "System"
            last_name = "Administrator"
            registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Hash the password
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            
            # Insert admin user
            cur.execute("""
                INSERT INTO users (username, password_hash, role, first_name, last_name, registration_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, password_hash, role, first_name, last_name, registration_date))
            conn.commit()
            print("✅ Admin user created successfully")
        else:
            print("ℹ️ Admin user already exists")
        
        conn.close()

    def _ensure_database(self):
        """Create database and users table if they don't exist"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
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

    def _encrypt_log(self, data):
        """Encrypt log data"""
        return self.fernet.encrypt(data.encode())

    def _decrypt_log(self, data):
        """Decrypt log data"""
        return self.fernet.decrypt(data).decode()

    def hash_password(self, password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    def verify_password(self, password, hashed):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode(), hashed)

    def register_user(self, username, password):
        """Register a new user"""
        valid, msg = self.validate_username(username)
        if not valid:
            return False, msg

        valid, msg = self.validate_password(password)
        if not valid:
            return False, msg

        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            if cur.fetchone()[0] > 0:
                return False, "Username already exists"

            password_hash = self.hash_password(password)
            registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                INSERT INTO users (username, password_hash, registration_date)
                VALUES (?, ?, ?)
            """, (username, password_hash, registration_date))
            conn.commit()
            
            self.log_activity(username, "REGISTER_SUCCESS")
            return True, "User registered successfully"
        except Exception as e:
            conn.rollback()
            return False, f"Error during registration: {str(e)}"
        finally:
            conn.close()

    def login(self, username, password):
        """Authenticate user"""
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        try:
            cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
            result = cur.fetchone()
            
            if result:
                hashed = result[0]
                if self.verify_password(password, hashed):
                    self.log_activity(username, "LOGIN_SUCCESS")
                    return True, "Login successful"
                else:
                    self.log_activity(username, "LOGIN_FAILED")
                    return False, "Invalid password"
            else:
                self.log_activity(username, "LOGIN_FAILED")
                return False, "User not found"
        except Exception as e:
            return False, f"Error during login: {str(e)}"
        finally:
            conn.close()

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



