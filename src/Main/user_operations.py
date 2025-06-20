import random
import sqlite3
import string
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

def register_user_interactively():
    """Interactive registration with role-based access control."""
    actor_role = get_current_user()["role"]

    # Check if the user has permission to register new users
    if not is_admin_user():
        print("❌ You do not have permission to register users.")
        return

    print("=== Register New User ===")

    # If role is not provided, show selection menu
    
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


def update_user():
    """Interactively update user fields or reset password."""
    actor = get_current_user()
    actor_role = actor["role"]
    current_user_id = actor["user_id"]

    if not is_admin_user():
        print("❌ You do not have permission to update users.")
        return

    user_id_input = input("Enter the user ID to update: ").strip()
    if not user_id_input.isdigit():
        print("❌ Invalid user ID format.")
        return
    user_id = int(user_id_input)

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    # Get target user's role
    cur.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        print("⚠ User not found.")
        return
    target_role = row[0]

    # Enforce role rules
    if actor_role == "System Administrator":
        if target_role == "System Administrator" and user_id != current_user_id:
            print("❌ You cannot modify other System Administrators.")
            return

    print("\nWhat would you like to do?")
    print("1. Update user info (first name, last name, role)")
    print("2. Reset user password")
    choice = input("Enter choice: ").strip()

    if choice == "1":
        editable_fields = {
            "1": "first_name",
            "2": "last_name",
            "3": "role"
        }

        print("\nWhich field would you like to update?")
        for key, field in editable_fields.items():
            print(f"{key}. {field}")

        field_choice = input("Enter field number: ").strip()
        if field_choice not in editable_fields:
            print("❌ Invalid choice.")
            return

        field = editable_fields[field_choice]
        new_value = input(f"Enter new value for {field}: ").strip()

        # Validate role change
        if field == "role":
            if actor_role == "System Administrator" and new_value == "System Administrator" and user_id != current_user_id:
                print("❌ You cannot assign or change System Administrator roles.")
                return
            if new_value not in ["System Administrator", "Service Engineer"]:
                print("❌ Invalid role.")
                return

        cur.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (new_value, user_id))
        conn.commit()
        print("✅ User information updated.")

    elif choice == "2":
        if actor_role == "System Administrator" and target_role != "Service Engineer" and user_id != current_user_id:
            print("❌ You can only reset passwords for Service Engineers or yourself.")
            return

        # Generate random password
        chars = string.ascii_letters + string.digits + string.punctuation
        new_password = ''.join(random.choice(chars) for _ in range(14))

        # Hash it
        password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
        cur.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (password_hash, user_id))
        conn.commit()
        print(f"✅ Password reset. New password is: {new_password}")

    else:
        print("❌ Invalid selection.")
        return

    conn.close()


def delete_user():
    """Interactively delete a user by user ID. System Admins can only delete Service Engineers."""
    actor = get_current_user()
    actor_role = actor["role"]
    current_user_id = actor["user_id"]

    if not is_admin_user():
        print("❌ You do not have permission to delete users.")
        return

    user_id_input = input("Enter the user ID to delete: ").strip()
    if not user_id_input.isdigit():
        print("❌ Invalid user ID format.")
        return

    user_id = int(user_id_input)

    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
    except sqlite3.Error as e:
        print(f"❌ Error connecting to database: {str(e)}")
        return

    try:
        cur.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            print("⚠ User not found.")
            return

        target_role = row[0]

        # Deletion logic based on roles
        if actor_role == "Super Administrator":
            cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        elif actor_role == "System Administrator":
            if user_id == current_user_id:
                cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            elif target_role == "Service Engineer":
                cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            else:
                print("❌ System Admins can only delete Service Engineers.")
                return
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