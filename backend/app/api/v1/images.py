from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid

from app.db.database import get_db
from app.models.user import User
from app.models.image import Image
from app.schemas.image import (
    ImageGenerateRequest,
    ImageResponse,
    ImageListResponse
)
from app.core.security import decode_token, oauth2_scheme
import google.generativeai as genai

router = APIRouter(prefix="/images", tags=["Images"])

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))


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


@router.post("/generate", response_model=ImageListResponse)
def generate_images(
    request: ImageGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate images using Gemini API"""
    images = []

    # Map aspect ratios to Gemini dimensions
    aspect_ratios = {
        "1:1": (1024, 1024),
        "4:3": (1024, 768),
        "3:4": (768, 1024),
        "3:2": (1024, 683),
        "16:9": (1024, 576),
        "9:16": (576, 1024)
    }

    width, height = aspect_ratios.get(request.aspect_ratio, (1024, 1024))

    # Generate images
    for i in range(request.image_count):
        try:
            # Use Gemini to generate image description/code
            model = genai.GenerativeModel('gemini-pro-vision')

            # For now, we'll create a placeholder response
            # In production, you would integrate with an image generation API
            response = model.generate_content(
                f"Generate an image description for: {request.prompt}"
            )

            # Create image record (placeholder URL for now)
            new_image = Image(
                user_id=current_user.id,
                prompt=request.prompt,
                image_url=f"https://placeholder.com/image_{uuid.uuid4().hex[:8]}.png",
                aspect_ratio=request.aspect_ratio,
                is_favorite=False
            )
            db.add(new_image)
            images.append(new_image)

        except Exception as e:
            # Continue even if one generation fails
            print(f"Error generating image: {e}")
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

    # Save file (in production, upload to cloud storage)
    file_ext = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4().hex}.{file_ext}"
    file_path = f"/tmp/{file_name}"

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"url": file_path, "filename": file_name}
