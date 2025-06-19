import unittest
from logger import Logger
from backup_manager import BackupManager
import sqlite3
import os

class TestLoggingBackup(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Setup test database
        cls.test_db = 'test_urban_mobility.db'
        cls.conn = sqlite3.connect(cls.test_db)
        cls.cursor = cls.conn.cursor()
        
        # Create tables
        cls.cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                username BLOB NOT NULL,
                action_description BLOB NOT NULL,
                additional_info BLOB NOT NULL,
                is_suspicious INTEGER NOT NULL
            )
        ''')
        
        cls.cursor.execute('''
            CREATE TABLE IF NOT EXISTS backups (
                backup_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                created_by TEXT NOT NULL,
                file_path TEXT NOT NULL,
                restore_code TEXT,
                is_used INTEGER DEFAULT 0
            )
        ''')
        
        cls.conn.commit()
        
        # Create test key file
        from cryptography.fernet import Fernet
        cls.test_key = Fernet.generate_key()
        with open('test_log_key.key', 'wb') as key_file:
            key_file.write(cls.test_key)
        
        # Create test backup directory
        os.makedirs('test_backups', exist_ok=True)
    
    def setUp(self):
        # Clear tables before each test
        self.cursor.execute('DELETE FROM logs')
        self.cursor.execute('DELETE FROM backups')
        self.conn.commit()
        
        # Initialize fresh logger and backup manager for each test
        self.logger = Logger(self.test_db)
        self.logger.key = self.test_key  # Override with test key
        self.logger.cipher = Fernet(self.test_key)
        
        self.backup_manager = BackupManager(self.test_db)
        self.backup_manager.backup_dir = 'test_backups'
    
    def test_log_activity(self):
        # Test normal logging
        self.assertTrue(self.logger.log_activity('test_user', 'Test action', 'Additional info'))
        
        # Test logging with empty additional info
        self.assertTrue(self.logger.log_activity('test_user', 'Test action 2'))
        
        # Test suspicious activity logging
        self.assertTrue(self.logger.log_activity('test_user', 'Suspicious action', '', True))
        
        # Verify logs were created
        logs = self.logger.get_recent_logs()
        self.assertEqual(len(logs), 3)
        self.assertTrue(logs[0]['suspicious'])
    
    def test_create_backup(self):
        # Create a test database file
        with open(self.test_db, 'wb') as f:
            f.write(b'test data')
        
        backup_path = self.backup_manager.create_backup('test_admin')
        self.assertIsNotNone(backup_path)
        self.assertTrue(os.path.exists(backup_path))
        
        # Verify backup was recorded in database
        self.cursor.execute('SELECT COUNT(*) FROM backups')
        self.assertEqual(self.cursor.fetchone()[0], 1)
    
    def test_restore_backup(self):
        # Create a backup
        with open(self.test_db, 'wb') as f:
            f.write(b'original data')
        backup_path = self.backup_manager.create_backup('test_admin')
        
        # Modify the database
        with open(self.test_db, 'wb') as f:
            f.write(b'modified data')
        
        # Restore the backup
        self.cursor.execute('SELECT backup_id FROM backups')
        backup_id = self.cursor.fetchone()[0]
        
        success, message = self.backup_manager.restore_backup(backup_id, 'test_admin')
        self.assertTrue(success)
        
        # Verify database was restored
        with open(self.test_db, 'rb') as f:
            content = f.read()
        self.assertEqual(content, b'original data')
    
    def test_restore_with_code(self):
        # Create a backup
        with open(self.test_db, 'wb') as f:
            f.write(b'original data')
        backup_path = self.backup_manager.create_backup('test_admin')
        
        # Get backup ID
        self.cursor.execute('SELECT backup_id FROM backups')
        backup_id = self.cursor.fetchone()[0]
        
        # Generate restore code
        code = self.backup_manager.generate_restore_code(backup_id, 'super_admin')
        self.assertIsNotNone(code)
        
        # Modify the database
        with open(self.test_db, 'wb') as f:
            f.write(b'modified data')
        
        # Restore with code
        success, message = self.backup_manager.restore_backup(backup_id, 'system_admin', code)
        self.assertTrue(success)
        
        # Verify database was restored
        with open(self.test_db, 'rb') as f:
            content = f.read()
        self.assertEqual(content, b'original data')
        
        # Verify code can't be used again
        success, message = self.backup_manager.restore_backup(backup_id, 'system_admin', code)
        self.assertFalse(success)
    
    @classmethod
    def tearDownClass(cls):
        # Clean up test files
        cls.conn.close()
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
        if os.path.exists('test_log_key.key'):
            os.remove('test_log_key.key')
        if os.path.exists('test_backups'):
            import shutil
            shutil.rmtree('test_backups')

if __name__ == '__main__':
    unittest.main()