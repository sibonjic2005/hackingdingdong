# src/Data/backup_handler.py
import os
import sqlite3
import zipfile
from datetime import datetime
from pathlib import Path

from .crypto import encryptfile, decryptfile  # Requires crypto.py with these functions
from session import get_current_user
from .user_auth import UserAuth

# Constants - using absolute paths
DB_PATH = os.path.abspath("data/urban_mobility.db")
BACKUP_DIR = os.path.abspath("data/backups")

# Initialize UserAuth
user_auth = UserAuth()

def create_system_backup():
    """Create and encrypt a database backup with full verification"""
    print("\n=== Starting Backup Process ===")
    print(f"Database: {DB_PATH}")
    print(f"Backup Directory: {BACKUP_DIR}")

    try:
        # 1. Verify/Create backup directory
        try:
            os.makedirs(BACKUP_DIR, exist_ok=True)
            # Test write permissions
            test_file = os.path.join(BACKUP_DIR, "permission_test.tmp")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            print("✓ Backup directory is writable")
        except Exception as e:
            error_msg = f"❌ Cannot write to backup directory: {str(e)}"
            print(error_msg)
            return {'success': False, 'error': error_msg}

        # 2. Verify database exists
        if not os.path.exists(DB_PATH):
            error_msg = f"❌ Database not found at {DB_PATH}"
            print(error_msg)
            return {'success': False, 'error': error_msg}
        print(f"✓ Database found ({os.path.getsize(DB_PATH)} bytes)")

        # 3. Create zip backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}.zip"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(DB_PATH, os.path.basename(DB_PATH))
            print(f"✓ Temporary ZIP created ({os.path.getsize(backup_path)} bytes)")
        except Exception as e:
            error_msg = f"❌ Failed to create ZIP: {str(e)}"
            print(error_msg)
            return {'success': False, 'error': error_msg}

        # 4. Encrypt the backup (MODIFIED WITH ENHANCED CHECKS)
        encrypted_path = f"{backup_path}.enc"
        try:
            # Verify encryption function exists and is callable
            if not callable(encryptfile):
                raise Exception("Encrypt function not found or not callable")
            
            # Perform encryption
            encryptfile(backup_path)
            
            # Verify the encrypted file was created
            if not os.path.exists(encrypted_path):
                # Diagnostic info
                print("\n=== ENCRYPTION DEBUG ===")
                print(f"Expected path: {encrypted_path}")
                print(f"Parent dir exists: {os.path.exists(os.path.dirname(encrypted_path))}")
                print(f"Files in dir: {os.listdir(os.path.dirname(encrypted_path))}")
                raise Exception("Encrypted file not created after encryption")
            
            print(f"✓ Encryption successful ({os.path.getsize(encrypted_path)} bytes)")
        except Exception as e:
            error_msg = f"❌ Encryption failed: {str(e)}"
            print(error_msg)
            # Clean up failed files
            if os.path.exists(backup_path):
                os.remove(backup_path)
            if os.path.exists(encrypted_path):
                os.remove(encrypted_path)
            return {'success': False, 'error': error_msg}

        # 5. Cleanup temporary zip
        os.remove(backup_path)
        print("✓ Temporary files cleaned up")

        # 6. Final verification
        if not os.path.exists(encrypted_path):
            error_msg = "❌ Final backup file missing after all operations"
            print(error_msg)
            return {'success': False, 'error': error_msg}

        # 7. Log activity
        if (user := get_current_user()):
            user_auth.log_activity(
                user['username'],
                "BACKUP_CREATED",
                os.path.basename(encrypted_path)
            )
            print(f"✓ Activity logged for user {user['username']}")

        print("\n=== Backup Successful ===")
        print(f"🔐 Encrypted Backup: {os.path.basename(encrypted_path)}")
        print(f"📁 Location: {encrypted_path}")
        print(f"💾 Size: {os.path.getsize(encrypted_path)} bytes\n")

        return {
            'success': True,
            'path': encrypted_path,
            'filename': os.path.basename(encrypted_path)
        }

    except Exception as e:
        error_msg = f"❌ Unexpected error: {str(e)}"
        print(error_msg)
        return {'success': False, 'error': error_msg}

def list_available_backups():
    """List all valid backups with verification"""
    try:
        if not os.path.exists(BACKUP_DIR):
            return {'success': True, 'backups': [], 'count': 0}
        
        backups = []
        for f in os.listdir(BACKUP_DIR):
            if f.endswith('.enc'):
                full_path = os.path.join(BACKUP_DIR, f)
                if os.path.isfile(full_path) and os.path.getsize(full_path) > 0:
                    backups.append(f)
        
        print(f"\nFound {len(backups)} valid backups in {BACKUP_DIR}")
        return {
            'success': True,
            'backups': sorted(backups, reverse=True),
            'count': len(backups),
            'directory': BACKUP_DIR
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'backups': [],
            'count': 0
        }

def restore_backup(backup_filename):
    """Restore a backup with full verification"""
    print(f"\n=== Attempting to restore {backup_filename} ===")
    
    try:
        # 1. Verify backup exists
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        if not os.path.exists(backup_path):
            error_msg = f"❌ Backup file not found at {backup_path}"
            print(error_msg)
            return {'success': False, 'error': error_msg}
        print(f"✓ Backup found ({os.path.getsize(backup_path)} bytes)")

        # 2. Verify database write permissions
        if not os.access(DB_PATH, os.W_OK):
            error_msg = f"❌ No write permission for database at {DB_PATH}"
            print(error_msg)
            return {'success': False, 'error': error_msg}
        print("✓ Database is writable")

        # 3. Create temporary restore path
        temp_restore_path = f"{DB_PATH}.temp"
        if os.path.exists(temp_restore_path):
            os.remove(temp_restore_path)

        # 4. Move current database to temp location
        os.rename(DB_PATH, temp_restore_path)
        print("✓ Current database moved to temporary location")

        try:
            # 5. Decrypt backup
            decrypted_path = backup_path.replace('.enc', '')
            try:
                with open(backup_path, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = decryptfile(encrypted_data)
                with open(decrypted_path, 'wb') as f:
                    f.write(decrypted_data)
                print("✓ Backup decrypted successfully")
            except Exception as e:
                raise Exception(f"Decryption failed: {str(e)}")

            # 6. Extract zip
            try:
                with zipfile.ZipFile(decrypted_path, 'r') as zip_ref:
                    zip_ref.extractall(os.path.dirname(DB_PATH))
                print("✓ Database extracted from backup")
            except Exception as e:
                raise Exception(f"Extraction failed: {str(e)}")

            # 7. Verify restoration
            if not os.path.exists(DB_PATH):
                raise Exception("Database not restored after extraction")

            # 8. Cleanup
            os.remove(decrypted_path)
            print("✓ Temporary files cleaned up")

            # 9. Log activity
            if (user := get_current_user()):
                user_auth.log_activity(
                    user['username'],
                    "BACKUP_RESTORED",
                    backup_filename
                )
                print(f"✓ Activity logged for user {user['username']}")

            print("\n=== Restore Successful ===")
            return {'success': True}

        except Exception as restore_error:
            # Restore original database if something went wrong
            if os.path.exists(temp_restore_path):
                os.rename(temp_restore_path, DB_PATH)
                print("✓ Original database restored after error")
            error_msg = f"❌ Restore failed: {str(restore_error)}"
            print(error_msg)
            return {'success': False, 'error': error_msg}

    except Exception as e:
        error_msg = f"❌ Restore process failed: {str(e)}"
        print(error_msg)
        return {'success': False, 'error': error_msg}