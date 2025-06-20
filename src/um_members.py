import msvcrt
from Authentication.secure_auth import SecureAuth
from session import set_current_user, get_current_user, clear_current_user
from Main.user_operations import *
from Main.scooter_operations import *
from Main.traveller_operation import create_traveller_from_input
from Data.user_auth import UserAuth
from Data.log_viewer import view_system_logs
from Data.backup_handler import create_system_backup
from Authentication.restore_code_manager import generate_restore_code
from Authentication.restore_code_revoker import revoke_restore_code
from session import get_current_user

# Initialize authentication
auth = SecureAuth()

from Authentication.auth import SUPER_ADMIN_USERNAME, SUPER_ADMIN_PASSWORD, SUPER_ADMIN_USER, verify_admin_credentials

def login():
    print("=== Login ===")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    # Verify credentials using the auth module
    if verify_admin_credentials(username, password):
        print(f"✅ Login successful as {get_current_user()['role']}")
        return True
    else:
        print("❌ Invalid username or password")
        return False

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
        print("\n1. Service Engineers")
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
        register_user_interactively("Service Engineer")
    elif choice == "2":
        print("🔍 Updating Service Engineer...")
        update_user_interactively("Service Engineer")
    elif choice == "3":
        print("🔍 Deleting Service Engineer...")
        delete_user_interactively("Service Engineer")
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

def update_current_user_profile():
    """Update the current user's profile."""
    current_user = get_current_user()
    print("\n=== Update Profile ===")
    print(f"Current profile for {current_user['username']}")
    
    # Get current user's data
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT username, first_name, last_name, email FROM users WHERE user_id = ?", 
               (current_user['user_id'],))
    user_data = cur.fetchone()
    
    if not user_data:
        print("❌ User not found.")
        return False
    
    # Show current data
    print("\nCurrent information:")
    print(f"Username: {user_data[0]}")
    print(f"First name: {user_data[1]}")
    print(f"Last name: {user_data[2]}")
    print(f"Email: {user_data[3]}")
    
    # Get updates
    print("\nLeave fields empty to keep current values")
    new_first = input("New first name: ").strip() or user_data[1]
    new_last = input("New last name: ").strip() or user_data[2]
    new_email = input("New email: ").strip() or user_data[3]
    
    # Update database
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
        # Delete user
        cur.execute("DELETE FROM users WHERE user_id = ?", (current_user['user_id'],))
        conn.commit()
        print("✅ Account deleted successfully.")
        clear_current_user()
        print("🔒 You have been logged out.")
        return False
    except Exception as e:
        conn.rollback()
        print(f"❌ Error deleting account: {str(e)}")
        return False
    finally:
        conn.close()

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
        update_scooter_information()
    elif choice != "0":
        print("Invalid choice")
    return True

def search_scooters():
    """Search for scooters with specific criteria."""
    print("\n=== Search Scooters ===")
    print("Search by:")
    print("1. Scooter ID")
    print("2. Location")
    print("3. Status")
    print("\n0. Back")
    
    choice = input("\nChoose search option: ").strip()
    if choice == "1":
        scooter_id = input("Enter scooter ID: ").strip()
        if scooter_id:
            view_scooter_details(scooter_id)
    elif choice == "2":
        location = input("Enter location (city or area): ").strip()
        if location:
            search_by_location(location)
    elif choice == "3":
        print("\nStatus options:")
        print("1. Available")
        print("2. In use")
        print("3. Maintenance")
        status_choice = input("\nChoose status: ").strip()
        if status_choice in ["1", "2", "3"]:
            statuses = {"1": "available", "2": "in_use", "3": "maintenance"}
            search_by_status(statuses[status_choice])
    elif choice != "0":
        print("Invalid choice")

def search_by_location(location):
    """Search for scooters in a specific location."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM scooters 
        WHERE location LIKE ? 
        ORDER BY status ASC
    """, (f"%{location}%",))
    
    scooters = cur.fetchall()
    if not scooters:
        print("❌ No scooters found in this location.")
        return
    
    print("\nFound scooters:")
    for scooter in scooters:
        print(f"\nScooter ID: {scooter[0]}")
        print(f"Location: {scooter[1]}")
        print(f"Status: {scooter[2]}")
        print(f"Battery: {scooter[3]}%")
        print(f"Last maintenance: {scooter[4]}")
    
    conn.close()

def search_by_status(status):
    """Search for scooters with a specific status."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM scooters 
        WHERE status = ? 
        ORDER BY location ASC
    """, (status,))
    
    scooters = cur.fetchall()
    if not scooters:
        print(f"❌ No scooters found with status: {status}")
        return
    
    print(f"\nScooters with status {status}:")
    for scooter in scooters:
        print(f"\nScooter ID: {scooter[0]}")
        print(f"Location: {scooter[1]}")
        print(f"Status: {scooter[2]}")
        print(f"Battery: {scooter[3]}%")
        print(f"Last maintenance: {scooter[4]}")
    
    conn.close()

