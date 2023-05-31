from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr

class UserAuthorisation(BaseModel):
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    username: str