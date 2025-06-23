from cryptography.fernet import Fernet
from flask import current_app

def get_cipher():
    """
    Initializes and returns a Fernet cipher instance using the app's secret key.
    """
    key = current_app.config['ENCRYPTION_KEY']
    if not key:
        raise ValueError("ENCRYPTION_KEY not set in config")
    return Fernet(key.encode())

def encrypt_data(data):
    """
    Encrypts the given data.
    """
    if data is None:
        return None
    cipher = get_cipher()
    return cipher.encrypt(str(data).encode()).decode()

def decrypt_data(encrypted_data):
    """
    Decrypts the given encrypted data.
    """
    if encrypted_data is None:
        return None
    cipher = get_cipher()
    try:
        return cipher.decrypt(encrypted_data.encode()).decode()
    except Exception:
        # If decryption fails, it could be legacy data or an error.
        # Return the original data or handle as per your policy.
        return encrypted_data
