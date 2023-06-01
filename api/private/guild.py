from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request

from api.models.guild import CreateGuild, Guild, GuildKey, GuildOut
from api.models.member import GuildMember
from api.models.user import User
from app.core.fastjwt import FastJWT
from app.core.password import generate_password

guild_router = APIRouter(prefix="/guild")

@guild_router.post("/")
async def create_guild(guild_data: CreateGuild, request: Request):
    auth_token = await FastJWT().decode(request.headers["Authorisation"])

    user: User = (await User.find_one({"email": auth_token["email"]}))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    guild = await Guild(**guild_data.dict(), owner=user.id).save()
    await GuildMember(guild_id=guild.id, user_id=user.id).save()
    
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
    if not guild:
        raise HTTPException(status_code=404, detail="Guild not found")
    
    guild = guild.dict()
    guild["id"] = str(guild["id"])
    guild = GuildOut(**guild).dict()

    members = await GuildMember.find({"guild_id": ObjectId(id)}).to_list(1_000_000_000)

    guild["members_count"] = len(members)

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

    key = generate_password(length=10)
    
    await GuildKey(guild_id=guild.id, key=key).save()

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
    
    await guild.delete()

    await GuildMember.delete_many({"guild_id": ObjectId(id)})
    await GuildKey.delete_many({"guild_id": ObjectId(id)})
    # TODO: delete all channels

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
    await guild.commit()

    return {"message": "Visibility changed.", "is_private": guild.is_private}

@guild_router.get("/{id}/leave")
async def leave_guild(id: str, request: Request):
    pass 

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
        if _key.key != key:
            raise HTTPException(status_code=404, detail="Guild not found")

    if await GuildMember.find_one({"guild_id": ObjectId(id), "user_id": ObjectId(user.id)}):
        raise HTTPException(status_code=400, detail="User already in guild")

    await GuildMember(guild_id=guild.id, user_id=user.id).save()

    return {"message": "Joined guild"}