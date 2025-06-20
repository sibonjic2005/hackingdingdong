import sqlite3
from datetime import datetime
from Data.crypto import decrypt 
import os

DB_PATH = "data/urban_mobility.db"

def initialize_logs_table():
    """Create logs table if it doesn't exist"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                username TEXT,
                action_description TEXT NOT NULL,
                additional_info TEXT,
                is_suspicious INTEGER DEFAULT 0
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"Error initializing logs table: {str(e)}")
    finally:
        if conn:
            conn.close()

def view_system_logs(limit=50):
    """Display decrypted system logs from database"""
    # Initialize table first
    initialize_logs_table()
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, username, action_description, additional_info, is_suspicious
            FROM logs 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        logs = cursor.fetchall()
        
        if not logs:
            print("\nNo logs found in database")
            return
            
        print("\n=== SYSTEM LOGS ===")
        print(f"{'Timestamp':<19} | {'User':<12} | {'Action':<25} | {'Details':<20} | {'Suspicious'}")
        print("-" * 90)
        
        for log in logs:
            try:
                timestamp = datetime.strptime(log[0], "%Y-%m-%d %H:%M:%S").strftime("%d/%m %H:%M:%S")
                user = decrypt(log[1]).decode() if log[1] else "SYSTEM"
                action = decrypt(log[2]).decode()
                details = decrypt(log[3]).decode() if log[3] else ""
                
                print(f"{timestamp:<19} | {user:<12} | {action[:25]:<25} | {details[:20]:<20} | {'⚠️' if log[4] else ''}")
            except Exception as e:
                print(f"Error processing log entry: {str(e)}")
                continue
                
    except sqlite3.Error as e:
        print(f"\nDatabase error: {str(e)}")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
    finally:
        if conn:
            conn.close()