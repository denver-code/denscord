from beanie import Document, Indexed, PydanticObjectId
from bson import ObjectId
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class Channel(Document):
    name: str
    description: str
    server_id: PydanticObjectId
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    # TODO: Add permissions field

    class Settings:
        name = "channels"

  
class ChannelOut(BaseModel):
    id: str
    name: str
    description: str
    server_id: PydanticObjectId


class CreateChannel(BaseModel):
    name: str
    description: str