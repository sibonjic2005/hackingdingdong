# In Authentication/restore_code_manager.py
import sqlite3
import secrets
import hashlib
from Data.backup_handler import list_available_backups
import os
from Data.crypto import *

DB_PATH = "data/urban_mobility.db"
BACKUP_DIR = "data/backups"
TEMP_DIR = "data/temp_restore"


class RestoreManager:
    def __init__(self, db_path='data/urban_mobility.db'):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._initialize_tables()

    def perform_restore(self):
        try:
            # List available backups
            backups = list_available_backups()
            if not backups['success'] or not backups['backups']:
                print("❌ No backups available")
                return False

            print("\nAvailable backups:")
            for i, backup in enumerate(backups['backups'], 1):
                print(f"{i}. {backup['filename']}")

            # Select backup
            try:
                choice = int(input("Select backup to restore (number): ")) - 1
                backup_name = backups['backups'][choice]['filename']
            except (ValueError, IndexError):
                print("❌ Invalid selection")
                return False

            # Get restore code
            restore_code = input("Enter restore code: ").strip()
            if not restore_code:
                print("❌ Restore code required")
                return False

            # Verify code
            code_hash = hashlib.sha256(restore_code.encode()).hexdigest()
            self.cursor.execute('''
                SELECT 1 FROM restore_codes 
                WHERE restore_code_hash = ? 
                AND is_used = 0
            ''', (code_hash,))
            if not self.cursor.fetchone():
                print("❌ Invalid or used restore code")
                return False

            # NEW: Create temporary decrypted file path
            temp_dir = "data/temp_restore"
            os.makedirs(temp_dir, exist_ok=True)
            decrypted_zip_path = os.path.join(temp_dir, f"decrypted_{backup_name}")
            
            # Decrypt the backup first
            if not decrypt_file(os.path.join(BACKUP_DIR, backup_name), decrypted_zip_path):
                print("❌ Failed to decrypt backup file")
                return False
            
            # Perform restore with the decrypted file
            from Data.backup_handler import restore_backup
            result = restore_backup(decrypted_zip_path)  # Pass the decrypted path
            
            # Clean up temp file
            try:
                os.remove(decrypted_zip_path)
            except:
                pass
            
            if result['success']:
                self.cursor.execute('''
                    UPDATE restore_codes 
                    SET is_used = 1 
                    WHERE restore_code_hash = ?
                ''', (code_hash,))
                self.conn.commit()
                print("✅ Database restored successfully")
                return True
            
            print(f"❌ Restore failed: {result.get('error', 'Unknown error')}")
            return False

        except Exception as e:
            print(f"❌ Error during restore: {str(e)}")
            return False
    def _initialize_tables(self):
        """Initialize restore_codes table if not exists"""
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS restore_codes (
            code_id INTEGER PRIMARY KEY AUTOINCREMENT,
            backup_name TEXT NOT NULL,
            system_admin_username TEXT NOT NULL,
            restore_code_hash TEXT NOT NULL,
            is_used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.conn.commit()

    def generate_restore_code(self):
        """
        Generate a one-time restore code (simplified version)
        """
        try:
            # List available backups
            backup_result = list_available_backups()
            if not backup_result['success'] or not backup_result['backups']:
                print("❌ No backups available")
                return None
            
            backups = backup_result['backups']
            print("\nAvailable backups:")
            for i, backup in enumerate(backups, 1):
                print(f"{i}. {backup['filename']}")
            
            # Get backup selection
            try:
                choice = int(input("Select backup (number): ")) - 1
                backup_name = backups[choice]['filename']
            except (ValueError, IndexError):
                print("❌ Invalid selection")
                return None

            # Get admin username (just ask for input)
            system_admin_username = input("Enter admin username to assign this code to: ").strip()
            if not system_admin_username:
                print("❌ Admin username required")
                return None

            # Generate and store code
            plain_code = secrets.token_hex(8)
            code_hash = hashlib.sha256(plain_code.encode()).hexdigest()

            self.cursor.execute('''
            INSERT INTO restore_codes 
            (backup_name, system_admin_username, restore_code_hash)
            VALUES (?, ?, ?)
            ''', (backup_name, system_admin_username, code_hash))
            self.conn.commit()
            
            print(f"\n✅ Restore code generated successfully")
            print(f"Code: {plain_code}")
            print(f"For backup: {backup_name}")
            print(f"Assigned to: {system_admin_username}")
            
            return plain_code
        except sqlite3.Error as e:
            print(f"❌ Database error: {str(e)}")
            return None
    

    def revoke_restore_code(self):
        """Revoke a restore code (simplified version)"""
        try:
            # List active codes
            self.cursor.execute('''
            SELECT code_id, backup_name, system_admin_username, created_at 
            FROM restore_codes WHERE is_used = 0
            ''')
            codes = self.cursor.fetchall()
            
            if not codes:
                print("❌ No active restore codes available")
                return False
                
            print("\nActive restore codes:")
            for code in codes:
                print(f"ID: {code[0]} | Backup: {code[1]} | Admin: {code[2]} | Created: {code[3]}")
            
            # Get code to revoke
            try:
                code_id = int(input("Enter code ID to revoke: "))
            except ValueError:
                print("❌ Invalid code ID")
                return False

            # Delete the code
            self.cursor.execute('DELETE FROM restore_codes WHERE code_id = ?', (code_id,))
            self.conn.commit()
            
            if self.cursor.rowcount > 0:
                print("✅ Restore code revoked successfully")
                
                return True
            print("❌ No such restore code found")
            return False
        except sqlite3.Error as e:
            print(f"❌ Database error: {str(e)}")
            return False
        
        
    

    def close(self):
        """Close database connection"""
        self.conn.close()