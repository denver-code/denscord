from fastapi import APIRouter, Depends
from api.private.user.profile import profile_router
from app.core.fastjwt import FastJWT
from api.private.guild.guild import guild_router
from api.private.user.social import social_router

private_router = APIRouter(prefix="/private", dependencies=[Depends(FastJWT().login_required)])
private_router.include_router(profile_router)
private_router.include_router(guild_router)
private_router.include_router(social_router)