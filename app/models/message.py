from pydantic import BaseModel
from beanie import Document, Indexed, PydanticObjectId
from bson import ObjectId
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class Message(Document):
    message: str
    author_id: PydanticObjectId
    guild_id: PydanticObjectId
    channel_id: PydanticObjectId
    created_at: datetime = datetime.now()

    class Settings:
        name = "messages"

class MessageOut(BaseModel):
    id: str
    message: str
    author_avatar: Optional[str] = "https://cdn.discordapp.com/embed/avatars/0.png"
    author_username: str
    created_at: datetime

class InternalMessage(BaseModel):
    message: str