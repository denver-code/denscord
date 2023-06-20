import re
from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional

class User(Document):
    email: Indexed(EmailStr, unique=True)
    password: str
    username: Optional[str] = None
    avatar: Optional[str] = "https://www.gravatar.com/avatar/0bc83cb571cd1c50ba6f3e8a78ef1346"
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Settings:
        name = "users"
    

class UserOut(BaseModel):
    id: str
    email: Indexed(EmailStr, unique=True)
    username: Optional[str] = None
    avatar: Optional[str] = "https://www.gravatar.com/avatar/0bc83cb571cd1c50ba6f3e8a78ef1346"


class UserUpdate(BaseModel):
    username: Optional[str] = None
    avatar: Optional[str] = None

    @validator("avatar")
    def check_email_event(cls, v):
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        if v:
            if not re.fullmatch(regex, v):
                raise ValueError("Invalid email")
            return v
          
          
class BulkUsers(BaseModel):
    users: Optional[list[str]] = None

      
# class SetUsername(BaseModel):
#     username: str
