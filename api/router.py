from fastapi import APIRouter
from api.public import public_router

api_router = APIRouter(prefix="/api")

api_router.include_router(public_router)
