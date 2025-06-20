import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from cryptography.fernet import Fernet

key = Fernet.generate_key()
fernet = Fernet(key)

def encrypt(text):
    return fernet.encrypt(text.encode()).decode()

def decrypt(ciphertext):
    return fernet.decrypt(ciphertext.encode()).decode()
