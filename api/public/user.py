from bson import ObjectId
from fastapi import APIRouter, HTTPException

from api.models.user import BulkUsers, User, UserOut

users_router = APIRouter(prefix="/profile")

@users_router.get("/bulk")
@users_router.get("/{id}")
async def get_user_profile(id: str, users: BulkUsers = None):
    if users:
        print(users.users)
        _users = await User.find({"_id": {"$in": [ObjectId(user) for user in users.users]}}).to_list(1_000_000_000)
        _users_list = []
        for _user in _users:
            _user = _user.dict()
            _user["id"] = str(_user["id"])
            _user = UserOut(**_user).dict()
            del _user["email"]
            _users_list.append(_user)
        
        return _users_list

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