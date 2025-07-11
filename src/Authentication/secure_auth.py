import sqlite3
import bcrypt
import os
import json
from datetime import datetime
from Data.crypto import fernet
from Data.input_validation import *
from config import DB_FILE, LOG_FILE
from session import set_current_user
from Data.logging_util import SystemLogger
logger = SystemLogger()

SUPER_ADMIN_USERNAME = "super_admin"
SUPER_ADMIN_PASSWORD = "Admin_123?"

SUPER_ADMIN_USER = {
    "username": SUPER_ADMIN_USERNAME,
    "role": "Super Administrator",
    "user_id": 1,
    "first_name": "System",
    "last_name": "Administrator"
}
def log_activity(self, username, action, details=None):
    """Unified logging using SystemLogger to database"""
    try:
        # Track failed login attempts for suspicious activity detection
        if action == "LOGIN_FAILED":
            # Get recent failed attempts
            conn = sqlite3.connect(self.db_file)
            cur = conn.cursor()
            cur.execute("""
                SELECT COUNT(*) FROM system_logs 
                WHERE username = ? 
                AND action = 'LOGIN_FAILED'
                AND timestamp > datetime('now', '-10 minutes')
            """, (username,))
            failed_attempts = cur.fetchone()[0]
            
            if failed_attempts >= 3:
                logger.log_activity(
                    username, 
                    "SUSPICIOUS_ACTIVITY", 
                    f"Multiple failed logins ({failed_attempts+1})",
                    is_suspicious=True
                )
        
        # Log the actual action
        logger.log_activity(
            username,
            action,
            details,
            is_suspicious=(action == "SUSPICIOUS_ACTIVITY")
        )
        
    except Exception as e:
        print(f"⚠️ Logging error: {str(e)}")
        
class SecureAuth:
    def __init__(self):
        self.db_file = DB_FILE
        self.log_file = LOG_FILE
        self._ensure_database()
        self._ensure_log_file()
        self._create_admin_user_if_not_exists()

    def _ensure_database(self):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
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
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'wb') as f:
                f.write(b'')

    def _create_admin_user_if_not_exists(self):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users WHERE username = ?", (SUPER_ADMIN_USERNAME,))
        if cur.fetchone()[0] == 0:
            password_hash = bcrypt.hashpw(SUPER_ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()
            registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                INSERT INTO users (username, password_hash, role, first_name, last_name, registration_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                SUPER_ADMIN_USERNAME, password_hash, "Super Administrator",
                "System", "Administrator", registration_date
            ))
            conn.commit()
            print("✅ Super Admin aangemaakt")
        conn.close()

    def _encrypt_log(self, data):
        return fernet.encrypt(data.encode())

    def _decrypt_log(self, data):
        return fernet.decrypt(data).decode()

    def verify_password(self, password, hashed):
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def register_user(self, username, password, role, first_name, last_name):
        valid, msg = validate_username(username)
        if not valid:
            return False, msg

        valid, msg = validate_password(password)
        if not valid:
            return False, msg

        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            if cur.fetchone()[0] > 0:
                return False, "❌ Gebruikersnaam bestaat al."

            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            registration_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("""
                INSERT INTO users (username, password_hash, role, first_name, last_name, registration_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, password_hash, role, first_name, last_name, registration_date))
            conn.commit()
            self.log_activity(username, "REGISTER_SUCCESS")
            return True, "✅ Gebruiker succesvol geregistreerd"
        except Exception as e:
            conn.rollback()
            return False, f"❌ Fout bij registratie: {str(e)}"
        finally:
            conn.close()

    def login(self, username, password):
        if username == SUPER_ADMIN_USERNAME and password == SUPER_ADMIN_PASSWORD:
            set_current_user(SUPER_ADMIN_USER)
            logger.log_activity(username, "LOGIN_SUCCESS")
            return True, "✅ Super Administrator login successful"
        logger.log_activity(username, "Super administrator login", "Successful login")

        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        try:
            cur.execute("SELECT user_id, password_hash, role, first_name, last_name FROM users WHERE username = ?", (username,))
            result = cur.fetchone()
            if not result:
                logger.log_activity(username, "LOGIN_FAILED")
                return False, "❌ Gebruiker niet gevonden"
            
            
            

            user_id, password_hash, role, first_name, last_name = result
            if self.verify_password(password, password_hash):
                set_current_user({
                    "username": username,
                    "role": role,
                    "user_id": user_id,
                    "first_name": first_name,
                    "last_name": last_name
                })
                logger.log_activity(username, "LOGIN_SUCCESS")
                return True, "✅ Inloggen geslaagd"
            else:
                logger.log_activity(username, "LOGIN_FAILED")
                return False, "❌ Verkeerd wachtwoord"
            
        except Exception as e:
            return False, f"❌ Fout bij inloggen: {str(e)}"
        finally:
            conn.close()

    # In secure_auth.py, modify the log_activity method to use SystemLogger consistently:



    def reset_service_engineer_password(self):
        print("\n🔧 Reset Service Engineer Password")
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute("SELECT user_id, username, first_name, last_name FROM users WHERE role = 'Service Engineer'")
        engineers = cur.fetchall()

        if not engineers:
            print("❌ Geen service engineers gevonden.")
            return False

        print("\nBeschikbare Service Engineers:")
        for i, (user_id, username, first, last) in enumerate(engineers, 1):
            print(f"{i}. {first} {last} ({username})")

        choice = input(f"\nKies een engineer (1-{len(engineers)}): ").strip()
        if not choice.isdigit() or int(choice) not in range(1, len(engineers) + 1):
            print("❌ Ongeldige keuze.")
            return False

        selected = engineers[int(choice) - 1]
        user_id = selected[0]
        new_password = input("Nieuw wachtwoord (12-30 tekens): ")
        while not validate_password(new_password):
            new_password = input("❌ Ongeldig. Probeer opnieuw: ")

        password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        cur.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (password_hash, user_id))
        conn.commit()
        conn.close()

        print("✅ Wachtwoord succesvol gereset.")
        return True