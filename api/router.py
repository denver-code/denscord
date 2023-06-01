from fastapi import APIRouter, WebSocket
from api.public import public_router
from api.private import private_router
from api.ws_notifier import ConnectionManager

api_router = APIRouter(prefix="/api")

api_router.include_router(public_router)
api_router.include_router(private_router)
