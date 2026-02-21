
from typing import List, Union

from pydantic import AnyHttpUrl, BaseSettings, validator



class Settings(BaseSettings):
    PROJECT_NAME: str
    BACKEND_CORS_ORIGINS: List[str] = []
    DATABASE_URL: str
    SALT_SECRET_KEY: str
    JWT_SECRET_KEY: str



    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
