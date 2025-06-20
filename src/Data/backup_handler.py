import os
import sqlite3
import zipfile
from datetime import datetime
from pathlib import Path

from .crypto import encrypt
from session import get_current_user
from Authentication.secure_auth import SecureAuth

DB_PATH = "data/urban_mobility.db"
BACKUP_DIR = "data/backups"

user_auth = SecureAuth()

def create_system_backup():
    try:
        Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.zip"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"Database file not found at {DB_PATH}")
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(DB_PATH, os.path.basename(DB_PATH))
        encrypt(backup_path)
        encrypted_path = f"{backup_path}.enc"
        os.remove(backup_path)
        current_user = get_current_user()
        if current_user:
            user_auth.log_activity(current_user['username'], "BACKUP_CREATED")
        return {
            'success': True,
            'path': encrypted_path,
            'filename': f"{backup_name}.enc"
        }
    except PermissionError as e:
        return {
            'success': False,
            'error': f"Permission denied: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Backup failed: {str(e)}"
        }

def list_available_backups():
    try:
        if not os.path.exists(BACKUP_DIR):
            return {'success': True, 'backups': []}
        backups = sorted(
            [f for f in os.listdir(BACKUP_DIR) if f.endswith('.enc')],
            reverse=True
        )
        return {
            'success': True,
            'backups': backups
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Error listing backups: {str(e)}",
            'backups': []
        }

def restore_backup(backup_filename):
    try:
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        if not os.path.exists(backup_path):
            return {
                'success': False,
                'error': "Backup file not found"
            }
        if not os.access(DB_PATH, os.W_OK):
            return {
                'success': False,
                'error': "No write permission for database"
            }
        temp_restore_path = f"{DB_PATH}.temp"
        if os.path.exists(temp_restore_path):
            os.remove(temp_restore_path)
        os.rename(DB_PATH, temp_restore_path)
        try:
            os.remove(temp_restore_path)
            current_user = get_current_user()
            if current_user:
                user_auth.log_activity(current_user['username'], "BACKUP_RESTORED")
            return {'success': True}
        except Exception as restore_error:
            os.rename(temp_restore_path, DB_PATH)
            return {
                'success': False,
                'error': f"Restore failed: {str(restore_error)}"
            }
    except Exception as e:
        return {
            'success': False,
            'error': f"Restore process failed: {str(e)}"
        }
