import sqlite3
import os
from Authentication.restore_code_manager import *
from Authentication.restore_code_revoker import *
from Data.backup_handler import *
from Data.log_viewer import *
from session import *
from Data import *
from Main.user_operations import *
from Main.scooter_operations import *
from Main.traveller_operation import *
from Authentication.secure_auth import *


def main_menu():
    """Display the main menu based on user role."""
    role = get_current_user()["role"]
    print("\n=== Main Menu ===")
    print(f"Logged in as: {get_current_user()['username']} ({role})")
    
    if role == "Super Administrator":
        print("\n1. Manage Administrators")
        print("2. Travellers")
        print("3. Scooters")
        print("4. System Management")
        print("\n0. Exit")
    elif role == "System Administrator":
        print("\n1. Manage Service Engineers")
        print("2. Travellers")
        print("3. Scooters")
        print("4. System Management")
        print("5. My Account")
        print("\n0. Exit")
    elif role == "Service Engineer":
        print("\n1. Scooters")
        print("2. My Account")
        print("\n0. Exit")

    choice = input("\nChoose an option: ").strip()
    if role == "Super Administrator":
        if choice == "1":
            return admin_management_menu()
        elif choice == "2":
            return traveller_menu()
        elif choice == "3":
            return scooter_menu()
        elif choice == "4":
            return system_management_menu()
        elif choice == "0":
            clear_current_user()
            print("🔒 Logged out.")
            return False
    elif role == "System Administrator":
        if choice == "1":
            return service_engineer_management_menu()
        elif choice == "2":
            return traveller_menu()
        elif choice == "3":
            return scooter_menu()
        elif choice == "4":
            return system_management_menu()
        elif choice == "5":
            return my_account_menu()
        elif choice == "0":
            clear_current_user()
            print("🔒 Logged out.")
            return False
    elif role == "Service Engineer":
        if choice == "1":
            return service_engineer_scooter_menu()
        elif choice == "2":
            return service_engineer_account_menu()
        elif choice == "0":
            clear_current_user()
            print("🔒 Logged out.")
            return False
    return True

def admin_management_menu():
    """Menu for managing all administrators."""
    print("\n=== Manage Administrators ===")
    print("1. Create new administrator")
    print("2. Update administrator")
    print("3. Delete administrator")
    print("\n0. Back")
    
    choice = input("\nChoose an option: ").strip()
    if choice == "1":
        print("🔍 Creating new administrator...")
        return create_admin_interactively()
    elif choice == "2":
        print("🔍 Updating administrator...")
        return update_admin_interactively()
    elif choice == "3":
        print("🔍 Deleting administrator...")
        return delete_admin_interactively()
    elif choice != "0":
        print("Invalid choice")
    return True

def service_engineer_management_menu():
    """Menu for managing service engineers."""
    print("\n=== Service Engineers ===")
    print("1. Create new Service Engineer")
    print("2. Update Service Engineer")
    print("3. Delete Service Engineer")
    print("4. Reset Service Engineer password")
    print("\n0. Back")
    
    choice = input("\nChoose an option: ").strip()
    if choice == "1":
        print("🔍 Creating new Service Engineer...")
        register_user_interactively()
    elif choice == "2":
        print("🔍 Updating Service Engineer...")
        update_user()   
    elif choice == "3":
        print("🔍 Deleting Service Engineer...")
        delete_user()
    elif choice == "4":
        print("🔍 Resetting Service Engineer password...")
        reset_service_engineer_password()
    elif choice != "0":
        print("Invalid choice")
    return True

def my_account_menu():
    """Menu for managing your own account."""
    print("\n=== My Account ===")
    print("1. Update Profile")
    print("2. Delete Account")
    print("\n0. Back")
    
    choice = input("\nChoose an option: ").strip()
    if choice == "1":
        print("🔍 Updating your profile...")
        update_current_user_profile()
    elif choice == "2":
        print("🔍 Deleting your account...")
        delete_current_user()
    elif choice != "0":
        print("Invalid choice")
    return True

