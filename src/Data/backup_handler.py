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
        
        # 2. Verify the backup file is valid before proceeding
        try:
            with zipfile.ZipFile(backup_path, 'r') as test_zip:
                if test_zip.testzip() is not None:
                    return {'success': False, 'error': 'Corrupted backup file'}
        except zipfile.BadZipFile:
            return {'success': False, 'error': 'Invalid backup file format'}
        
        # 3. Create temporary restore path
        restore_path = DB_PATH + '.restore'
        temp_db_path = os.path.join(os.path.dirname(restore_path), 'temp_restore.db')
        
        # Clean up any previous temporary files
        for temp_file in [restore_path, temp_db_path]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        # 4. Extract the database file from backup
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Find the database file in the zip (in case there are multiple files)
                db_files = [f for f in zipf.namelist() if f.endswith('.db')]
                if not db_files:
                    return {'success': False, 'error': 'No database file found in backup'}
                
                # Extract the first database file found
                zipf.extract(db_files[0], os.path.dirname(temp_db_path))
                extracted_path = os.path.join(os.path.dirname(temp_db_path), db_files[0])
                
                # Verify the extracted database is valid
                try:
                    conn = sqlite3.connect(extracted_path)
                    conn.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1;")
                    conn.close()
                except sqlite3.Error:
                    return {'success': False, 'error': 'Invalid database in backup'}
                
                os.rename(extracted_path, temp_db_path)
        except Exception as e:
            return {'success': False, 'error': f'Extraction failed: {str(e)}'}
        
        # 5. Create backup of current database
        if os.path.exists(DB_PATH):
            try:
                os.rename(DB_PATH, DB_PATH + '.old')
            except Exception as e:
                return {'success': False, 'error': f'Could not backup current DB: {str(e)}'}
        
        # 6. Perform the actual restore
        try:
            os.rename(temp_db_path, DB_PATH)
        except Exception as e:
            # Restore the original database if restore fails
            if os.path.exists(DB_PATH + '.old'):
                os.rename(DB_PATH + '.old', DB_PATH)
            return {'success': False, 'error': f'Restore failed: {str(e)}'}
        
        # 7. Clean up old backup if restore succeeded
        if os.path.exists(DB_PATH + '.old'):
            os.remove(DB_PATH + '.old')
        
        # 8. Log the activity
        if (user := get_current_user()):
            logger.log_activity(user['username'], "BACKUP_RESTORED", f"From: {backup_filename}")
        
        return {'success': True}
        
    except Exception as e:
        # Clean up any temporary files
        for temp_file in [restore_path, temp_db_path]:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
        
        logger.log_activity("RESTORE_FAILED", str(e))
        return {
            'success': False,
            'error': str(e)
        }