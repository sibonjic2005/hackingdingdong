import sqlite3
import os, sys
from Data.crypto import encrypt
from session import get_current_user
from Data.user_db import insert_user
from Data.input_validation import validate_username, validate_password
from session import get_current_user
from config import DB_FILE
import bcrypt
from datetime import datetime
    
def is_admin_user():
    return get_current_user()["role"] in ["System Administrator", "Super Administrator"]

def register_user_interactively(role=None):
    """Interactive registration with role-based access control."""
    actor_role = get_current_user()["role"]

    # Check if the user has permission to register new users
    if not is_admin_user():
        print("❌ You do not have permission to register users.")
        return

    print("=== Register New User ===")

    # If role is not provided, show selection menu
    if role is None:
        print("Select user role to register:")
        allowed_roles = []

        if actor_role == "Super Administrator":
            allowed_roles = ["System Administrator", "Service Engineer"]
        elif actor_role == "System Administrator":
            allowed_roles = ["Service Engineer"]

        for i, role in enumerate(allowed_roles, 1):
            print(f"{i}. {role}")

        choice = input("\nChoose role (1-{}): ".format(len(allowed_roles)))
        if not choice.isdigit() or int(choice) not in range(1, len(allowed_roles) + 1):
            print("❌ Invalid choice.")
            return

        role = allowed_roles[int(choice) - 1]

    username = input("Enter username (8–10 chars): ")
    while not validate_username(username):
        username = input("❌ Invalid. Enter valid username: ")

    password = input("Enter password (12–30 chars)\n" +
                     "Requires 1 uppercase, 1 lowercase, 1 digit, 1 special char): ")
    while not validate_password(password):
        password = input("❌ Invalid. Enter valid password: ")

    first = input("First name: ")
    last = input("Last name: ")

    # Insert user into database
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    try:
        # Check if username already exists
        cur.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
        if cur.fetchone()[0] > 0:
            print("❌ Username already exists")
            return

        # Hash the password
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        # Insert user
        cur.execute("""
            INSERT INTO users (username, password_hash, role, first_name, last_name, registration_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, password_hash, role, first, last, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        conn.commit()
        print(f"✅ {role} account created successfully.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating user: {str(e)}")
    finally:
        conn.close()


def update_user(user_id, updates: dict, reset_password=False):
    """Update user information or reset password.
    
    Args:
        user_id: ID of the user to update
        updates: Dictionary of fields to update
        reset_password: If True, will reset the user's password
    """
    actor_role = get_current_user()["role"]
    current_user_id = get_current_user()["user_id"]
    
    if not is_admin_user():
        print("❌ You do not have permission to update users.")
        return

    # Get current user's role
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
    target_role = cur.fetchone()[0]

    # System Admins may NOT change the role to or from System Admin
    if actor_role == "System Administrator":
        if "role" in updates and updates["role"] == "System Administrator":
            print("❌ System Admins cannot assign or modify System Admin roles.")
            return

    # System Admins can only modify Service Engineers, unless it's themselves
    if actor_role == "System Administrator" and target_role != "Service Engineer":
        if user_id != current_user_id:
            print("❌ System Admins can only modify Service Engineers.")
            return

    allowed_fields = {"first_name", "last_name", "role"}

    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        
        # Get current user's role
        cur.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
        target_role = cur.fetchone()[0]

        # System Admins may NOT change the role to or from System Admin
        if actor_role == "System Administrator":
            if "role" in updates and updates["role"] == "System Administrator":
                print("❌ System Admins cannot assign or modify System Admin roles.")
                return

        # System Admins can only modify Service Engineers
        if actor_role == "System Administrator" and target_role != "Service Engineer":
            print("❌ System Admins can only modify Service Engineers.")
            return

        allowed_fields = {"first_name", "last_name", "role"}
        if not updates:
            print("❌ No updates provided.")
            return
        if not set(updates).issubset(allowed_fields):
            print("❌ Invalid update field(s).")
            return

        try:
            parts = []
            values = []

            for k, v in updates.items():
                parts.append(f"{k} = ?")
                values.append(v)

            # If resetting password
            if reset_password:
                # Generate a random password
                import random
                import string
                chars = string.ascii_letters + string.digits + string.punctuation
                new_password = ''.join(random.choice(chars) for _ in range(12))
                
                # Hash the new password
                password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
                
                # Send password reset email (implement email system)
                print(f"⚠ Password reset for user. New password: {new_password}")
                
                # Add password_hash to update
                parts.append("password_hash = ?")
                values.append(password_hash)

            values.append(user_id)
            
            cur.execute(f"UPDATE users SET {', '.join(parts)} WHERE user_id = ?", values)
            conn.commit()
            print("✅ User updated successfully.")
        except Exception as e:
            conn.rollback()
            print(f"❌ Error updating user: {str(e)}")
    except sqlite3.Error as e:
        print(f"❌ Database error: {str(e)}")
    finally:
        try:
            conn.close()
        except:
            pass


def delete_user(user_id):
    """Delete a user. System Admins can only delete Service Engineers."""
    actor_role = get_current_user()["role"]
    current_user_id = get_current_user()["user_id"]
    
    if not is_admin_user():
        print("❌ You do not have permission to delete users.")
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
    except sqlite3.Error as e:
        print(f"❌ Error connecting to database: {str(e)}")
        return

    try:
        # Get target user's role
        cur.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            print("⚠ User not found.")
            return

        target_role = row[0]
        
        # Super Admin can delete any user
        if actor_role == "Super Administrator":
            cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        # System Admin can only delete Service Engineers
        elif actor_role == "System Administrator":
            if target_role == "Service Engineer":
                cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            else:
                print("❌ System Admins can only delete Service Engineers.")
                return
        # System Admin can delete themselves
        elif actor_role == "System Administrator" and user_id == current_user_id:
            cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        else:
            print("❌ You do not have permission to delete this user.")
            return

        conn.commit()
        print("✅ User deleted successfully.")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"❌ Error deleting user: {str(e)}")
    finally:
        try:
            conn.close()
        except:
            pass
