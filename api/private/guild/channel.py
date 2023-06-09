from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request

from api.models.channel import Channel, ChannelOut, CreateChannel
from api.models.guild import Guild
from api.models.member import GuildMember
from api.models.message import Message
from app.core.fastjwt import FastJWT

from api.private.guild.message import message_router

channel_router = APIRouter(prefix="/{guild_id}/channel")

channel_router.include_router(message_router)

@channel_router.post("/")
async def create_channel(request: Request, guild_id: str, channel: CreateChannel):
    if not ObjectId.is_valid(guild_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    auth_token = await FastJWT().decode(request.headers["Authorisation"])

    guild = await Guild.find_one({"_id": ObjectId(guild_id)})
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    if guild.owner != ObjectId(auth_token["id"]):
        raise HTTPException(status_code=403, detail="You are not owner of this guild")
    
    if len(channel.name) > 15:
        channel.name = channel.name[:15]
    
    if await Channel.find_one({"guild_id": ObjectId(guild_id), "name": channel.name}):
        _len = await Channel.find({"guild_id": ObjectId(guild_id), "name": {"$regex": f"^{channel.name}-"}}).count()
        channel.name = f"{channel.name}-{_len+1}"

    await Channel(**channel.dict(), guild_id=guild.id, created_at=datetime.now()).save()

    return {"message": "Channel created"}

@channel_router.get("/")
async def get_guild_channels(request: Request, guild_id: str):
    if not ObjectId.is_valid(guild_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    auth_token = await FastJWT().decode(request.headers["Authorisation"])
    
    guild = await Guild.find_one({"_id": ObjectId(guild_id)})
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    if guild.is_private and not await GuildMember.find_one({"guild_id": ObjectId(guild_id), "user_id": ObjectId(auth_token["id"])}):
        raise HTTPException(status_code=403, detail="You are not member of this guild")
    

    channels = await Channel.find({"guild_id": ObjectId(guild_id)}).to_list(1_000_000_000)
    guild_channels = []
    for channel in channels:
        channel = channel.dict()
        channel["id"] = str(channel["id"])
        channel = ChannelOut(**channel).dict()
        guild_channels.append(channel)

    return guild_channels


@channel_router.delete("/{channel_id}")
async def delete_channel(request: Request, guild_id: str, channel_id: str):
    if not ObjectId.is_valid(guild_id) or not ObjectId.is_valid(channel_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    auth_token = await FastJWT().decode(request.headers["Authorisation"])
    
    guild = await Guild.find_one({"_id": ObjectId(guild_id)})
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    if guild.owner != ObjectId(auth_token["id"]):
        raise HTTPException(status_code=403, detail="You are not owner of this guild")
    
    channel = await Channel.find_one({"_id": ObjectId(channel_id)})
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    await channel.delete()
    await (Message.find(
        {"guild_id": ObjectId(guild_id), "channel_id": ObjectId(channel_id)}
    )).delete()

    return {"message": "Channel deleted"}
