import sqlite3
from Authentication.secure_auth import SecureAuth
from session import get_current_user
from Data.log_viewer import view_system_logs

DB_PATH = "data/urban_mobility.db"

def revoke_restore_code():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        current_user = get_current_user()
        if not current_user or current_user['role'] != 'Super Administrator':
            print("\n❌ Only Super Administrators can revoke restore codes")
            return False

        cursor.execute("""
            SELECT code_id, code, backup_file, created_at, expires_at
            FROM restore_codes
            WHERE is_used = 0
            AND datetime(expires_at) > datetime('now')
            ORDER BY created_at DESC
        """)
        
        active_codes = cursor.fetchall()
        
        if not active_codes:
            print("\nNo active restore codes found")
            return False

        print("\n=== ACTIVE RESTORE CODES ===")
        print(f"{'ID':<5} | {'Code':<18} | {'Backup File':<25} | {'Expires At'}")
        print("-" * 70)
        
        for code in active_codes:
            print(f"{code[0]:<5} | {code[1]:<18} | {code[2][:25]:<25} | {code[4]}")

        code_id = input("\nEnter Code ID to revoke (0 to cancel): ").strip()
        if code_id == "0":
            return False

        cursor.execute("""
            SELECT 1 FROM restore_codes
            WHERE code_id = ?
            AND is_used = 0
            AND datetime(expires_at) > datetime('now')
        """, (code_id,))
        
        if not cursor.fetchone():
            print("\n❌ Invalid or expired code ID")
            return False

        cursor.execute("""
            UPDATE restore_codes
            SET is_used = 1
            WHERE code_id = ?
        """, (code_id,))
        
        conn.commit()

        log_activity(
            current_user['username'],
            "Revoked restore code",
            f"Code ID: {code_id}"
        )

        print("\n✅ Restore code revoked successfully")
        return True

    except sqlite3.Error as e:
        print(f"\n❌ Database error: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ Error revoking code: {str(e)}")
        return False
    finally:
        conn.close() if 'conn' in locals() else None

def revoke_all_expired_codes():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE restore_codes
            SET is_used = 1
            WHERE is_used = 0
            AND datetime(expires_at) <= datetime('now')
        """)
        
        count = cursor.rowcount
        conn.commit()
        
        if count > 0:
            print(f"\nAutomatically revoked {count} expired restore codes")
        
        return count
    except sqlite3.Error:
        return 0
    finally:
        conn.close() if 'conn' in locals() else None