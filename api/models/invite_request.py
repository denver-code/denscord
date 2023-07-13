from pydantic import BaseModel
from beanie import Document, Indexed, PydanticObjectId
from bson import ObjectId
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class Sender(BaseModel):
    id: str
    username: str
    avatar: str

class Recipient(BaseModel):
    id: str
    username: str
    avatar: str

class Guild(BaseModel):
    id: str
    name: str
    avatar: str
    description: str

class InviteRequestOut(BaseModel):
    id: str
    sender: Sender
    recipient: Recipient
    guild: Guild
    created_at: datetime

class InvitePayload(BaseModel):
    recipient_id: str
    guild_id: str

class InviteRequest(Document):
    sender_id: PydanticObjectId
    recipient_id: PydanticObjectId
    guild_id: PydanticObjectId
    created_at: datetime = datetime.now()

    class Settings:
        name = "invite_requests"
    
        unique_together = ("_id", "sender_id", "recipient_id", "guild_id")

