import sqlite3
import zipfile
import os
from datetime import datetime
import shutil
import secrets

class BackupManager:
    def __init__(self, db_path='data/urban_mobility.db'):
        self.db_path = db_path
        self.backup_dir = 'data/backups'
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, admin_username):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}.zip"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            # Create zip with database file
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(self.db_path, 'urban_mobility.db')
            
            # Record backup in database
            cursor.execute('''
                INSERT INTO backups 
                (timestamp, created_by, file_path, restore_code, is_used)
                VALUES (?, ?, ?, ?, ?)
            ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                 admin_username, backup_path, None, False))
            
            conn.commit()
            return backup_path
        except Exception as e:
            print(f"Error creating backup: {e}")
            return None
        finally:
            conn.close()
    
    def list_backups(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT backup_id, timestamp, created_by, file_path, is_used
                FROM backups
                ORDER BY timestamp DESC
            ''')
            
            backups = []
            for backup in cursor.fetchall():
                backups.append({
                    'id': backup[0],
                    'timestamp': backup[1],
                    'created_by': backup[2],
                    'file_path': backup[3],
                    'is_used': bool(backup[4])
                })
            
            return backups
        except Exception as e:
            print(f"Error listing backups: {e}")
            return []
        finally:
            conn.close()
    
    def generate_restore_code(self, backup_id, admin_username):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Generate a secure random code
            restore_code = secrets.token_hex(16)
            
            cursor.execute('''
                UPDATE backups 
                SET restore_code = ?, is_used = ?
                WHERE backup_id = ?
            ''', (restore_code, False, backup_id))
            
            conn.commit()
            return restore_code
        except Exception as e:
            print(f"Error generating restore code: {e}")
            return None
        finally:
            conn.close()
    
    def restore_backup(self, backup_id, requesting_user, restore_code=None):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if backup exists and can be restored
            query = '''
                SELECT file_path, restore_code, is_used 
                FROM backups 
                WHERE backup_id = ?
            '''
            params = (backup_id,)
            
            if restore_code:
                query += ' AND restore_code = ? AND is_used = ?'
                params += (restore_code, False)
            
            cursor.execute(query, params)
            backup = cursor.fetchone()
            
            if not backup:
                return False, "Backup not found or invalid restore code"
            
            backup_path, code, is_used = backup
            
            # For code-based restores, mark code as used
            if restore_code:
                cursor.execute('''
                    UPDATE backups 
                    SET is_used = ?
                    WHERE backup_id = ? AND restore_code = ?
                ''', (True, backup_id, restore_code))
                conn.commit()
            
            # Close all database connections before restoring
            conn.close()
            
            # Create a temporary backup of current database
            temp_backup = f"{self.db_path}.temp"
            shutil.copy2(self.db_path, temp_backup)
            
            try:
                # Extract the backup
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extract('urban_mobility.db', os.path.dirname(self.db_path))
                
                # Verify the restored database
                test_conn = sqlite3.connect(self.db_path)
                test_conn.close()
                
                return True, "Restore successful"
            except Exception as e:
                # Restore the original database if something went wrong
                shutil.copy2(temp_backup, self.db_path)
                return False, f"Restore failed: {e}. Original database restored."
            finally:
                if os.path.exists(temp_backup):
                    os.remove(temp_backup)
        except Exception as e:
            return False, f"Error during restore: {e}"
        finally:
            if 'conn' in locals():
                conn.close()