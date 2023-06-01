from beanie import Document, Indexed, PydanticObjectId
from bson import ObjectId
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class GuildMember(Document):
    guild_id: PydanticObjectId
    user_id: PydanticObjectId
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    class Settings:
        name = "members"