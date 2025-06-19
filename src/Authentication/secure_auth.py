import sqlite3
import bcrypt
import os
from datetime import datetime
from cryptography.fernet import Fernet
import json
from config import DB_FILE, LOG_FILE

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

    def _encrypt_log(self, data):
        """Encrypt log data"""
        return self.fernet.encrypt(data.encode())

    def _decrypt_log(self, data):
        """Decrypt log data"""
        return self.fernet.decrypt(data).decode()

    def validate_username(self, username):
        """Validate username format"""
        if not 8 <= len(username) <= 10:
            return False, "Username must be between 8 and 10 characters"
        if not (username[0].isalpha() or username[0] == '_'):
            return False, "Username must start with a letter or underscore"
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'")
        if not all(c in allowed_chars for c in username):
            return False, "Username can only contain letters, numbers, _, ' or ."
        return True, ""

    def validate_password(self, password):
        """Validate password format"""
        if not 12 <= len(password) <= 30:
            return False, "Password must be between 12 and 30 characters"
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        special_chars = set("~!@#$%&_-+=")
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character (~!@#$%&_-+=)"
        return True, ""

    def hash_password(self, password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    def verify_password(self, password, hashed):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode(), hashed)

    def login(self, username, password):
        """Authenticate user and return success status and message"""
        conn = None
        cur = None
        try:
            conn = sqlite3.connect(self.db_file)
            cur = conn.cursor()
            
            # Get user record
            cur.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
            result = cur.fetchone()
            
            if not result:
                return False, "User not found"
                
            password_hash = result[0]
            if self.verify_password(password, password_hash):
                self._log_activity(username, "LOGIN_SUCCESS")
                return True, "Login successful"
            else:
                self._log_activity(username, "LOGIN_FAILED")
                return False, "Invalid password"
                
        except sqlite3.Error as e:
            return False, f"Database error: {str(e)}"
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    def register_user(self, username, password):
        """Register a new user"""
        valid, msg = self.validate_username(username)
        if not valid:
            return False, msg

        valid, msg = self.validate_password(password)
        if not valid:
            return False, msg

        conn = None
        cur = None

        try:
            conn = sqlite3.connect(self.db_file)
            cur = conn.cursor()

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
            self._log_activity(username, "REGISTER_SUCCESS")
            return True, "User registered successfully"

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
            return False, f"Database error: {str(e)}"

        except Exception as e:
            if conn:
                conn.rollback()
            return False, f"Error during registration: {str(e)}"

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
            conn.close()
