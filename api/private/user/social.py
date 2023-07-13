from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request
from api.models.guild import Guild
from api.models.invite_request import InvitePayload, InviteRequest, InviteRequestOut, Recipient, Sender, Guild as InviteGuild
from api.models.member import GuildMember
from api.models.user import User
from app.core.fastjwt import FastJWT

social_router = APIRouter(prefix="/social")

@social_router.post("/")
async def create_invite(request: Request, invite_payload: InvitePayload):
    auth_token = await FastJWT().decode(request.headers["Authorisation"])

    user_sender: User = await User.find_one({"email": auth_token["email"]})
    if not user_sender:
        raise HTTPException(status_code=404, detail="User not found")

    user_receiver: User = await User.find_one({"_id": ObjectId(invite_payload.recipient_id)})
    target_guild = await Guild.find_one({"_id": ObjectId(invite_payload.guild_id)})
    if not user_receiver or not target_guild:
        raise HTTPException(status_code=404, detail="User or guild not found")

    if not user_sender.id == target_guild.owner:
        raise HTTPException(status_code=403, detail="Sender is not guild owner")
    
    if not user_receiver.allow_invites:
        raise HTTPException(status_code=403, detail="User does not allow invites")
    
    if await GuildMember.find_one({"user_id": user_receiver.id, "guild_id": target_guild.id}):
        raise HTTPException(status_code=403, detail="User already in guild")
    
    invite = InviteRequest(
        sender_id = user_sender.id,
        recipient_id = user_receiver.id,
        guild_id = target_guild.id,
        created_at = datetime.now()
    )

    await invite.save()


    invite_out: InviteRequestOut = InviteRequestOut(
        id = str(invite.id),
        sender = Sender(
            id = str(user_sender.id),
            username = user_sender.username,
            avatar = user_sender.avatar
        ),
        recipient= Recipient(
            id = str(user_receiver.id),
            username = user_receiver.username,
            avatar = user_receiver.avatar
        ),
        guild = InviteGuild(
            id = str(target_guild.id),
            name = target_guild.name,
            avatar = target_guild.avatar,
            description = target_guild.description
        ),
        created_at = invite.created_at
    )

    return invite_out


@social_router.get("/")
async def get_invites(request: Request):
    auth_token = await FastJWT().decode(request.headers["Authorisation"])

    user: User = await User.find_one({"email": auth_token["email"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    invites = await InviteRequest.find({"recipient_id": user.id}).to_list(length=1000000)

    invites_out = []

    for invite in invites:
        sender: User = await User.find_one({"_id": invite.sender_id})
        guild: Guild = await Guild.find_one({"_id": invite.guild_id})

        invite_out = InviteRequestOut(
            id = str(invite.id),
            sender = Sender(
                id = str(sender.id),
                username = sender.username,
                avatar = sender.avatar
            ),
            recipient= Recipient(
                id = str(user.id),
                username = user.username,
                avatar = user.avatar
            ),
            guild = InviteGuild(
                id = str(guild.id),
                name = guild.name,
                avatar = guild.avatar,
                description = guild.description
            ),
            created_at = invite.created_at
        )

        invites_out.append(invite_out)
    
    return invites_out

@social_router.get("/{invite_id}/{action}")
async def handle_invite(request: Request, invite_id: str, action: str):
    auth_token = await FastJWT().decode(request.headers["Authorisation"])

    user: User = await User.find_one({"email": auth_token["email"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    invite: InviteRequest = await InviteRequest.find_one({"_id": ObjectId(invite_id), "recipient_id": user.id})
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    
    if action == "accept":
        guild: Guild = await Guild.find_one({"_id": invite.guild_id})
        if not guild:
            await invite.delete()
            raise HTTPException(status_code=404, detail="Guild not found, invite will be deleted")
        
        if await GuildMember.find_one({"user_id": user.id, "guild_id": guild.id}):
            await invite.delete()
            raise HTTPException(status_code=403, detail="User already in guild, invite will be deleted")
        
        await GuildMember(
            user_id = user.id,
            guild_id = guild.id,
            created_at = datetime.now()
        ).save()
        await invite.delete()
        return {"message": "Invite accepted"}
    
    elif action == "decline":
        await invite.delete()
        return {"message": "Invite declined"}
    
    return {"message": "Invalid action"}

