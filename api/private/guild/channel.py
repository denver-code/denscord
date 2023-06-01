from fastapi import APIRouter, Request

channel_router = APIRouter(prefix="/{guild_id}/channel")

@channel_router.post("/")
async def create_channel(request: Request, guild_id: str):
    pass

