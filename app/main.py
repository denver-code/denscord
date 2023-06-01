from beanie import init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.models.channel import Channel
from api.models.guild import Guild, GuildKey
from api.models.member import GuildMember
from api.models.user import User

from app.core.config import settings
from app.core.database import db

from api.router import api_router


def get_application():
    _app = FastAPI(title=settings.PROJECT_NAME)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = get_application()


@app.on_event("startup")
async def on_startup():
    await init_beanie(
        database=db, document_models=[User, Guild, GuildMember, GuildKey, Channel],
    )

app.include_router(api_router)