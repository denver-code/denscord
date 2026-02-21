import secrets
import string
import bcrypt

from app.core.config import settings

def hash_password(password: str) -> str:
    """
    Returns a salted password hash using a unique, 
    automatically generated salt.
    """
    pwd_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt(rounds=12))
    
    return hashed.decode('utf-8')

def generate_password(length: int = 10) -> str:
    """Returns a random string of length"""
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    
    return password