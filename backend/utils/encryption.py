from typing import Optional, Any, Union
from cryptography.fernet import Fernet
from flask import current_app

def get_cipher() -> Fernet:
    """
    Initializes and returns a Fernet cipher instance using the app's secret key.
    
    Returns:
        Fernet cipher instance
        
    Raises:
        ValueError: If ENCRYPTION_KEY is not set in the application config
    """
    key = current_app.config['ENCRYPTION_KEY']
    if not key:
        raise ValueError("ENCRYPTION_KEY not set in config")
    return Fernet(key.encode())

def encrypt_data(data: Any) -> Optional[str]:
    """
    Encrypts the given data.
    
    Args:
        data: The data to encrypt
        
    Returns:
        Encrypted data as a string, or None if input was None
    """
    if data is None:
        return None
    cipher = get_cipher()
    return cipher.encrypt(str(data).encode()).decode()

def decrypt_data(encrypted_data: Optional[str]) -> Optional[str]:
    """
    Decrypts the given encrypted data.
    
    Args:
        encrypted_data: The encrypted data to decrypt
        
    Returns:
        Decrypted data as a string, or None if input was None.
        If decryption fails, returns the original encrypted data.
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
