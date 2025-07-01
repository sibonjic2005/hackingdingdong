import random
import sqlite3
import string
import os, sys
from Data.crypto import encrypt
from session import get_current_user
from Data.user_db import insert_user
from Data.input_validation import validate_username, validate_password
from Authentication.secure_auth import *
from session import get_current_user
from config import DB_FILE
import bcrypt
from datetime import datetime
current_user = get_current_user()
def is_admin_user():
    return get_current_user()["role"] in ["System Administrator", "Super Administrator"]

def register_user_interactively():
    """Interactive registration with role-based access control."""
    actor_role = get_current_user()["role"]

    if not is_admin_user():
        print("❌ You do not have permission to register users.")
        return

    print("=== Register New User ===")

    
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
    success, message = insert_user(username, password, role, first, last)
    if success:
        print(f"✅ {role} account created.")
        from Main.menu import main_menu
        main_menu()
    else:
        print(f"❌ {message}")

def view_all_users():
    """Debug function to view all users in the database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT username, role, first_name, last_name FROM users")
        users = cur.fetchall()
        print("\n=== All Users in Database ===")
        for user in users:
            print(f"Username: {user[0]}, Role: {user[1]}, Name: {user[2]} {user[3]}")
    except Exception as e:
        print(f"❌ Error viewing users: {str(e)}")
    finally:
        try:
            conn.close()
        except:
            pass

def update_current_user_profile():
    """Update the current user's profile."""
    current_user = get_current_user()
    print("\n=== Update Profile ===")
    print(f"Current profile for {current_user['username']}")

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT username, first_name, last_name, email FROM users WHERE user_id = ?", 
               (current_user['user_id'],))
    user_data = cur.fetchone()
    
    if not user_data:
        print("❌ User not found.")
        return False
    
    print("\nCurrent information:")
    print(f"Username: {user_data[0]}")
    print(f"First name: {user_data[1]}")
    print(f"Last name: {user_data[2]}")
    print(f"Email: {user_data[3]}")
    
    print("\nLeave fields empty to keep current values")
    new_first = input("New first name: ").strip() or user_data[1]
    new_last = input("New last name: ").strip() or user_data[2]
    new_email = input("New email: ").strip() or user_data[3]
    
    cur.execute("UPDATE users SET first_name = ?, last_name = ?, email = ? WHERE user_id = ?",
               (new_first, new_last, new_email, current_user['user_id']))
    conn.commit()
    conn.close()
    
    print("✅ Profile updated successfully.")
    return True

def delete_current_user():
    """Delete the current user's account."""
    print("⚠️ WARNING: This will permanently delete your account!")
    confirm = input("Type 'DELETE' to confirm: ").strip()
    
    if confirm != "DELETE":
        print("❌ Deletion cancelled.")
        return False
    
    current_user = get_current_user()
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM users WHERE user_id = ?", (current_user['user_id'],))
        conn.commit()
        print("✅ Account deleted successfully.")
        print("🔒 You have been logged out.")
        return False
    except Exception as e:
        conn.rollback()
        print(f"❌ Error deleting account: {str(e)}")
        return False
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

    cur.execute("SELECT username, role, first_name, last_name FROM users WHERE user_id = ?", (user_id,))
    user_data = cur.fetchone()
    if not user_data:
        print("⚠ User not found.")
        return

    print(f"\nCurrent user data:")
    print(f"Username: {user_data[0]}")
    print(f"Role: {user_data[1]}")
    print(f"Name: {user_data[2]} {user_data[3]}")
    target_role = user_data[1]
    if not user_data:
        print("⚠ User not found.")
        return
    target_role = user_data[1]

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
            "1": "username",
            "2": "first_name",
            "3": "last_name",
            "4": "role"
        }

        print("\nWhich field would you like to update?")
        for key, field in editable_fields.items():
            print(f"{key}. {field}")

        field_choice = input("Enter field number: ").strip()
        if field_choice not in editable_fields:
            print("❌ Invalid choice.")
            return

        field = editable_fields[field_choice]
        
        if field == "role":
            if actor_role == "System Administrator" and user_id != current_user_id:
                print("❌ You cannot assign or change System Administrator roles.")
                return

            role_options = ["System Administrator", "Service Engineer"]
            print("\nSelect the new role for the user:")
            for i, r in enumerate(role_options, 1):
                print(f"{i}. {r}")

            role_choice = input("Enter the number of the desired role: ").strip()
            if not role_choice.isdigit() or int(role_choice) not in range(1, len(role_options) + 1):
                print("❌ Invalid choice.")
                return

            new_value = role_options[int(role_choice) - 1]

            # Check if same role
            cur.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
            current_role = cur.fetchone()[0]
            if current_role == new_value:
                print("ℹ️ User already has this role. No changes made.")
                return

        elif field == "username":
            new_value = input("Enter new username (8–10 characters): ").strip()
            while not validate_username(new_value):
                new_value = input("❌ Invalid. Enter a valid username: ").strip()

            cur.execute("SELECT COUNT(*) FROM users WHERE username = ?", (new_value,))
            if cur.fetchone()[0] > 0:
                print("❌ Username already exists.")
                return

        elif field == "first_name":
            new_value = input("Enter new first name: ").strip()
            if not new_value:
                print("❌ First name cannot be empty.")
                return

        elif field == "last_name":
            new_value = input("Enter new last name: ").strip()
            if not new_value:
                print("❌ Last name cannot be empty.")
                return

        cur.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (new_value, user_id))
        conn.commit()
        print(f"✅ {field.replace('_', ' ').capitalize()} updated successfully.")

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

