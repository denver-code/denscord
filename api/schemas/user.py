import re
from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr, validator

class UserAuthorisation(BaseModel):
    email: EmailStr
    password: str
    
    @validator("email")
    def check_email_event(cls, v):
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        if not re.fullmatch(regex, v):
            raise ValueError("Invalid email")
        return v
    

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: str

    @validator("email")
    def check_email_event(cls, v):
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        if not re.fullmatch(regex, v):
            raise ValueError("Invalid email")
        return v
    