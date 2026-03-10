from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, List, Union
import json


class Settings(BaseSettings):
    """应用配置"""

    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/ai_image_db"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
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
                return [origin.strip() for origin in v.split(',')]
        return v

    # Image Generator Provider (banana, gemini, replicate)
    IMAGE_GENERATOR_PROVIDER: str = "gemini"

    # Gemini API (primary provider)
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash-exp"  # 支持 gemini-2.5-flash-image 等

    # Banana.dev API
    BANANA_API_KEY: Optional[str] = None
    BANANA_MODEL_KEY: str = "stable-diffusion-v1-5"

    # Replicate API
    REPLICATE_API_KEY: Optional[str] = None

    # Image storage
    IMAGE_STORAGE_PATH: str = "./generated_images"

    # App
    APP_NAME: str = "AI Image Generator"
    DEBUG: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None

    # Default admin (disabled by default for security)
    CREATE_DEFAULT_ADMIN: bool = False
    DEFAULT_ADMIN_USERNAME: Optional[str] = None
    DEFAULT_ADMIN_PASSWORD: Optional[str] = None
    DEFAULT_ADMIN_EMAIL: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
