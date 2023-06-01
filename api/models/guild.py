from beanie import Document, Indexed, PydanticObjectId
from bson import ObjectId
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class Guild(Document):
    name: str
    description: str
    avatar: Optional[str] = "https://cdn.discordapp.com/embed/avatars/0.png"
    owner: PydanticObjectId
    is_private: bool = False
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Settings:
        name = "guilds"

class GuildKey(Document):
    guild_id: PydanticObjectId
    key: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Settings:
        name = "keys"
  
class GuildOut(BaseModel):
    id: str
    name: str
    description: str
    avatar: Optional[str] = "https://cdn.discordapp.com/embed/avatars/0.png"
    owner: PydanticObjectId
    members_count: int


class CreateGuild(BaseModel):
    name: str
    description: str
    is_private: bool
    avatar: Optional[str] = "https://cdn.discordapp.com/embed/avatars/0.png"

class UpdateGuild(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None
    is_private: Optional[bool] = None