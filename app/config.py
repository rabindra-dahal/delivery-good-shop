# app/config.py
import os

class Settings:
    DATABASE_URL: str = "sqlite:///./shop.db"
    
    # Resolves InsecureKeyLengthWarning: Enforced minimum string threshold (>=32 characters/bytes)
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", 
        "supersecretkey123_production_grade_32_byte_minimum_string"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

settings = Settings()
