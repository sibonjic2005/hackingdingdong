import sqlite3
from datetime import datetime
from Data.crypto import decrypt  # Your decryption module

def view_system_logs(limit=50, show_suspicious_only=False):
    """Display system logs to admin users with proper decryption"""
    try:
        conn = sqlite3.connect("data/urban_mobility.db")
        cursor = conn.cursor()
        
        # Build query based on filters
        query = """
            SELECT log_id, timestamp, username, action, details, is_suspicious
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
            
        print(f"\n{'No.':<5} | {'Date/Time':<20} | {'User':<12} | {'Action':<25} | {'Details':<40} | {'Suspicious'}")
        print("-" * 120)
        
        for log in logs:
            try:
                # Decrypt sensitive fields
                username = decrypt(log[2]) if log[2] else "SYSTEM"
                action = decrypt(log[3]) if log[3] else "UNKNOWN ACTION"
                details = decrypt(log[4]) if log[4] else ""
                
                # Format timestamp
                log_time = datetime.strptime(log[1], "%Y-%m-%d %H:%M:%S")
                formatted_time = log_time.strftime("%d-%m-%Y %H:%M")
                
                # Format suspicious flag
                suspicious = "⚠️ YES" if log[5] else "NO"
                
                print(f"{log[0]:<5} | {formatted_time:<20} | {username:<12} | {action[:25]:<25} | {details[:40]:<40} | {suspicious}")
                
            except Exception as e:
                print(f"\nError decrypting log entry {log[0]}: {str(e)}")
                continue
                
        # Show stats if not filtered
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
# view_system_logs(show_suspicious_only=True)  # Show only suspicious activities