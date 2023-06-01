from fastapi import APIRouter, HTTPException
from api.models.user import User
from api.schemas.user import UserAuthorisation, UserRegister
from app.core.fastjwt import FastJWT
from app.core.password import hash_password


authorisation_router = APIRouter(prefix="/authorisation")
    

@authorisation_router.post("/signup")
async def signup_event(user_auth_model: UserRegister):
    if await User.find_one({"email": user_auth_model.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    if await User.find_one({"username": user_auth_model.username}):
        raise HTTPException(status_code=400, detail="Username already registered")
    user_auth_model.password = hash_password(user_auth_model.password)
    user = User(
        email=user_auth_model.email,
        password=user_auth_model.password,
        username=user_auth_model.username
    )
    await user.save()
    return {"message": "User created"}


@authorisation_router.post("/signin")
async def signin_event(user_auth_model: UserAuthorisation):
    user = await User.find_one({"email": user_auth_model.email})
    if user_auth_model is None or hash_password(user_auth_model.password) != user.password:
        raise HTTPException(status_code=401, detail="Bad email or password")
    
    jwt_token = await FastJWT().encode(optional_data={
        "id": str(user.id),
        "email": user_auth_model.email,
    })

    return {"token": jwt_token}
