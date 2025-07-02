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

def encrypt_file(input_path, output_path=None):
    """
    Encrypt a file
    Args:
        input_path: path to file to encrypt
        output_path: path to save encrypted file (defaults to input_path + '.enc')
    """
    if output_path is None:
        output_path = input_path + '.enc'
    
    with open(input_path, 'rb') as f:
        data = f.read()
    
    encrypted_data = fernet.encrypt(data)
    
    with open(output_path, 'wb') as f:
        f.write(encrypted_data)
    
    return output_path

def decrypt_file(input_path, output_path=None):
    """
    Decrypt a file
    Args:
        input_path: path to encrypted file
        output_path: path to save decrypted file (defaults to input_path without '.enc')
    """
    if output_path is None:
        if input_path.endswith('.enc'):
            output_path = input_path[:-4]
        else:
            output_path = input_path + '.decrypted'
    
    with open(input_path, 'rb') as f:
        encrypted_data = f.read()
    
    try:
        decrypted_data = fernet.decrypt(encrypted_data)
    except:
        return None
    
    with open(output_path, 'wb') as f:
        f.write(decrypted_data)
    
    return output_path