from fastapi import APIRouter
from api.public.authorisation import authorisation_router

public_router = APIRouter(prefix="/public")

public_router.include_router(authorisation_router)