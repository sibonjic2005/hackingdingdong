import sqlite3
from config import DB_FILE
import bcrypt
from session import set_current_user

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

def verify_admin_credentials(username, password):
    """Verify admin credentials - checks both hardcoded super admin and database users"""
    # First check if it's the hardcoded super admin
    if username == SUPER_ADMIN_USERNAME and password == SUPER_ADMIN_PASSWORD:
        set_current_user(SUPER_ADMIN_USER)
        return True

    # If not super admin, check database users
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        
        # Get user from database
        cur.execute("SELECT user_id, password_hash, role, first_name, last_name FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        
        if row:
            user_id, password_hash, role, first_name, last_name = row
            # Verify password
            if bcrypt.checkpw(password.encode(), password_hash.encode()):
                user_data = {
                    "username": username,
                    "role": role,
                    "user_id": user_id,
                    "first_name": first_name,
                    "last_name": last_name
                }
                set_current_user(user_data)
                return True
    except Exception as e:
        print(f"❌ Error verifying credentials: {str(e)}")
    finally:
        try:
            conn.close()
        except:
            pass
    
    return False