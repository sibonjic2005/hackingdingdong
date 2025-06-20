# src/Data/crypto.py
from cryptography.fernet import Fernet
import os
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())  # Copy this output
# Generate this once and keep it constant
# To generate: Fernet.generate_key().decode()
KEY = b'5TV_WeLP1H1rNXOLJJb4CG4DqrgC24rLFbdU_zPG6CQ='  # Replace with your actual key

def encryptfile(file_path):
    """Encrypt a file in-place, creating .enc version"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        fernet = Fernet(KEY)
        encrypted = fernet.encrypt(data)
        
        encrypted_path = f"{file_path}.enc"
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted)
            
        return encrypted_path
    except Exception as e:
        raise Exception(f"File encryption failed: {str(e)}")

def decryptfile(encrypted_data):
    """Decrypt bytes data"""
    try:
        if not encrypted_data:
            return b""
        fernet = Fernet(KEY)
        return fernet.decrypt(encrypted_data)
    except Exception as e:
        raise Exception(f"Decryption failed: {str(e)}")
    
def encrypt(text):
    return fernet.encrypt(text.encode()).decode()

def decrypt(ciphertext):
    return fernet.decrypt(ciphertext.encode()).decode()