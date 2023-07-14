from bson import ObjectId
from fastapi import APIRouter, HTTPException

from api.models.user import BulkUsers, User, UserOut

users_router = APIRouter(prefix="/profile")

@users_router.get("/{query}")
async def get_user_profile(query: str):
    search_query = {"username": query}
    if ObjectId.is_valid(query):
        # raise HTTPException(status_code=400, detail="Invalid ID")
        search_query = {"_id": ObjectId(query)}

    user: User = (await User.find_one(search_query))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user = user.dict()
    user["id"] = str(user["id"])
    user: UserOut = UserOut(**user).dict()

    del user["email"]  # Remove email from response

    return user


@users_router.post("/bulk")
async def get_users_profiles(users: BulkUsers):
    _users = []
    for user in users.users:
        if not ObjectId.is_valid(user):
            continue  # Skip invalid IDs
        _users.append(ObjectId(user))

    _users = await User.find({"_id": {"$in": _users}}).to_list(1_000_000_000)
    _users_list = []
    for _user in _users:
        _user = _user.dict()
        _user["id"] = str(_user["id"])
        _user = UserOut(**_user).dict()
        del _user["email"]
        _users_list.append(_user)

    return _users_list
