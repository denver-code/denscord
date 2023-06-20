from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from api.models.user import SetUsername, User, UserOut, UserUpdate
from libgravatar import Gravatar

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


# @profile_router.post("/username")
# async def set_username(request: Request, new_username: SetUsername):
#     if await User.find_one({"username": new_username.username}):
#         raise HTTPException(status_code=400, detail="Username already registered")
    
#     auth_token = await FastJWT().decode(request.headers["Authorisation"])

#     user: User = await User.find_one({"email": auth_token["email"]})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
    
#     user.username = new_username.username
#     await user.save()

#     return {"message": "Username updated"}


@profile_router.put("/")
async def update_profile(request: Request, user_data: UserUpdate):
    if not user_data.username and not user_data.avatar:
        raise HTTPException(status_code=400, detail="No data to update")
    
    auth_token = await FastJWT().decode(request.headers["Authorisation"])

    user: User = await User.find_one({"email": auth_token["email"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user_data.username:
        if await User.find_one({"username": user_data.username}):
            raise HTTPException(status_code=400, detail="Username already registered")
        user.username = user_data.username
    
    if user_data.avatar:
        _avatar = Gravatar(user_data.avatar).get_image(size=256, default="identicon")
        user.avatar = _avatar

    user.updated_at = datetime.now()
    await user.save()

    user.id = str(user.id)
    _user_out = UserOut(**user.dict()).dict()

    return _user_out
        