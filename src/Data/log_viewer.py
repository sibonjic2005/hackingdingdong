import sqlite3
from datetime import datetime
from Data.crypto import decrypt  

def view_system_logs(limit=50, show_suspicious_only=False):
    """View system logs with proper decryption and formatting"""
    try:
       
        conn = sqlite3.connect("data/urban_mobility.db")
        cursor = conn.cursor()
        
        
        query = """
            SELECT 
                log_id, 
                timestamp, 
                username, 
                action, 
                details, 
                is_suspicious
            FROM system_logs
        """
        params = []
        
        if show_suspicious_only:
            query += " WHERE is_suspicious = 1"
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        
        cursor.execute(query, params)
        logs = cursor.fetchall()
        
        if not logs:
            print("\nNo logs found in database")
            return
            
       
        print("\n=== SYSTEM LOGS ===")
        if show_suspicious_only:
            print("(Showing only suspicious activities)")
            
        print(f"\n{'ID':<5} | {'Date':<10} | {'Time':<8} | {'User':<12} | {'Action':<20} | {'Details':<30} | {'Suspicious'}")
        print("-"*100)
        
       
        for log in logs:
            log_id, timestamp, username, action, details, is_suspicious = log
            
            try:
                
                decrypted_user = decrypt(username) if username else "SYSTEM"
                decrypted_action = decrypt(action) if action else "UNKNOWN"
                decrypted_details = decrypt(details) if details else ""
                
                
                try:
                    date_part, time_part = timestamp.split(" ")
                    time_display = time_part[:8]
                    date_display = date_part
                except:
                    date_display = "UNKNOWN"
                    time_display = "UNKNOWN"
                
                
                print(
                    f"{log_id:<5} | {date_display:<10} | {time_display:<8} | "
                    f"{decrypted_user[:12]:<12} | "
                    f"{decrypted_action[:20]:<20} | "
                    f"{decrypted_details[:30]:<30} | "
                    f"{'⚠️' if is_suspicious else ''}"
                )
                
            except Exception as e:
                
                print(
                    f"{log_id:<5} | [DECRYPT FAILED] | "
                    f"{str(username)[:12]:<12} | "
                    f"{str(action)[:20]:<20} | "
                    f"{str(details)[:30]:<30} | "
                    f"{'⚠️' if is_suspicious else ''}"
                )
                continue
                
        
        if not show_suspicious_only:
            cursor.execute("SELECT COUNT(*) FROM system_logs WHERE is_suspicious = 1")
            suspicious_count = cursor.fetchone()[0]
            print(f"\nTotal suspicious activities in system: {suspicious_count}")
            
    except sqlite3.Error as e:
        print(f"\nDatabase error: {str(e)}")
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

# Example usage:
# view_system_logs(20)  # Show last 20 logs
# view_system_logs(show_suspicious_only=True)  # Show only suspicious logs