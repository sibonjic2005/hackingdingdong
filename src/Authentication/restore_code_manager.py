# src/Authentication/restore_code_manager.py
import sqlite3
import secrets
from datetime import datetime

from Data.user_auth import UserAuth
from session import get_current_user

DB_PATH = "data/urban_mobility.db"
CODE_EXPIRY_HOURS = 24  # Codes expire after 24 hours

def generate_restore_code(backup_filename=None):
    """Generate a one-time use restore code for a specific backup"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # If backup filename not provided, show available backups
        if not backup_filename:
            from Data.backup_handler import list_available_backups
            backups = list_available_backups()
            if not backups:
                return None
                
            print("\nSelect a backup to generate code for:")
            for i, backup in enumerate(backups, 1):
                print(f"{i}. {backup}")
                
            choice = input("\nEnter backup number: ")
            try:
                backup_filename = backups[int(choice)-1]
            except (ValueError, IndexError):
                print("❌ Invalid selection")
                return None

        # Verify backup exists
        backup_path = f"data/backups/{backup_filename}"
        if not os.path.exists(backup_path):
            print(f"❌ Backup file not found: {backup_filename}")
            return None

        # Get current admin user
        current_user = get_current_user()
        if not current_user or current_user['role'] != 'Super Administrator':
            print("❌ Only Super Administrators can generate restore codes")
            return None

        # Generate secure 16-character code
        restore_code = secrets.token_hex(8)  # 16 characters
        expiry_time = (datetime.now() + 
                      timedelta(hours=CODE_EXPIRY_HOURS)).strftime("%Y-%m-%d %H:%M:%S")

        # Store code in database
        cursor.execute("""
            INSERT INTO restore_codes 
            (code, backup_file, created_by, created_at, expires_at, is_used)
            VALUES (?, ?, ?, datetime('now'), ?, 0)
        """, (restore_code, backup_filename, current_user['username'], expiry_time))
        
        conn.commit()
        
        # Log the action
        log_activity(
            current_user['username'],
            "Generated restore code",
            f"Backup: {backup_filename}"
        )
        
        print(f"\n✅ Restore code generated successfully")
        print(f"Code: {restore_code}")
        print(f"Expires: {expiry_time}")
        print(f"Backup: {backup_filename}")
        
        return restore_code
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None
    finally:
        conn.close() if 'conn' in locals() else None

def validate_restore_code(code):
    """Check if a restore code is valid and unused"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT code_id, backup_file, expires_at 
            FROM restore_codes 
            WHERE code = ? 
            AND is_used = 0
            AND datetime(expires_at) > datetime('now')
        """, (code,))
        
        result = cursor.fetchone()
        if not result:
            return None
            
        return {
            'code_id': result[0],
            'backup_file': result[1],
            'expires_at': result[2]
        }
        
    except sqlite3.Error:
        return None
    finally:
        conn.close() if 'conn' in locals() else None