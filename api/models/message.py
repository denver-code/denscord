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
    author_avatar: Optional[str] = "https://www.gravatar.com/avatar/0bc83cb571cd1c50ba6f3e8a78ef1346"
    author_username: str
    created_at: datetime

class InternalMessage(BaseModel):
    message: str