def service_engineer_scooter_menu():
    """Menu for Service Engineer to manage scooters."""
    print("\n=== Scooter Management ===")
    print("1. Search Scooters")
    print("2. View Scooter Details")
    print("3. Update Scooter Information")
    print("\n0. Back")
    
    choice = input("\nChoose an option: ").strip()
    if choice == "1":
        print("🔍 Searching scooters...")
        search_scooters()
    elif choice == "2":
        print("🔍 Viewing scooter details...")
        view_scooter_details()
    elif choice == "3":
        print("🔍 Updating scooter information...")
        update_scooter_via_cli()
    elif choice != "0":
        print("Invalid choice")
    return True

def service_engineer_account_menu():
    """Menu for Service Engineer to manage their account."""
    print("\n=== My Account ===")
    print("1. Change Password")
    print("\n0. Back")
    
    choice = input("\nChoose an option: ").strip()
    if choice == "1":
        print("🔍 Changing password...")
        return reset_service_engineer_password()
    elif choice != "0":
        print("Invalid choice")
    return True

def service_engineer_menu():
    """Menu for managing Service Engineers."""
    print("\n=== Service Engineers ===")
    print("1. Create new Service Engineer")
    print("2. Update Service Engineer")
    print("3. Delete Service Engineer")
    print("\n0. Back")
    
    choice = input("\nChoose an option: ").strip()
    if choice == "1":
        print("🔍 Creating new Service Engineer...")
        register_user_interactively()
    elif choice == "2":
        print("🔍 Updating Service Engineer...")
        update_user()
    elif choice == "3":
        print("🔍 Deleting Service Engineer...")
        delete_user()
    elif choice != "0":
        print("Invalid choice")
    return True

def traveller_menu():
    """Menu for managing Travellers."""
    print("\n=== Travellers ===")
    print("1. Create new traveller")
    print("2. Update traveller")
    print("3. Delete traveller")
    print("\n0. Back")
    
    choice = input("\nChoose an option: ").strip()
    if choice == "1":
        create_traveller_from_input()
    elif choice == "2":
        print("🔍 Updating traveller...")
        update_traveller_record()
    elif choice == "3":
        print("🔍 Deleting traveller...")
        remove_traveller()
    elif choice != "0":
        print("Invalid choice")
    return True

def scooter_menu():
    """Menu for managing Scooters."""
    print("\n=== Scooters ===")
    print("1. Search scooters")
    print("2. Create new scooter")
    print("3. Update scooter")
    print("4. Delete scooter")
    print("\n0. Back")
    
    choice = input("\nChoose an option: ").strip()
    if choice == "1":
        print("🔍 Searching scooters...")
        search_scooters()
    elif choice == "2":
        print("🔍 Creating new scooter...")
        create_scooter_from_input()
    elif choice == "3":
        print("🔍 Updating scooter...")
        update_scooter_via_cli()
    elif choice == "4":
        print("🔍 Deleting scooter...")
        scooter_id = input("Enter scooter ID to delete: ").strip()
        if scooter_id:
            delete_scooter(scooter_id)
        else:
            print("❌ No scooter ID provided.")
    elif choice != "0":
        print("Invalid choice")
    return True

def system_management_menu():
    """Menu for system management tasks."""
    print("\n=== System Management ===")
    print("1. View logs (TBD)")
    print("2. Create backup")
    print("3. Generate restore code")
    print("4. Revoke restore code")
    print("\n0. Back")
    
    choice = input("\nChoose an option: ").strip()
    if choice == "1":
        view_system_logs(49)
        print("🛠 Logs view (TBD)")
    elif choice == "2":
        # Create and encrypt backup
        if get_current_user()['role'] in ['Super Administrator', 'System Administrator']:
            backup_path = create_system_backup()
            if backup_path:
                print(f"Backup successfully created at: {backup_path}")
        else:
            print("❌ Only administrators can create backups")
        input("\nPress Enter to continue...")
    elif choice == "3":
        generate_restore_code()
        print("🛠 Generate restore code")
    elif choice == "4":
        revoke_restore_code()
        print("🛠 Revoke restore code")
    elif choice != "0":
        print("Invalid choice")
    return True