# src/Authentication/restore_code_manager.py
import sqlite3
import secrets
import os
from datetime import datetime, timedelta
from pathlib import Path
from Data.user_auth import UserAuth
from session import get_current_user

DB_PATH = os.path.join("data", "urban_mobility.db")
CODE_EXPIRY_HOURS = 24  # Codes expire after 24 hours
BACKUP_DIR = os.path.join("data", "backups")

# Initialize UserAuth
user_auth = UserAuth()

def generate_restore_code(backup_filename=None):
    """Generate a one-time use restore code for a specific backup"""
    conn = None
    try:
        # Ensure backup directory exists
        Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Create restore_codes table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS restore_codes (
                code_id INTEGER PRIMARY KEY,
                code TEXT UNIQUE NOT NULL,
                backup_file TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                is_used INTEGER DEFAULT 0
            )
        """)
        
        # If backup filename not provided, show available backups
        if not backup_filename:
            from Data.backup_handler import list_available_backups
            backups_result = list_available_backups()
            
            if not backups_result['success']:
                print(f"❌ Error listing backups: {backups_result.get('error', 'Unknown error')}")
                return None
                
            backups = backups_result['backups']
            if not backups:
                print("❌ No valid backup files found in backup directory")
                print(f"Checked directory: {os.path.abspath(BACKUP_DIR)}")
                return None
                
            print("\nAvailable Backups:")
            for i, backup in enumerate(backups, 1):
                print(f"{i}. {backup}")
                
            try:
                choice = int(input("\nEnter backup number: "))
                if choice < 1 or choice > len(backups):
                    raise ValueError
                backup_filename = backups[choice-1]
            except (ValueError, IndexError):
                print("❌ Invalid selection - please enter a valid number")
                return None

        # Verify backup exists and is valid
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        if not os.path.exists(backup_path):
            print(f"❌ Backup file not found at: {os.path.abspath(backup_path)}")
            return None
        if os.path.getsize(backup_path) <= 0:
            print(f"❌ Backup file is empty: {backup_filename}")
            return None

        # Get current admin user
        current_user = get_current_user()
        if not current_user:
            print("❌ No authenticated user")
            return None
        if current_user.get('role') != 'Super Administrator':
            print("❌ Only Super Administrators can generate restore codes")
            return None

        # Generate secure 16-character code
        restore_code = secrets.token_hex(8)  # 16 characters
        expiry_time = (datetime.now() + timedelta(hours=CODE_EXPIRY_HOURS)).strftime("%Y-%m-%d %H:%M:%S")

        # Store code in database
        try:
            cursor.execute("""
                INSERT INTO restore_codes 
                (code, backup_file, created_by, created_at, expires_at, is_used)
                VALUES (?, ?, ?, datetime('now'), ?, 0)
            """, (restore_code, backup_filename, current_user['username'], expiry_time))
            conn.commit()
            
            # Log the action
            user_auth.log_activity(
                current_user['username'],
                "RESTORE_CODE_GENERATED",
                f"Backup: {backup_filename}"
            )
            
            print("\n=== RESTORE CODE GENERATED ===")
            print(f"🔑 Code: {restore_code}")
            print(f"⏳ Expires: {expiry_time}")
            print(f"💾 Backup: {backup_filename}")
            print("⚠️ Store this code securely - it will only be shown once!")
            
            return restore_code
            
        except sqlite3.IntegrityError:
            print("❌ Generated duplicate code (extremely rare), please try again")
            return None
            
    except sqlite3.Error as e:
        print(f"❌ Database error: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return None
    finally:
        if conn:
            conn.close()

def validate_and_restore(code):
    """Validate code and perform restore if valid"""
    valid_code = validate_restore_code(code)
    if not valid_code:
        print("❌ Invalid or expired restore code")
        return False
    
    from Data.backup_handler import restore_backup
    result = restore_backup(valid_code['backup_file'])
    
    if result and result.get('success'):
        print("✅ Backup restored successfully")
        return True
    else:
        print(f"❌ Restore failed: {result.get('error', 'Unknown error')}")
        return False