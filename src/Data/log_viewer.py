# src/Data/log_viewer.py
import sqlite3
from datetime import datetime
from Data.crypto import decrypt

DB_PATH = "data/urban_mobility.db"

def view_system_logs(limit=50):
    """Display decrypted system logs from database"""
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
            timestamp = datetime.strptime(log[0], "%Y-%m-%d %H:%M:%S").strftime("%d/%m %H:%M:%S")
            user = decrypt_data(log[1]).decode() if log[1] else "SYSTEM"
            action = decrypt_data(log[2]).decode()
            details = decrypt_data(log[3]).decode() if log[3] else ""
            
            print(f"{timestamp:<19} | {user:<12} | {action[:25]:<25} | {details[:20]:<20} | {'⚠️' if log[4] else ''}")
            
    except sqlite3.Error as e:
        print(f"\nDatabase error: {str(e)}")
    except Exception as e:
        print(f"\nError decrypting logs: {str(e)}")
    finally:
        conn.close() if 'conn' in locals() else None