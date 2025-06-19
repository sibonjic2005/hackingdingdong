from Main.traveller_operation import create_traveller_from_input
from session import *
from Main.user_operations import *
from Main.scooter_operations import *

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
    # 🧪 Mock login for testing
    set_current_user({
        "username": "admin",
        "role": "Super Administrator",  # or "System Administrator", "Service Engineer"
        "user_id": 1,
        "first_name": "Admin",
        "last_name": "Test"
    })
    print("✅ Logged in as mock Super Administrator")
    return True


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

if __name__ == "__main__":
    main_menu()
