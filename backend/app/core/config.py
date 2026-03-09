from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/ai_image_db"

    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

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

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
