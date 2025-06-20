# src/Data/backup_handler.py
import os
import sqlite3
import zipfile
from datetime import datetime
from pathlib import Path

from .crypto import encrypt
from session import get_current_user
from .user_auth import UserAuth

# Constants
DB_PATH = "data/urban_mobility.db"
BACKUP_DIR = "data/backups"

# Create UserAuth instance for logging
user_auth = UserAuth()

def create_system_backup():
    """Create an encrypted backup of the system database"""
    try:
        # Ensure backup directory exists
        Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.zip"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        
        # Verify database exists
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"Database file not found at {DB_PATH}")
        
        # Create compressed backup
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(DB_PATH, os.path.basename(DB_PATH))
        
        # Encrypt the backup
        encrypt(backup_path)
        encrypted_path = f"{backup_path}.enc"
        
        # Clean up unencrypted version
        os.remove(backup_path)
        
        # Log the action
        current_user = get_current_user()
        if current_user:
            user_auth.log_activity(  # Changed to use the UserAuth instance
                current_user['username'],
                "BACKUP_CREATED"
            )
        
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
    """List all available encrypted backups"""
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
    """Restore a backup (called from restore_code_manager)"""
    try:
        # Verify backup exists
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        if not os.path.exists(backup_path):
            return {
                'success': False,
                'error': "Backup file not found"
            }
        
        # Verify we can write to database
        if not os.access(DB_PATH, os.W_OK):
            return {
                'success': False,
                'error': "No write permission for database"
            }
        
        # Create temporary restore
        temp_restore_path = f"{DB_PATH}.temp"
        if os.path.exists(temp_restore_path):
            os.remove(temp_restore_path)
        
        # Restore process
        os.rename(DB_PATH, temp_restore_path)
        try:
            # Your decryption logic here
            # Then unzip to original location
            
            # If successful, delete temp
            os.remove(temp_restore_path)
            
            # Log the restore
            current_user = get_current_user()
            if current_user:
                user_auth.log_activity(  # Changed to use the UserAuth instance
                    current_user['username'],
                    "BACKUP_RESTORED"
                )
            
            return {'success': True}
            
        except Exception as restore_error:
            # Restore original database
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