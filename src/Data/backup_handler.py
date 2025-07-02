import os
import sqlite3
import zipfile
from datetime import datetime
from pathlib import Path


from .crypto import *  # Make sure you have decrypt function
from session import get_current_user
from Authentication.secure_auth import SecureAuth
from Data.logging_util import SystemLogger

logger = SystemLogger()

DB_PATH = "data/urban_mobility.db"
BACKUP_DIR = "data/backups"
Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)  # Create dir at module load

def create_system_backup():
    """Create an encrypted backup of the database"""
    try:
        # 1. Verify database exists
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"Database file not found at {DB_PATH}")
        
        # 2. Create timestamped backup name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.zip"
        temp_path = os.path.join(BACKUP_DIR, f"temp_{backup_name}")
        final_path = os.path.join(BACKUP_DIR, backup_name)
        
        # 3. Create the zip backup
        with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(DB_PATH, os.path.basename(DB_PATH))
        
        # 4. Encrypt the backup
        encrypt_file(temp_path, final_path)
        os.remove(temp_path)  # Clean up temporary file
        
        # 5. Verify the backup was created
        if not os.path.exists(final_path):
            raise Exception("Backup file was not created successfully")
        
        # 6. Log the activity
        if (user := get_current_user()):
            logger.log_activity(user['username'], "BACKUP_CREATED", f"Backup: {backup_name}")
        
        return {
            'success': True,
            'path': final_path,
            'filename': backup_name,
            'size': os.path.getsize(final_path)
        }
        
    except Exception as e:
        logger.log_activity("BACKUP_FAILED", str(e))
        return {
            'success': False,
            'error': str(e)
        }

def list_available_backups():
    """List all available backups with verification"""
    try:
        backups = []
        for filename in sorted(os.listdir(BACKUP_DIR), reverse=True):
            if filename.endswith('.zip'):
                filepath = os.path.join(BACKUP_DIR, filename)
                backups.append({
                    'filename': filename,
                    'path': filepath,
                    'size': os.path.getsize(filepath),
                    'created': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return {
            'success': True,
            'backups': backups,
            'count': len(backups)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'backups': []
        }

def restore_backup(backup_filename):
    """Restore a backup with proper validation"""
    try:
        # 1. Validate input
        if not backup_filename.endswith('.zip'):
            backup_filename += '.zip'
            
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        if not os.path.exists(backup_path):
            return {'success': False, 'error': 'Backup file not found'}
        
        # 2. Create restore path
        restore_path = DB_PATH + '.restore'
        if os.path.exists(restore_path):
            os.remove(restore_path)
        
        # 3. Decrypt backup (if encrypted)
        # Note: Adjust based on your crypto implementation
        if backup_path.endswith('.enc'):
            decrypted_path = backup_path.replace('.enc', '')
            decrypt(backup_path, decrypted_path)
            backup_path = decrypted_path
        
        # 4. Verify the backup
        if not zipfile.is_zipfile(backup_path):
            raise ValueError("Invalid backup file format")
        
        # 5. Perform the restore
        with zipfile.ZipFile(backup_path, 'r') as zipf:
            zipf.extractall(os.path.dirname(restore_path))
        
        # 6. Replace current database
        if os.path.exists(DB_PATH):
            os.replace(DB_PATH, DB_PATH + '.old')
        os.rename(restore_path, DB_PATH)
        
        # 7. Clean up
        if backup_path.endswith('.temp'):
            os.remove(backup_path)
        
        # 8. Log the activity
        if (user := get_current_user()):
            logger.log_activity(user['username'], "BACKUP_RESTORED", f"From: {backup_filename}")
        
        return {'success': True}
        
    except Exception as e:
        logger.log_error("RESTORE_FAILED", str(e))
        return {
            'success': False,
            'error': str(e)
        }