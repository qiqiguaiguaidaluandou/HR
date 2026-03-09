from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# Image schemas
class ImageBase(BaseModel):
    prompt: str
    aspect_ratio: str = "1:1"


class ImageCreate(ImageBase):
    image_count: int = 1


class ImageGenerateRequest(BaseModel):
    prompt: str
    aspect_ratio: str = "1:1"
    image_count: int = 1
    reference_image: Optional[str] = None


class ImageResponse(BaseModel):
    id: int
    user_id: int
    prompt: str
    image_url: Optional[str]
    aspect_ratio: str
    is_favorite: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ImageListResponse(BaseModel):
    images: list[ImageResponse]
    total: int
