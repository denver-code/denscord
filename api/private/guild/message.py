from api.models.message import ChatIn, Message, MessageMarkupOut, UserFrom
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request
from api.models.channel import Channel
from api.models.guild import Guild
from api.models.member import GuildMember
from api.models.message import MessageOut
from api.models.user import User

from app.core.fastjwt import FastJWT

message_router = APIRouter(prefix="/{channel_id}/message")


@message_router.get("/")
async def get_messages(guild_id: str, channel_id: str, request: Request, limit: int = 100, offset: int = 0):
    if not ObjectId.is_valid(guild_id) or not ObjectId.is_valid(channel_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    auth_token = await FastJWT().decode(request.headers["Authorisation"])

    guild = await Guild.find_one({"_id": ObjectId(guild_id)})
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    if guild.is_private and not await GuildMember.find_one({"guild_id": ObjectId(guild_id), "user_id": ObjectId(auth_token["id"])}):
        raise HTTPException(status_code=403, detail="You are not member of this guild")

    channel = await Channel.find_one({"_id": ObjectId(channel_id), "guild_id": ObjectId(guild_id)})
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    
    messages = await Message.find({"channel_id": ObjectId(channel_id), "guild_id": ObjectId(guild_id)}).to_list(1_000_000_000_000)
    messages.sort(key=lambda x: x.created_at, reverse=True)
    messages = messages[offset:offset+limit]
    
    if not messages:
        return []
    
    users_hashmap = {}
    _messages_out = []

    for m in messages:
        m = m.dict()
        m["id"] = str(m["id"])

        if not users_hashmap.get(m["author_id"]):
            user = await User.find_one({"_id": m["author_id"]})
            users_hashmap[m["author_id"]] = user.dict()
        
        message_out = MessageOut(
            message=MessageMarkupOut(
                message_id=m["id"],
                from_user=UserFrom(
                    id=str(m["author_id"]),
                    is_bot=False,
                    username=users_hashmap[m["author_id"]]["username"],
                    avatar=users_hashmap[m["author_id"]]["avatar"]
                ),
                chat=ChatIn(guild_id=guild_id, channel_id=channel_id),
                text=m["message"]
            ),
            created_at=m["created_at"]
    )

        _messages_out.append(message_out.dict())

    return  _messages_out


@message_router.delete("/{message_id}")
async def delete_message(guild_id: str, channel_id: str, message_id: str, request: Request):
    # check if all ids are valid
    if not ObjectId.is_valid(guild_id) or not ObjectId.is_valid(channel_id) or not ObjectId.is_valid(message_id):
        raise HTTPException(status_code=400, detail="Invalid ID")

    # get user token
    auth_token = await FastJWT().decode(request.headers["Authorisation"])

    # get guild, channel and message
    guild = await Guild.find_one({"_id": ObjectId(guild_id)})
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    channel = await Channel.find_one({"_id": ObjectId(channel_id), "guild_id": ObjectId(guild_id)})
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    message = await Message.find_one({"_id": ObjectId(message_id), "channel_id": ObjectId(channel_id), "guild_id": ObjectId(guild_id)})
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # check if user is member of guild or a owner
    if not await GuildMember.find_one({"guild_id": ObjectId(guild_id), "user_id": ObjectId(auth_token["id"])}):
        raise HTTPException(status_code=403, detail="You are not member of this guild")

    # check if user is author of message or a owner
    print(message.author_id, auth_token["id"], guild.owner)
    if not message.author_id == ObjectId(auth_token["id"]) and not guild.owner == ObjectId(auth_token["id"]):
        raise HTTPException(status_code=403, detail="You are not the author of this message")

    # delete message

    await message.delete()

    return {"message":"deleted"}
