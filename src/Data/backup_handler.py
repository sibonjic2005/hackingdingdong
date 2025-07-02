import os
import sqlite3
import zipfile
from datetime import datetime
from pathlib import Path
from Authentication.restore_code_manager import *
from .crypto import *  # Make sure you have decrypt function
from session import get_current_user
from Authentication.secure_auth import SecureAuth
from Data.logging_util import SystemLogger

logger = SystemLogger()

DB_PATH = "data/urban_mobility.db"
BACKUP_DIR = "data/backups"
TEMP_DIR = "data/temp_restore"
Path(BACKUP_DIR).mkdir(parents=True, exist_ok=True)
Path(TEMP_DIR).mkdir(parents=True, exist_ok=True)

def create_system_backup():
    """Create an encrypted backup of the database"""
    try:
        # 1. Verify database exists
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"Database file not found at {DB_PATH}")
        
        # 2. Create timestamped backup name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.zip"
        temp_zip_path = os.path.join(TEMP_DIR, f"temp_{backup_name}")
        final_path = os.path.join(BACKUP_DIR, backup_name)
        
        # 3. Create the zip backup
        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(DB_PATH, os.path.basename(DB_PATH))
        
        # 4. Encrypt the zip file
        if not encrypt_file(temp_zip_path, final_path):
            raise Exception("Failed to encrypt backup file")
        
        # 5. Clean up temporary zip
        os.remove(temp_zip_path)
        
        # 6. Verify the backup was created
        if not os.path.exists(final_path):
            raise Exception("Backup file was not created successfully")
        
        # 7. Log the activity
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
    """Restore a backup with proper decryption and validation"""
    temp_files = {
        'decrypted': os.path.join(TEMP_DIR, f"decrypted_{backup_filename}"),
        'db_old': DB_PATH + '.old',
        'db_restore': os.path.join(TEMP_DIR, 'temp_restore.db')
    }
    
    try:
        # 1. Construct full backup path
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        if not os.path.exists(backup_path):
            return {'success': False, 'error': 'Backup file not found'}
        
        # 2. First decrypt the backup to a temporary file
        decrypted_path = decrypt_file(backup_path, temp_files['decrypted'])
        if not decrypted_path:
            return {'success': False, 'error': 'Failed to decrypt backup'}
        
        # 3. Verify the zip file
        try:
            with zipfile.ZipFile(decrypted_path, 'r') as zipf:
                if zipf.testzip() is not None:
                    raise ValueError("Corrupted backup file")
                
                # 4. Find the database file in the zip
                db_files = [f for f in zipf.namelist() if f.endswith('.db')]
                if not db_files:
                    raise ValueError("No database file found in backup")
                
                # 5. Extract the database file
                zipf.extract(db_files[0], TEMP_DIR)
                extracted_path = os.path.join(TEMP_DIR, db_files[0])
                
                # 6. Verify the extracted database
                try:
                    conn = sqlite3.connect(extracted_path)
                    conn.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1;")
                    conn.close()
                except sqlite3.Error as e:
                    raise ValueError(f"Invalid database in backup: {str(e)}")
                
                os.rename(extracted_path, temp_files['db_restore'])
        except Exception as e:
            return {'success': False, 'error': str(e)}
        
        # 7. Create backup of current database
        if os.path.exists(DB_PATH):
            try:
                os.rename(DB_PATH, temp_files['db_old'])
            except Exception as e:
                return {'success': False, 'error': f'Could not backup current DB: {str(e)}'}
        
        # 8. Perform the actual restore
        try:
            os.rename(temp_files['db_restore'], DB_PATH)
        except Exception as e:
            # Restore the original database if restore fails
            if os.path.exists(temp_files['db_old']):
                os.rename(temp_files['db_old'], DB_PATH)
            return {'success': False, 'error': f'Restore failed: {str(e)}'}
        
        # 9. Clean up if restore succeeded
        if os.path.exists(temp_files['db_old']):
            os.remove(temp_files['db_old'])
        
        # 10. Log the activity
        if (user := get_current_user()):
            logger.log_activity(user['username'], "BACKUP_RESTORED", f"From: {backup_filename}")
        
        return {'success': True}
        
    except Exception as e:
        # Clean up any temporary files
        for temp_file in temp_files.values():
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
    finally:
        # Always clean up the decrypted file
        if os.path.exists(temp_files['decrypted']):
            os.remove(temp_files['decrypted'])