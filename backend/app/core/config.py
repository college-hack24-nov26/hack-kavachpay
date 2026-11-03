import os
from pydantic import BaseModel

class Settings(BaseModel):
    APP_NAME: str = "KavachSetu – The Ghost Protocol"
    APP_TAGLINE: str = "Prove, Don't Share."
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./kavachsetu.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "kavachsetu_ghost_protocol_secure_jwt_secret_key_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

settings = Settings()

