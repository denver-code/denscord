import bcrypt

from app.core.config import settings


def hash_password(password: str) -> str:
    """Returns a salted password hash"""
    
    return bcrypt.hashpw(password.encode(), settings.SALT_SECRET_KEY.encode()).decode()