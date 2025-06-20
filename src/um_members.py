
from Main.menu import *
from session import *
from Authentication.secure_auth import SecureAuth


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

def register():
    auth = SecureAuth()
    
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
    if login_interface():
        main_menu()