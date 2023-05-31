from fastapi import APIRouter, HTTPException, Request
from api.models.user import SetUsername, User, UserOut

from app.core.fastjwt import FastJWT

profile_router = APIRouter(prefix="/profile")

@profile_router.get("/")
async def get_profile(request: Request):
    auth_token = await FastJWT().decode(request.headers["Authorisation"])

    user: User = (await User.find_one({"email": auth_token["email"]}))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = user.dict()
    user["id"] = str(user["id"])
    user = UserOut(**user).dict()

    return user

@profile_router.post("/username")
async def set_username(request: Request, new_username: SetUsername):
    if await User.find_one({"username": new_username.username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    auth_token = await FastJWT().decode(request.headers["Authorisation"])

    user: User = await User.find_one({"email": auth_token["email"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.username = new_username.username
    await user.save()

    return {"message": "Username updated"}
