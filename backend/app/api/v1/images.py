from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
import base64
import httpx

from app.db.database import get_db
from app.models.user import User
from app.models.image import Image
from app.schemas.image import (
    ImageGenerateRequest,
    ImageResponse,
    ImageListResponse
)
from app.core.security import decode_token, oauth2_scheme
from app.core.config import settings

router = APIRouter(prefix="/images", tags=["Images"])


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


def save_base64_image(base64_data: str, filename: str) -> str:
    """Save base64 encoded image to storage and return the URL"""
    # Create storage directory if not exists
    storage_path = settings.IMAGE_STORAGE_PATH
    os.makedirs(storage_path, exist_ok=True)

    # Save file
    file_path = os.path.join(storage_path, filename)
    image_data = base64.b64decode(base64_data)
    with open(file_path, "wb") as f:
        f.write(image_data)

    # Return URL (in production, use cloud storage or static file server)
    return f"/images/{filename}"


async def generate_image_with_banana(prompt: str, width: int = 1024, height: int = 1024) -> Optional[str]:
    """Generate image using Banana.dev API"""
    if not settings.BANANA_API_KEY or settings.BANANA_API_KEY == "your-banana-api-key":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banana API key not configured"
        )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.banana.dev/api/v4/inference/stable-diffusion",
                json={
                    "api_key": settings.BANANA_API_KEY,
                    "model_key": settings.BANANA_MODEL_KEY,
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                    "num_inference_steps": 25,
                    "guidance_scale": 7.5
                },
                timeout=120.0
            )

            if response.status_code != 200:
                print(f"Banana API error: {response.status_code} - {response.text}")
                return None

            result = response.json()

            # Banana API returns base64 encoded image
            if result.get("outputs") and len(result["outputs"]) > 0:
                return result["outputs"][0]  # Base64 image data

            return None

        except Exception as e:
            print(f"Error calling Banana API: {e}")
            return None


@router.post("/generate", response_model=ImageListResponse)
async def generate_images(
    request: ImageGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate images using Banana.dev Stable Diffusion API"""
    images = []

    # Map aspect ratios to dimensions
    aspect_ratios = {
        "1:1": (512, 512),
        "4:3": (512, 384),
        "3:4": (384, 512),
        "3:2": (512, 341),
        "16:9": (512, 288),
        "9:16": (288, 512)
    }

    width, height = aspect_ratios.get(request.aspect_ratio, (512, 512))

    # Generate images
    for i in range(request.image_count):
        try:
            # Call Banana API to generate image
            base64_image = await generate_image_with_banana(
                prompt=request.prompt,
                width=width,
                height=height
            )

            if base64_image:
                # Save image to storage
                filename = f"{uuid.uuid4().hex}.png"
                image_url = save_base64_image(base64_image, filename)

                # Create image record
                new_image = Image(
                    user_id=current_user.id,
                    prompt=request.prompt,
                    image_url=image_url,
                    aspect_ratio=request.aspect_ratio,
                    is_favorite=False
                )
                db.add(new_image)
                images.append(new_image)
            else:
                # Create placeholder if generation fails
                new_image = Image(
                    user_id=current_user.id,
                    prompt=request.prompt,
                    image_url=f"https://placeholder.com/{width}x{height}?text=Generation+Failed",
                    aspect_ratio=request.aspect_ratio,
                    is_favorite=False
                )
                db.add(new_image)
                images.append(new_image)

        except Exception as e:
            print(f"Error generating image {i+1}: {e}")
            continue

    db.commit()

    # Refresh images
    for img in images:
        db.refresh(img)

    return {"images": images, "total": len(images)}


@router.get("", response_model=ImageListResponse)
def get_images(
    skip: int = 0,
    limit: int = 20,
    favorite_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's images"""
    query = db.query(Image).filter(Image.user_id == current_user.id)

    if favorite_only:
        query = query.filter(Image.is_favorite == True)

    total = query.count()
    images = query.order_by(Image.created_at.desc()).offset(skip).limit(limit).all()

    return {"images": images, "total": total}


@router.post("/{image_id}/favorite", response_model=ImageResponse)
def toggle_favorite(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle image favorite status"""
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.user_id == current_user.id
    ).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    image.is_favorite = not image.is_favorite
    db.commit()
    db.refresh(image)
    return image


@router.delete("/{image_id}")
def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an image"""
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.user_id == current_user.id
    ).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    # Delete local file if exists
    if image.image_url and image.image_url.startswith("/images/"):
        filename = image.image_url.replace("/images/", "")
        file_path = os.path.join(settings.IMAGE_STORAGE_PATH, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.delete(image)
    db.commit()
    return {"message": "Image deleted successfully"}


@router.post("/upload")
async def upload_reference_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a reference image"""
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )

    # Save file to storage
    storage_path = settings.IMAGE_STORAGE_PATH
    os.makedirs(storage_path, exist_ok=True)

    file_ext = file.filename.split(".")[-1] if file.filename else "png"
    file_name = f"ref_{uuid.uuid4().hex}.{file_ext}"
    file_path = os.path.join(storage_path, file_name)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"url": f"/images/{file_name}", "filename": file_name}
