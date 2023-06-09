from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request

from api.models.guild import CreateGuild, Guild, GuildKey, GuildOut
from api.models.member import GuildMember
from api.models.channel import Channel
from api.models.message import Message
from api.models.user import User
from app.core.fastjwt import FastJWT
from app.core.password import generate_password
from api.private.guild.channel import channel_router

guild_router = APIRouter(prefix="/guild")

guild_router.include_router(channel_router)

@guild_router.post("/")
async def create_guild(guild_data: CreateGuild, request: Request):
    auth_token = await FastJWT().decode(request.headers["Authorisation"])

    user: User = (await User.find_one({"email": auth_token["email"]}))
    if not user:
        # TODO: Return Unauthorised
        raise HTTPException(status_code=404, detail="User not found")

    if len(guild_data.name) > 15:
        guild_data.name = guild_data.name[:15]
    
    guild = await Guild(**guild_data.dict(), owner=user.id, created_at=datetime.now()).save()
    await GuildMember(guild_id=guild.id, user_id=user.id, created_at=datetime.now()).save()
    
    return {"message": "Guild created"}

@guild_router.get("/")
async def get_my_guilds(request: Request):
    auth_token = await FastJWT().decode(request.headers["Authorisation"])

    guilds_id_list = await GuildMember.find({"user_id": ObjectId(auth_token["id"])}).to_list(100000)
    guilds = []
    for id in guilds_id_list:
        _g = await Guild.find_one({"_id": ObjectId(id.guild_id)})
        _g = _g.dict()
        _g["id"] = str(_g["id"])
        _g["members_count"] = len(await GuildMember.find({"guild_id": ObjectId(id.guild_id)}).to_list(1_000_000_000))

        guilds.append(GuildOut(**_g).dict())

    return guilds


@guild_router.get("/{id}")
async def get_guild(id: str, request: Request):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    auth_token = await FastJWT().decode(request.headers["Authorisation"])

    guild = await Guild.find_one({"_id": ObjectId(id)})
    
    if not guild or (guild.is_private == True and not await GuildMember.find_one({"guild_id": ObjectId(id), "user_id": ObjectId(auth_token["id"])})):
        raise HTTPException(status_code=404, detail="Guild not found")
    
    guild = guild.dict()
    guild["id"] = str(guild["id"])
    members = await GuildMember.find({"guild_id": ObjectId(id)}).to_list(1_000_000_000)

    guild["members_count"] = len(members)
    guild = GuildOut(**guild).dict()

    return guild


@guild_router.get("/{id}/key")
async def set_guild_key(id: str, request: Request):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    auth_token = await FastJWT().decode(request.headers["Authorisation"])
    
    guild = await Guild.find_one({"_id": ObjectId(id)})
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    if guild.owner != ObjectId(auth_token["id"]):
        raise HTTPException(status_code=401, detail="You are not the owner of this guild")
    
    if guild.is_private == False:
        raise HTTPException(status_code=400, detail="Guild is not private")

    key = generate_password()
    
    await GuildKey(guild_id=guild.id, key=key, created_at=datetime.now()).save()

    return {"message": "Keep it safe.", "key": key}

@guild_router.delete("/{id}/key")
async def delete_guild_key(id: str, request: Request):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    auth_token = await FastJWT().decode(request.headers["Authorisation"])
    
    guild = await Guild.find_one({"_id": ObjectId(id)})
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    if guild.owner != ObjectId(auth_token["id"]):
        raise HTTPException(status_code=401, detail="You are not the owner of this guild")
    
    if guild.is_private == False:
        raise HTTPException(status_code=400, detail="Guild is not private")

    key = await GuildKey.find_one({"guild_id": ObjectId(id)})
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
    
    await key.delete()

    return {"message": "Key deleted."}

