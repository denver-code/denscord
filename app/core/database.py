import motor.motor_asyncio
from beanie import Document
from app.core.config import settings
from datetime import datetime


client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.DATABASE_URL, uuidRepresentation="standard"
)
db = client["denscord"]