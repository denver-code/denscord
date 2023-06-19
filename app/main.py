from datetime import datetime
import json

from bson import ObjectId, json_util
from api.models.message import InternalMessage, Message, MessageOut
import random
from beanie import init_beanie
from fastapi import APIRouter, Cookie, Depends, FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from api.models.channel import Channel
from api.models.guild import Guild, GuildKey
from api.models.member import GuildMember
from api.models.user import User
from api.ws_notifier import ConnectionManager

from app.core.config import settings
from app.core.database import db

from api.router import api_router
from starlette.websockets import WebSocketState

from app.core.fastjwt import FastJWT

def get_application():
    _app = FastAPI(title=settings.PROJECT_NAME)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = get_application()


@app.on_event("startup")
async def on_startup():
    await init_beanie(
        database=db, document_models=[
            User,
            Guild,
            GuildMember, 
            GuildKey, 
            Channel, 
            Message
        ],
    )

app.include_router(api_router)


manager = ConnectionManager()

async def upload_message(message, guild_id, channel_id, user):
    message = await Message(
        message=message,
        guild_id=guild_id,
        channel_id=channel_id,
        author_id=user.id,
        created_at=datetime.now()
        
    ).save()
    message.id = str(message.id)

    return MessageOut(**message.dict(), author_avatar=user.avatar, author_username=user.username).dict()

@app.websocket("/ws/{guild_id}/{channel_id}")
async def ws_endpoint(websocket: WebSocket, guild_id: str, channel_id: str):
    try:
        token = websocket.headers.get("Authorisation")
        if not token or not await FastJWT().decode(token):
            return await websocket.close()
        token = await FastJWT().decode(token)

        if not ObjectId.is_valid(guild_id) or not ObjectId.is_valid(channel_id):
            return await websocket.close()

        guild = await Guild.find_one({"_id": ObjectId(guild_id)})
        channel = await Channel.find_one({"_id": ObjectId(channel_id)})
        member = await GuildMember.find_one(
            {"guild_id": ObjectId(guild_id), "user_id": ObjectId(token["id"])}
        )
        user = await User.find_one({"_id": ObjectId(token["id"])})

        if not guild or not channel or not member or not user:
            return await websocket.close()
        
        await manager.connect(websocket)
        while True:
            if websocket.client_state == WebSocketState.CONNECTED:
                message = json.loads(await websocket.receive_text())

                try:
                    message = InternalMessage(**message)
                except:
                    await websocket.send_json({"error": "Invalid message"})
                    continue

                message_out = await upload_message(
                    message.message, guild_id, channel_id, user
                )
                await manager.broadcast(
                    json.dumps(
                        message_out,
                        default=json_util.default
                    )
                )
            else:
                manager.connect(websocket)

    except Exception as e:
        manager.disconnect(websocket)
