import secrets
import string
import bcrypt

from app.core.config import settings


def hash_password(password: str) -> str:
    """Returns a salted password hash"""
    
    return password

def generate_password(length: int = 10) -> str:
    """Returns a random string of length"""
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    
    return password