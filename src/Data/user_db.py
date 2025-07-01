import sqlite3
import os
import sys
from datetime import datetime
from crypto import encrypt
from session import get_current_user
import hashlib
from config import DB_FILE

def hash_password(password: str) -> str:
    """Hash the password using SHA-256 (or use bcrypt in main auth layer)."""
    return hashlib.sha256(password.encode()).hexdigest()

def insert_user(username, password, role, first_name, last_name):
    """Insert a new System Admin or Service Engineer into the users table."""

    if role not in ["System Administrator", "Service Engineer"]:
        print("Invalid role.")
        return False, "Invalid role"

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            registration_date TEXT
        )
    ''')

    enc_username = encrypt(username)
    hashed_pw = hash_password(password)
    reg_date = datetime.now().strftime("%Y-%m-%d")

    try:
        cur.execute('''
            INSERT INTO users (username, password_hash, role, first_name, last_name, registration_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (enc_username, hashed_pw, role, first_name, last_name, reg_date))
        conn.commit()
        print(f"[✓] {role} account created successfully.")
        return True, f"{role} account created successfully."
    except sqlite3.IntegrityError:
        print("[!] Username already exists.")
        return False, "Username already exists."
    except Exception as e:
        print(f"[!] Error: {str(e)}")
        return False, f"Error: {str(e)}"
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python user_db.py <username> <password> <role> <first_name> <last_name>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    role = sys.argv[3]
    first_name = sys.argv[4]
    last_name = sys.argv[5]

    success, message = insert_user(username, password, role, first_name, last_name)
    if not success:
        print(f"Error: {message}")
        sys.exit(1)