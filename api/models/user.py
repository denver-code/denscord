from beanie import Document, Indexed
from pydantic import EmailStr
from datetime import datetime
from typing import Optional

class User(Document):
    email: Indexed(EmailStr, unique=True)
    password: str
    username: Optional[str] = None
    avatar: Optional[str] = "https://cdn.discordapp.com/embed/avatars/0.png"
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Settings:
        name = "users"