def create_admin_interactively():
    """Interactive menu for creating a new administrator."""
    print("\n=== Create New Administrator ===")
    print("1. Create System Administrator")
    print("2. Create Service Engineer")
    print("\n0. Back")
    
    choice = input("\nChoose administrator type: ").strip()
    if choice == "1":
        print("🔍 Creating new System Administrator...")
        register_user_interactively()
    elif choice == "2":
        print("🔍 Creating new Service Engineer...")
        register_user_interactively()
    elif choice != "0":
        print("Invalid choice")
    return True

def update_admin_interactively():
    """Interactive menu for updating an administrator."""
    print("\n=== Update Administrator ===")
    print("1. Update System Administrator")
    print("2. Update Service Engineer")
    print("\n0. Back")
    
    choice = input("\nChoose administrator type: ").strip()
    if choice == "1":
        print("🔍 Updating System Administrator...")
        update_user()
    elif choice == "2":
        print("🔍 Updating Service Engineer...")
        update_user()
    elif choice != "0":
        print("Invalid choice")
    return True

def delete_admin_interactively():
    """Interactive menu for deleting an administrator."""
    print("\n=== Delete Administrator ===")
    print("1. Delete System Administrator")
    print("2. Delete Service Engineer")
    print("\n0. Back")
    
    choice = input("\nChoose administrator type: ").strip()
    if choice == "1":
        print("🔍 Deleting System Administrator...")
        delete_user()
    elif choice == "2":
        print("🔍 Deleting Service Engineer...")
        delete_user()
    elif choice != "0":
        print("Invalid choice")
    return True


def view_users_by_role():
    if not is_admin_user():
        print("❌ You do not have permission to view users.")
        return

    if current_user["role"] == "Service Engineer":
        print("❌ Access denied: you do not have permission to view users.")
        return

    if current_user["role"] == "Super Administrator":
        print("\nSelect which user role you'd like to view:")
        print("1. System Administrators")
        print("2. Service Engineers")
        choice = input("Enter choice: ").strip()

        if choice == "1":
            target_role = "System Administrator"
        elif choice == "2":
            target_role = "Service Engineer"
        else:
            print("❌ Invalid choice.")
            return

    elif current_user["role"] == "System Administrator":
        target_role = "Service Engineer"

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, username, first_name, last_name, role, registration_date
        FROM users WHERE role = ?
    """, (target_role,))
    users = cur.fetchall()
    conn.close()

    if not users:
        print(f"\nℹ️ No users found with role '{target_role}'.")
        return

    print(f"\nUsers with role: {target_role}")
    print("-" * 50)
    for u in users:
        print(f"ID: {u[0]} | Username: {u[1]} | Name: {u[2]} {u[3]} | Registered: {u[5]}")
    print("-" * 50)
