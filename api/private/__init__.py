from fastapi import APIRouter, Depends
from api.private.user.profile import profile_router
from app.core.fastjwt import FastJWT

private_router = APIRouter(prefix="/private", dependencies=[Depends(FastJWT().login_required)])
private_router.include_router(profile_router)