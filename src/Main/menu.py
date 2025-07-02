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
from um_members import *


def main_menu():
    """Display the main menu based on user role."""
    while True:
        role = get_current_user()["role"]
        print("\n=== Main Menu ===")
        print(f"Logged in as: {get_current_user()['username']} ({role})")

        if role == "Super Administrator":
            print("\n1. Manage Administrators")
            print("2. Travellers")
            print("3. Scooters")
            print("4. System Management")
            print("0. Exit")
        elif role == "System Administrator":
            print("\n1. Manage Service Engineers")
            print("2. Travellers")
            print("3. Scooters")
            print("4. System Management")
            print("5. My Account")
            print("0. Exit")
        elif role == "Service Engineer":
            print("\n1. Scooters")
            print("2. My Account")
            print("0. Exit")

        choice = input("\nChoose an option: ").strip()

        if role == "Super Administrator":
            if choice == "1":
                admin_management_menu()
            elif choice == "2":
                traveller_menu()
            elif choice == "3":
                scooter_menu()
            elif choice == "4":
                system_management_menu()
            elif choice == "0":
                clear_current_user()
                print("🔒 Logged out.")
                login_interface()
            else:
                print("❌ Ongeldige keuze. Probeer opnieuw.")
        elif role == "System Administrator":
            if choice == "1":
                service_engineer_management_menu()
            elif choice == "2":
                traveller_menu()
            elif choice == "3":
                scooter_menu()
            elif choice == "4":
                system_management_menu()
            elif choice == "5":
                my_account_menu()
            elif choice == "0":
                clear_current_user()
                print("🔒 Logged out.")
                login_interface()
            else:
                print("❌ Ongeldige keuze. Probeer opnieuw.")
        elif role == "Service Engineer":
            if choice == "1":
                service_engineer_scooter_menu()
            elif choice == "2":
                service_engineer_account_menu()
            elif choice == "0":
                clear_current_user()
                print("🔒 Logged out.")
                login_interface()
            else:
                print("❌ Ongeldige keuze. Probeer opnieuw.")


def admin_management_menu():
    """Menu for managing all administrators."""
    while True:
        print("\n=== Manage Administrators ===")
        print("1. Create new administrator")
        print("2. Update administrator")
        print("3. Delete administrator")
        print("4. View all administrators")
        print("0. Back")

        choice = input("\nChoose an option: ").strip()
        if choice == "1":
            print("🔍 Creating new administrator...")
            create_admin_interactively()
        elif choice == "2":
            print("🔍 Updating administrator...")
            update_admin_interactively()
        elif choice == "3":
            print("🔍 Deleting administrator...")
            delete_admin_interactively()
        elif choice == "4":
            print("🔍 Viewing all administrators...")
            view_users_by_role()
        elif choice == "0":
            break
        else:
            print("❌ Ongeldige keuze. Probeer opnieuw.")


def service_engineer_management_menu():
    """Menu for managing service engineers."""
    while True:
        print("\n=== Service Engineers ===")
        print("1. Create new Service Engineer")
        print("2. Update Service Engineer")
        print("3. Delete Service Engineer")
        print("4. Reset Service Engineer password")
        print("0. Back")

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
            update_admin_interactively()
        elif choice == "0":
            break
        else:
            print("❌ Ongeldige keuze. Probeer opnieuw.")


def my_account_menu():
    """Menu for managing your own account."""
    while True:
        print("\n=== My Account ===")
        print("1. Update Profile")
        print("2. Delete Account")
        print("0. Back")

        choice = input("\nChoose an option: ").strip()
        if choice == "1":
            print("🔍 Updating your profile...")
            update_current_user_profile()
        elif choice == "2":
            print("🔍 Deleting your account...")
            delete_current_user()
        elif choice == "0":
            break
        else:
            print("❌ Ongeldige keuze. Probeer opnieuw.")


def service_engineer_scooter_menu():
    """Menu for Service Engineer to manage scooters."""
    while True:
        print("\n=== Scooter Management ===")
        print("1. Search Scooters")
        print("2. View Scooter Details")
        print("3. Update Scooter Information")
        print("0. Back")

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
        elif choice == "0":
            break
        else:
            print("❌ Ongeldige keuze. Probeer opnieuw.")


def service_engineer_account_menu():
    """Menu for Service Engineer to manage their account."""
    while True:
        print("\n=== My Account ===")
        print("1. Change Password")
        print("0. Back")

        choice = input("\nChoose an option: ").strip()
        if choice == "1":
            print("🔍 Changing password...")
            update_admin_interactively()
        elif choice == "0":
            break
        else:
            print("❌ Ongeldige keuze. Probeer opnieuw.")


def traveller_menu():
    """Menu for managing Travellers."""
    while True:
        print("\n=== Travellers ===")
        print("1. Create new traveller")
        print("2. Update traveller")
        print("3. Delete traveller")
        print("4. View all travellers")
        print("0. Back")

        choice = input("\nChoose an option: ").strip()
        if choice == "1":
            create_traveller_from_input()
        elif choice == "2":
            print("🔍 Updating traveller...")
            update_traveller_record()
        elif choice == "3":
            print("🔍 Deleting traveller...")
            remove_traveller()
        elif choice == "4":
            print("🔍 Viewing all travellers...")
            print("=== All Travellers ===")
            view_all_travellers()
        elif choice == "0":
            break
        else:
            print("❌ Ongeldige keuze. Probeer opnieuw.")


def scooter_menu():
    """Menu for managing Scooters."""
    while True:
        print("\n=== Scooters ===")
        print("1. Search scooters")
        print("2. Create new scooter")
        print("3. Update scooter")
        print("4. Delete scooter")
        print("5. View all scooters")
        print("0. Back")

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
            scooter_id = input("Enter scooter ID to delete: ").strip()
            if scooter_id:
                delete_scooter(scooter_id)
            else:
                print("❌ No scooter ID provided.")
        elif choice == "5":
            print("🔍 Viewing all scooters...")
            view_all_scooters()
        elif choice == "0":
            break
        else:
            print("❌ Ongeldige keuze. Probeer opnieuw.")


def system_management_menu():
    """Menu for system management tasks."""
    while True:
        print("\n=== System Management ===")
        print("1. View logs (TBD)")
        print("2. Create backup")
        print("3. Generate restore code")
        print("4. Revoke restore code")
        print("0. Back")

        choice = input("\nChoose an option: ").strip()
        if choice == "1":
            view_system_logs(49)
            print("🛠 Logs view (TBD)")
        elif choice == "2":
            if get_current_user()['role'] in ['Super Administrator', 'System Administrator']:
                backup_path = create_system_backup()
                if backup_path:
                    print(f"✅ Backup successfully created at: {backup_path}")
            else:
                print("❌ Only administrators can create backups")
            input("\nPress Enter to continue...")
        elif choice == "3":
            RestoreManager.generate_restore_code()
            print("🛠 Restore code gegenereerd.")
        elif choice == "4":
            revoke_restore_code()
            print("🛠 Restore code ingetrokken.")
        elif choice == "0":
            break
        else:
            print("❌ Ongeldige keuze. Probeer opnieuw.")
