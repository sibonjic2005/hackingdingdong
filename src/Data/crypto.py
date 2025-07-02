from cryptography.fernet import Fernet
import os

# Persistent key management
KEY_FILE = 'encryption_key.key'

def get_fernet():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
    else:
        with open(KEY_FILE, 'rb') as f:
            key = f.read()
    return Fernet(key)

fernet = get_fernet()

def encrypt(text):
    """Always returns string"""
    if text is None:
        return None
    return fernet.encrypt(text.encode()).decode()

def decrypt(ciphertext):
    """Handles both strings and bytes"""
    if ciphertext is None:
        return None
    try:
        if isinstance(ciphertext, str):
            return fernet.decrypt(ciphertext.encode()).decode()
        return fernet.decrypt(ciphertext).decode()
    except:
        return None  # Silently fail for compatibility