from Main.traveller_operation import create_traveller_from_input
from session import *
from Main.user_operations import *
from Main.scooter_operations import *
from Data.user_auth import UserAuth

# from Data.user_db import authenticate_user

# def login():
#     print("=== Login ===")
#     username = input("Username: ").strip()
#     password = input("Password: ").strip()

#     user_data = authenticate_user(username, password)
#     if user_data:
#         set_current_user(user_data)
#         print(f"✅ Welcome, {user_data['first_name']} ({user_data['role']})")
#         return True
#     else:
#         print("Login failed.")
#         return False
def login():
    auth = UserAuth()
    
    print("=== Login ===")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    success, message = auth.login(username, password)
    
    if success:
        set_current_user({
            "username": username,
            "role": "Super Administrator",  # For now, we'll use a fixed role
            "user_id": 1,
            "first_name": "Admin",
            "last_name": "Test"
        })
        print(f"✅ {message}")
        return True
    else:
        print(f"❌ {message}")
        return False

# Add registration function
def register():
    auth = UserAuth()
    
    print("=== Register New User ===")
    username = input("Username: ").strip()
    password = input("Password: ").strip()
    
    success, message = auth.register_user(username, password)
    
    if success:
        print(f"✅ {message}")
        return True
    else:
        print(f"❌ {message}")
        return False

# Update main menu to include registration option
def main_menu():
    if not login():
        return

    while True:
        role = get_current_user()["role"]
        print("\n--- Urban Mobility Backend ---")
        print(f"Role: {role}")
        print("Available options:")
        print("1. Search scooters")

        if role in ["System Administrator", "Super Administrator"]:
            print("2. Register new traveller")
            print("3. Register new user")
            print("4. Add new scooter")
            print("5. Delete scooter")

        if role == "Super Administrator":
            print("6. View system logs (TBD)")
            print("7. Backup / Restore (TBD)")

        print("0. Logout")

        choice = input("Choose an option: ")

        if choice == "1":
            print("🔍 Searching scooters... (function not yet connected)")
            search_scooters()
        elif choice == "2" and role in ["System Administrator", "Super Administrator"]:
            create_traveller_from_input()
        elif choice == "3" and role in ["System Administrator", "Super Administrator"]:
            register_user_interactively()
        elif choice == "4" and role in ["System Administrator", "Super Administrator"]:
            create_scooter_from_input()
        elif choice == "5" and role in ["System Administrator", "Super Administrator"]:
            delete_scooter()
        elif choice == "6" and role == "Super Administrator":
            print("🛠 Logs view (TBD)")
        elif choice == "7" and role == "Super Administrator":
            print("🛠 Backup/Restore (TBD)")
        elif choice == "0":
            clear_current_user()
            print("🔒 Logged out.")
            break
        else:
            print("Invalid choice or access denied.")


def main_menu():
    if not login():
        return

    while True:
        role = get_current_user()["role"]
        print("\n--- Urban Mobility Backend ---")
        print(f"Role: {role}")
        print("Available options:")
        print("1. Search scooters")

        if role in ["System Administrator", "Super Administrator"]:
            print("2. Register new traveller")
            print("3. Register new user")
            print("4. Add new scooter")
            print("5. Delete scooter")

        if role == "Super Administrator":
            print("6. View system logs (TBD)")
            print("7. Backup / Restore (TBD)")

        print("0. Logout")

        choice = input("Choose an option: ")

        if choice == "1":
            print("🔍 Searching scooters... (function not yet connected)")
            search_scooters()
        elif choice == "2" and role in ["System Administrator", "Super Administrator"]:
            create_traveller_from_input()
        elif choice == "3" and role in ["System Administrator", "Super Administrator"]:
            register_user_interactively()
        elif choice == "4" and role in ["System Administrator", "Super Administrator"]:
            create_scooter_from_input()
        elif choice == "5" and role in ["System Administrator", "Super Administrator"]:
            delete_scooter()
        elif choice == "6" and role == "Super Administrator":
            print("🛠 Logs view (TBD)")
        elif choice == "7" and role == "Super Administrator":
            print("🛠 Backup/Restore (TBD)")
        elif choice == "0":
            clear_current_user()
            print("🔒 Logged out.")
            break
        else:
            print("Invalid choice or access denied.")

def delete_scooter():
    print("🔍 Searching for scooter to delete...")
    
    # Get scooter details
    brand = input("Brand: ").strip()
    if not brand:
        print("❌ Brand is required.")
        return
    
    model = input("Model: ").strip()
    if not model:
        print("❌ Model is required.")
        return
    
    serial = input("Serial Number: ").strip()
    if not serial:
        print("❌ Serial Number is required.")
        return
    
    # Search for scooter with these details
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT scooter_id, brand, model, serial_number 
        FROM scooters 
        WHERE UPPER(brand) = UPPER(?) 
        AND UPPER(model) = UPPER(?) 
        AND serial_number = ?
    """, (brand, model, serial))
    
    result = cur.fetchone()
    
    if not result:
        print("❌ No scooter found with these details.")
        conn.close()
        return
    
    scooter_id, found_brand, found_model, found_serial = result
    
    print(f"🔍 Found scooter:")
    print(f"ID: {scooter_id}")
    print(f"Brand: {found_brand}")
    print(f"Model: {found_model}")
    print(f"Serial: {found_serial}")
    
    # Confirm deletion
    confirm = input("Are you sure you want to delete this scooter? (y/n): ").lower()
    if confirm != 'y':
        print("❌ Deletion cancelled.")
        conn.close()
        return
    
    # Call the delete_scooter function
    from Main.scooter_operations import delete_scooter as delete_scooter_op
    delete_scooter_op(scooter_id)
    
    # Verify deletion
    cur.execute("SELECT COUNT(*) FROM scooters WHERE scooter_id = ?", (scooter_id,))
    if cur.fetchone()[0] == 0:
        print("✅ Scooter has been deleted successfully.")
    else:
        print("❌ Failed to delete scooter")
    
    conn.close()

if __name__ == "__main__":
    main_menu()
