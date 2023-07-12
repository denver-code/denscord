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
    
        unique_together = ("_id", "guild_id", "channel_id")


class UserFrom(BaseModel):
    id: str
    is_bot: bool
    username: str
    avatar: str


class ChatIn(BaseModel):
    guild_id: str
    channel_id: str


class MessageMarkupOut(BaseModel):
    message_id: str
    from_user: UserFrom
    chat: ChatIn
    text: str

class MessageOut(BaseModel):
    message: MessageMarkupOut
    created_at: datetime


class InternalMessage(BaseModel):
    message: str