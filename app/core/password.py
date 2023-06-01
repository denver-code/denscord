import bcrypt

from app.core.config import settings


def hash_password(password: str) -> str:
    """Returns a salted password hash"""
    
    return bcrypt.hashpw(password.encode(), settings.SALT_SECRET_KEY.encode()).decode()

def generate_password(length: int = 8) -> str:
    """Returns a random string of length"""
    
    return bcrypt.gensalt(length).decode()