def view_scooter_details(scooter_id=None):
    """View detailed information about a scooter."""
    if not scooter_id:
        scooter_id = input("Enter scooter ID: ").strip()
    
    if not scooter_id:
        print("❌ No scooter ID provided.")
        return
    
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT * FROM scooters 
        WHERE scooter_id = ?
    """, (scooter_id,))
    
    scooter = cur.fetchone()
    if not scooter:
        print(f"❌ Scooter with ID {scooter_id} not found.")
        return
    
    print("\n=== Scooter Details ===")
    print(f"Scooter ID: {scooter[0]}")
    print(f"Location: {scooter[1]}")
    print(f"Status: {scooter[2]}")
    print(f"Battery: {scooter[3]}%")
    print(f"Last maintenance: {scooter[4]}")
    print(f"Next maintenance due: {scooter[5]}")
    print(f"Total trips: {scooter[6]}")
    print(f"Total distance: {scooter[7]} km")
    
    conn.close()

def update_scooter_information():
    """Update scooter information."""
    scooter_id = input("Enter scooter ID to update: ").strip()
    if not scooter_id:
        print("❌ No scooter ID provided.")
        return
    
    # Get current scooter details
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT * FROM scooters WHERE scooter_id = ?", (scooter_id,))
    scooter = cur.fetchone()
    
    if not scooter:
        print(f"❌ Scooter with ID {scooter_id} not found.")
        return
    
    print("\nCurrent information:")
    print(f"Location: {scooter[1]}")
    print(f"Status: {scooter[2]}")
    print(f"Battery: {scooter[3]}%")
    print(f"Last maintenance: {scooter[4]}")
    print(f"Next maintenance due: {scooter[5]}")
    
    # Get updates
    print("\nLeave fields empty to keep current values")
    new_location = input("New location: ").strip() or scooter[1]
    
    print("\nStatus options:")
    print("1. Available")
    print("2. In use")
    print("3. Maintenance")
    status_choice = input("\nChoose new status (1-3): ").strip()
    new_status = scooter[2]
    if status_choice in ["1", "2", "3"]:
        statuses = {"1": "available", "2": "in_use", "3": "maintenance"}
        new_status = statuses[status_choice]
    
    new_battery = input("New battery level (0-100): ").strip()
    if new_battery:
        try:
            new_battery = int(new_battery)
            if not 0 <= new_battery <= 100:
                print("❌ Battery level must be between 0 and 100.")
                return
        except ValueError:
            print("❌ Invalid battery level.")
            return
    else:
        new_battery = scooter[3]
    
    # Update database
    cur.execute("""
        UPDATE scooters 
        SET location = ?, 
            status = ?,
            battery_level = ?,
            last_maintenance = CURRENT_TIMESTAMP
        WHERE scooter_id = ?
    """, (new_location, new_status, new_battery, scooter_id))
    
    conn.commit()
    conn.close()
    
    print("✅ Scooter information updated successfully.")

def service_engineer_account_menu():
    """Menu for Service Engineer to manage their account."""
    print("\n=== My Account ===")
    print("1. Change Password")
    print("\n0. Back")
    
    choice = input("\nChoose an option: ").strip()
    if choice == "1":
        print("🔍 Changing password...")
        return change_password_interactively()
    elif choice != "0":
        print("Invalid choice")
    return True

def reset_service_engineer_password():
    """Reset password for a service engineer."""
    print("\n=== Reset Service Engineer Password ===")
    
    # Get list of service engineers
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, first_name, last_name FROM users WHERE role = 'Service Engineer'")
    engineers = cur.fetchall()
    
    if not engineers:
        print("❌ No service engineers found.")
        return False
    
    print("\nAvailable Service Engineers:")
    for i, (user_id, username, first, last) in enumerate(engineers, 1):
        print(f"{i}. {first} {last} ({username})")
    
    choice = input("\nChoose engineer to reset password (1-{}): ".format(len(engineers))).strip()
    if not choice.isdigit() or int(choice) not in range(1, len(engineers) + 1):
        print("❌ Invalid choice.")
        return False
    
    selected_engineer = engineers[int(choice) - 1]
    user_id = selected_engineer[0]
    
    # Generate new password
    new_password = input("Enter new password (12-30 chars): ")
    while not validate_password(new_password):
        new_password = input("❌ Invalid. Enter valid password (12-30 chars): ")
    
    # Update password in database
    password_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    cur.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", 
               (password_hash, user_id))
    conn.commit()
    conn.close()
    
    print("✅ Password reset successfully.")
    return True

def create_admin_interactively():
    """Interactive menu for creating a new administrator."""
    print("\n=== Create New Administrator ===")
    print("1. Create System Administrator")
    print("2. Create Service Engineer")
    print("\n0. Back")
    
    choice = input("\nChoose administrator type: ").strip()
    if choice == "1":
        print("🔍 Creating new System Administrator...")
        register_user_interactively("System Administrator")
    elif choice == "2":
        print("🔍 Creating new Service Engineer...")
        register_user_interactively("Service Engineer")
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
        update_user_interactively("System Administrator")
    elif choice == "2":
        print("🔍 Updating Service Engineer...")
        update_user_interactively("Service Engineer")
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
        delete_user_interactively("System Administrator")
    elif choice == "2":
        print("🔍 Deleting Service Engineer...")
        delete_user_interactively("Service Engineer")
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
        update_user_interactively("Service Engineer")
    elif choice == "3":
        print("🔍 Deleting Service Engineer...")
        delete_user_interactively("Service Engineer")
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
        update_traveller_interactively()
    elif choice == "3":
        print("🔍 Deleting traveller...")
        delete_traveller_interactively()
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
        update_scooter_interactively()
    elif choice == "4":
        print("🔍 Deleting scooter...")
        delete_scooter_interactively()
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

    choice = input("\nChoose an option: ").strip()

    if role == "Super Administrator":
        if choice == "1":
            print("🔍 Creating new System Admin...")
        elif choice == "2":
            print("🔍 Updating System Admin...")
        elif choice == "3":
            print("🔍 Deleting System Admin...")
        elif choice == "4":
            print("🔍 Creating new Service Engineer...")
        elif choice == "5":
            print("🔍 Updating Service Engineer...")
        elif choice == "6":
            print("🔍 Deleting Service Engineer...")
        elif choice == "7":
            create_traveller_from_input()
        elif choice == "8":
            print("🔍 Updating traveller...")
        elif choice == "9":
            print("🔍 Deleting traveller...")
        elif choice == "10":
            print("🔍 Creating new scooter...")
        elif choice == "11":
            print("🔍 Updating scooter...")
        elif choice == "12":
            print("🔍 Deleting scooter...")
        elif choice == "13":
            print("🛠 Logs view (TBD)")
        elif choice == "14":
            print("🛠 Create backup")
        elif choice == "15":
            print("🛠 Generate restore code")
        elif choice == "16":
            print("🛠 Revoke restore code")
        elif choice == "0":
            clear_current_user()
            print("🔒 Logged out.")
            return
        else:
            print("Invalid choice or access denied.")
            input("\nPress Enter to continue...")
    elif role == "System Administrator":
        if choice == "1":
            print("🔍 Creating new Service Engineer...")
        elif choice == "2":
            print("🔍 Updating Service Engineer...")
        elif choice == "3":
            print("🔍 Deleting Service Engineer...")
        elif choice == "4":
            create_traveller_from_input()
        elif choice == "5":
            print("🔍 Updating traveller...")
        elif choice == "6":
            print("🔍 Deleting traveller...")
        elif choice == "7":
            print("🔍 Creating new scooter...")
        elif choice == "8":
            print("🔍 Updating scooter...")
        elif choice == "9":
            print("🔍 Deleting scooter...")
        elif choice == "10":
            print("🔒 Change password")
        elif choice == "0":
            clear_current_user()
            print("🔒 Logged out.")
            return
        else:
            print("Invalid choice or access denied.")
            input("\nPress Enter to continue...")
    elif role == "Service Engineer":
        if choice == "1":
            print("🔍 Searching scooters...")
            search_scooters()
        elif choice == "2":
            print("🔍 Updating scooter information...")
            update_scooter_info()
        elif choice == "3":
            print("🔒 Change password")
            change_password_interactively()
        elif choice == "0":
            clear_current_user()
            print("🔒 Logged out.")
            return
        else:
            print("Invalid choice or access denied.")
            input("\nPress Enter to continue...")

def manage_scooters():
    while True:
        print("\n--- Scooter Management ---")
        print("Available options:")
        print("1. View Scooters")
        print("2. Add New Scooter")
        print("3. Delete Scooter")
        print("0. Back")
        
        choice = input("\nChoose an option: ").strip()
        
        if choice == "1":
            view_scooters()
        elif choice == "2":
            create_scooter_from_input()
        elif choice == "3":
            delete_scooter()
        elif choice == "0":
            break
        else:
            print("Invalid choice.")
            input("\nPress Enter to continue...")

def manage_users():
    role = get_current_user()["role"]
    options = ["View Users", "Register New User", "Delete User", "Back"]
    functions = [view_users, register_user_interactively, delete_user, lambda: None]
    
    # Super Administrator can manage all users
    if role == "Super Administrator":
        options = ["View Users", "Register New User", "Update User", "Delete User", "Back"]
        functions = [view_users, register_user_interactively, update_user, delete_user, lambda: None]
    
    menu = Menu("User Management", options, functions)
    
    while True:
        choice = menu.run()
        if choice == -1 or choice == len(options) - 1:  # Escape or Back
            break
        else:
            input("\nPress Enter to continue...")

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
    # Initialize authentication
    auth = SecureAuth()
    
    # Start login process
    if login():
        main_menu()