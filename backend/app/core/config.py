from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List, Union
import json


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/ai_image_db"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000"]

    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # Fallback: split by comma
                return [origin.strip() for origin in v.split(',')]
        return v

    # Gemini API
    GEMINI_API_KEY: Optional[str] = None

    # Banana.dev API (Stable Diffusion)
    BANANA_API_KEY: Optional[str] = None
    BANANA_MODEL_KEY: str = "stable-diffusion-v1-5"

    # Image storage
    IMAGE_STORAGE_PATH: str = "./generated_images"

    # App
    APP_NAME: str = "AI Image Generator"
    DEBUG: bool = True

    # Default admin (disabled by default for security)
    CREATE_DEFAULT_ADMIN: bool = False
    DEFAULT_ADMIN_USERNAME: Optional[str] = None
    DEFAULT_ADMIN_PASSWORD: Optional[str] = None
    DEFAULT_ADMIN_EMAIL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
