import os
from cryptography.fernet import Fernet
from config import ENCRYPTION_KEY_FILE

# Zorg dat het key-bestand bestaat
if not os.path.exists(ENCRYPTION_KEY_FILE):
    key = Fernet.generate_key()
    with open(ENCRYPTION_KEY_FILE, 'wb') as f:
        f.write(key)
else:
    with open(ENCRYPTION_KEY_FILE, 'rb') as f:
        key = f.read()

fernet = Fernet(key)

def encrypt(text):
    return fernet.encrypt(text.encode()).decode()

def decrypt(ciphertext):
    return fernet.decrypt(ciphertext.encode()).decode()
