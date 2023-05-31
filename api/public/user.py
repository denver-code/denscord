from bson import ObjectId
from fastapi import APIRouter, HTTPException

from api.models.user import User, UserOut

users_router = APIRouter(prefix="/profile")

@users_router.get("/{id}")
async def get_user_profile(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid ID")
    
    user: User = (await User.find_one({"_id": ObjectId(id)}))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = user.dict()
    user["id"] = str(user["id"])
    user: UserOut = UserOut(**user).dict()

    del user["email"]  # Remove email from response

    return user