@guild_router.delete("/{id}")
async def delete_guild(id: str, request: Request):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    auth_token = await FastJWT().decode(request.headers["Authorisation"])
    
    guild = await Guild.find_one({"_id": ObjectId(id)})
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    if guild.owner != ObjectId(auth_token["id"]):
        raise HTTPException(status_code=401, detail="You are not the owner of this guild")
    
    await (GuildMember.find({"guild_id": ObjectId(id)})).delete() 
    await (GuildKey.find({"guild_id": ObjectId(id)})).delete() 
    await (Channel.find({"guild_id": ObjectId(id)})).delete()
    await (Message.find({"guild_id": ObjectId(id)})).delete()

    await guild.delete()

    return {"message": "Guild deleted."}

@guild_router.get("/{id}/members")
async def get_guild_members(id: str, request: Request):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    auth_token = await FastJWT().decode(request.headers["Authorisation"])
    
    guild = await Guild.find_one({"_id": ObjectId(id)})
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    if guild.is_private and guild.owner != ObjectId(auth_token["id"]):
        member = await GuildMember.find_one({"guild_id": ObjectId(id), "user_id": ObjectId(auth_token["id"])})
        if not member:
            raise HTTPException(status_code=401, detail="You are not in this guild")
    
    members = await GuildMember.find({"guild_id": ObjectId(id)}).to_list(1_000_000_000)
    members = [str(member.user_id) for member in members]

    return members

@guild_router.get("/{id}/change_visibility")
async def change_guild_visibility(id: str, request: Request):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    auth_token = await FastJWT().decode(request.headers["Authorisation"])
    
    guild = await Guild.find_one({"_id": ObjectId(id)})
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    if guild.owner != ObjectId(auth_token["id"]):
        raise HTTPException(status_code=401, detail="You are not the owner of this guild")
    
    guild.is_private = not guild.is_private
    await guild.save()

    return {"message": "Visibility changed.", "is_private": guild.is_private}

@guild_router.get("/{id}/leave")
async def leave_guild(id: str, request: Request):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    auth_token = await FastJWT().decode(request.headers["Authorisation"])

    guild_membership = await GuildMember.find_one({"guild_id": ObjectId(id), "user_id": ObjectId(auth_token["id"])})
    if not guild_membership:
        raise HTTPException(status_code=404, detail="You are not in this guild")
    
    guild = await Guild.find_one({"_id": ObjectId(id)})
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    if guild.owner == ObjectId(auth_token["id"]):
        raise HTTPException(status_code=400, detail="You can't leave your own guild")
    
    await guild_membership.delete()

    return {"message": "Left guild."}

@guild_router.get("/{id}/join")
@guild_router.get("/{id}/join/{key}")
async def join_guild(id: str, request: Request, key: str = ""):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    auth_token = await FastJWT().decode(request.headers["Authorisation"])

    user: User = (await User.find_one({"email": auth_token["email"]}))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    guild = await Guild.find_one({"_id": ObjectId(id)})
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")

    if guild.is_private:
        _key = await GuildKey.find_one({"guild_id": ObjectId(id)})
        if not _key or _key.key != key:
            raise HTTPException(status_code=404, detail="Guild not found")

    if await GuildMember.find_one({"guild_id": ObjectId(id), "user_id": ObjectId(user.id)}):
        raise HTTPException(status_code=400, detail="User already in guild")

    await GuildMember(guild_id=guild.id, user_id=user.id, created_at=datetime.now()).save()

    return {"message": "Joined guild"}

@guild_router.delete("/{id}/{user_id}")
async def kick_user(id: str, user_id: str, request: Request):
    if not ObjectId.is_valid(id) or not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    auth_token = await FastJWT().decode(request.headers["Authorisation"])

    guild = await Guild.find_one({"_id": ObjectId(id)})
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    if guild.owner != ObjectId(auth_token["id"]):
        raise HTTPException(status_code=401, detail="You are not the owner of this guild")
    
    if guild.owner == ObjectId(user_id):
        raise HTTPException(status_code=400, detail="You cannot kick the owner of the guild")
    
    member = await GuildMember.find_one({"guild_id": ObjectId(id), "user_id": ObjectId(user_id)})
    if not member:
        raise HTTPException(status_code=404, detail="User not found")
    
    await member.delete()

    return {"message": "Kicked user."}

