import sqlite3
import os, sys
from Data.crypto import encrypt
from session import get_current_user
from Data.user_db import insert_user
from Data.input_validation import validate_username, validate_password
from session import get_current_user
from config import DB_FILE
    
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

    # Choose role to create
    print("Select user role to register:")
    allowed_roles = []

    if actor_role == "Super Administrator":
        allowed_roles = ["System Administrator", "Service Engineer"]
    elif actor_role == "System Administrator":
        allowed_roles = ["Service Engineer"]

    for idx, role in enumerate(allowed_roles, start=1):
        print(f"{idx}. {role}")

    choice = input("Enter choice number: ").strip()
    try:
        role = allowed_roles[int(choice) - 1]
    except (IndexError, ValueError):
        print("❌ Invalid selection.")
        return

    username = input("Enter username (8–10 chars): ")
    while not validate_username(username):
        username = input("❌ Invalid. Enter valid username: ")

    password = input("Enter password (12–30 chars)\n" +
                     "Requires 1 uppercase, 1 lowercase, 1 digit, 1 special char): ")
    while not validate_password(password):
        password = input("❌ Invalid. Enter valid password: ")

    first = input("First name: ")
    last = input("Last name: ")

    
    insert_user(username, password, role, first, last)
    print(f"{role} account created successfully.")

def update_user(user_id, updates: dict):
    """Update first name, last name or role of a user (not username or password)."""
    actor_role = get_current_user()["role"]
    if not is_admin_user():
        print("You do not have permission to update users.")
        return

    # System Admins may NOT change the role to or from System Admin
    if actor_role == "System Administrator":
        if "role" in updates and updates["role"] == "System Administrator":
            print("System Admins cannot assign or modify System Admin roles.")
            return

    allowed_fields = {"first_name", "last_name", "role"}
    if not updates:
        print("No updates provided.")
        return
    if not set(updates).issubset(allowed_fields):
        print("Invalid update field(s).")
        return

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    parts = []
    values = []

    for k, v in updates.items():
        parts.append(f"{k} = ?")
        values.append(v)

    values.append(user_id)
    cur.execute(f"UPDATE users SET {', '.join(parts)} WHERE user_id = ?", values)
    conn.commit()
    conn.close()
    print("User updated.")


def delete_user(user_id):
    """Delete a user. Only Super Admin may delete System Admins."""
    actor_role = get_current_user()["role"]
    if not is_admin_user():
        print("You do not have permission to delete users.")
        return

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        print("⚠ User not found.")
        conn.close()
        return

    target_role = row[0]
    if target_role == "System Administrator" and actor_role != "Super Administrator":
        print("Only Super Administrator may delete a System Administrator.")
        conn.close()
        return

    cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    print("User deleted.")
