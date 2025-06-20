
from Main.menu import *
from session import *
from Data.user_auth import UserAuth


def login_interface():
    print("=== Login ===")
    username = input("Username: ")
    password = input("Password: ")

    auth = SecureAuth()
    success, message = auth.login(username, password)

    if success:
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
    
if __name__ == "__main__":
    # Start login process
    if login_interface():
        main_menu()