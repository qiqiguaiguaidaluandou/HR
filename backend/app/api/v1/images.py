from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
import os

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
from app.core.exceptions import AppException
from app.services.image_service import ImageService, ImageGenerationRequest
from app.container import get_storage_service, get_image_service

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


@router.post("/generate", response_model=ImageListResponse)
async def generate_images(
    request: ImageGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    image_service: ImageService = Depends(get_image_service)
):
    """生成图片"""
    try:
        # 构建请求
        gen_request = ImageGenerationRequest(
            prompt=request.prompt,
            aspect_ratio=request.aspect_ratio,
            image_count=request.image_count,
            reference_image=request.reference_image
        )

        # 生成图片
        images = await image_service.generate_images(
            request=gen_request,
            user=current_user,
            db=db
        )

        return {
            "images": images,
            "total": len(images),
            "page": 1,
            "page_size": request.image_count,
            "total_pages": 1
        }

    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate images: {str(e)}"
        )


@router.get("", response_model=ImageListResponse)
def get_images(
    skip: int = 0,
    limit: int = 20,
    favorite_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    image_service: ImageService = Depends(get_image_service)
):
    """获取用户的图片列表"""
    images, total = image_service.get_user_images(
        db=db,
        user=current_user,
        skip=skip,
        limit=limit,
        favorite_only=favorite_only
    )

    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1

    return {
        "images": images,
        "total": total,
        "page": page,
        "page_size": limit,
        "total_pages": total_pages
    }


@router.post("/{image_id}/favorite", response_model=ImageResponse)
def toggle_favorite(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    image_service: ImageService = Depends(get_image_service)
):
    """切换图片收藏状态"""
    try:
        image = image_service.toggle_favorite(
            db=db,
            user=current_user,
            image_id=image_id
        )
        return image
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )


@router.delete("/{image_id}")
def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    image_service: ImageService = Depends(get_image_service)
):
    """删除图片"""
    try:
        image_service.delete_image(
            db=db,
            user=current_user,
            image_id=image_id
        )
        return {"message": "Image deleted successfully"}
    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )


@router.post("/upload")
async def upload_reference_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    storage_service=Depends(get_storage_service)
):
    """上传参考图片"""
    # 验证文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )

    try:
        # 读取文件内容
        content = await file.read()

        # 保存文件
        stored = await storage_service.save_uploaded_file(
            file_content=content,
            filename=file.filename or "reference.png",
            prefix="ref"
        )

        return {"url": stored.url, "filename": stored.filename}

    except AppException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.get("/{image_id}/download")
def download_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """下载图片"""
    image = db.query(Image).filter(
        Image.id == image_id,
        Image.user_id == current_user.id
    ).first()

    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )

    if not image.image_url or not image.image_url.startswith("/images/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file not available for download"
        )

    storage = get_storage_service()
    file_path = storage.get_file_path(image.image_url)

    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found"
        )

    return FileResponse(
        file_path,
        media_type="image/png",
        filename=f"ai-image-{image_id}.png"
    )
