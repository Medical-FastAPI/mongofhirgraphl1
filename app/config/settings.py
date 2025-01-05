from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "FHIR Server"
    MONGODB_URL: str = "mongodb://mongo:UmxHXTOOXKBaiFQUnsawgcTQSmwkOHBw@autorack.proxy.rlwy.net:54479"
    DATABASE_NAME: str = "cursor5"
    DEBUG: bool = False

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()