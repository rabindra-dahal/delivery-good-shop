import os
from datetime import timedelta

class Settings:
    DATABASE_URL: str = "sqlite:///./shop.db"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkey123")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

settings = Settings()
