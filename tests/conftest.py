from beanie import init_beanie
from fastapi.testclient import TestClient
from app.main import app
import pytest
from mongomock_motor import AsyncMongoMockClient

from api.models.channel import Channel
from api.models.guild import Guild, GuildKey
from api.models.member import GuildMember
from api.models.user import User
from app.core.database import db
from api.models.message import InternalMessage, Message, MessageOut

@pytest.fixture(autouse=True)
async def my_fixture():
    client = AsyncMongoMockClient()
    await init_beanie(document_models=[User], database=client.get_database(name="denscord"))

@pytest.fixture(scope="module")
def client():
    return TestClient(app)
