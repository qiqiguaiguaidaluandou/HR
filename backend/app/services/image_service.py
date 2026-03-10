import asyncio
from typing import Optional
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.image import Image
from app.services.storage import StorageService
from app.services.image_generator.base import BaseImageGenerator, GenerationConfig
from app.core.logs import get_logger
from app.core.exceptions import ImageGenerationError

logger = get_logger(__name__)


@dataclass
class ImageGenerationRequest:
    """图片生成请求"""
    prompt: str
    aspect_ratio: str = "1:1"
    image_count: int = 1
    reference_image: Optional[str] = None


class ImageService:
    """图片业务逻辑服务"""

    # 宽高比映射
    ASPECT_RATIOS = {
        "1:1": (1024, 1024),
        "4:3": (1024, 768),
        "3:4": (768, 1024),
        "3:2": (1024, 683),
        "16:9": (1024, 576),
        "9:16": (576, 1024)
    }

    def __init__(
        self,
        generator: BaseImageGenerator,
        storage: StorageService
    ):
        self.generator = generator
        self.storage = storage

    def _get_dimensions(self, aspect_ratio: str) -> tuple[int, int]:
        """获取宽高尺寸"""
        return self.ASPECT_RATIOS.get(aspect_ratio, (1024, 1024))

    async def generate_images(
        self,
        request: ImageGenerationRequest,
        user: User,
        db: Session
    ) -> list[Image]:
        """
        生成图片

        Args:
            request: 生成请求
            user: 当前用户
            db: 数据库会话

        Returns:
            list[Image]: 生成的图片列表
        """
        width, height = self._get_dimensions(request.aspect_ratio)

        # 构建生成配置
        config = GenerationConfig(
            prompt=request.prompt,
            width=width,
            height=height,
            reference_image=request.reference_image,
            num_images=request.image_count
        )

        # 生成图片
        logger.info(
            f"Generating {request.image_count} images with "
            f"aspect_ratio={request.aspect_ratio}, prompt={request.prompt[:50]}..."
        )

        result = await self.generator.generate(config)

        if not result.success:
            raise ImageGenerationError(
                message=result.error or "Failed to generate images"
            )

        # 保存图片到存储并创建数据库记录
        images = []
        for base64_image in result.images:
            try:
                stored = self.storage.save_base64_image(
                    base64_image,
                    prefix="gen"
                )

                new_image = Image(
                    user_id=user.id,
                    prompt=request.prompt,
                    image_url=stored.url,
                    aspect_ratio=request.aspect_ratio,
                    is_favorite=False
                )
                images.append(new_image)

            except Exception as e:
                logger.error(f"Failed to save generated image: {e}")
                # 继续处理其他图片

        # 批量保存到数据库
        if images:
            db.add_all(images)
            db.commit()

            for img in images:
                db.refresh(img)

        logger.info(f"Successfully generated {len(images)} images")
        return images

    async def generate_single_image(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        reference_image: Optional[str] = None
    ) -> Optional[str]:
        """生成单张图片（不保存到数据库）"""
        width, height = self._get_dimensions(aspect_ratio)

        return await self.generator.generate_single(
            prompt=prompt,
            width=width,
            height=height,
            reference_image=reference_image
        )

    def get_user_images(
        self,
        db: Session,
        user: User,
        skip: int = 0,
        limit: int = 20,
        favorite_only: bool = False
    ) -> tuple[list[Image], int]:
        """
        获取用户的图片列表

        Returns:
            (images, total): 图片列表和总数
        """
        query = db.query(Image).filter(Image.user_id == user.id)

        if favorite_only:
            query = query.filter(Image.is_favorite == True)

        total = query.count()
        images = query.order_by(Image.created_at.desc()).offset(skip).limit(limit).all()

        return images, total

    def toggle_favorite(
        self,
        db: Session,
        user: User,
        image_id: int
    ) -> Image:
        """切换收藏状态"""
        image = db.query(Image).filter(
            Image.id == image_id,
            Image.user_id == user.id
        ).first()

        if not image:
            from app.core.exceptions import NotFoundError
            raise NotFoundError(f"Image {image_id} not found")

        image.is_favorite = not image.is_favorite
        db.commit()
        db.refresh(image)

        return image

    def delete_image(
        self,
        db: Session,
        user: User,
        image_id: int
    ) -> bool:
        """删除图片"""
        image = db.query(Image).filter(
            Image.id == image_id,
            Image.user_id == user.id
        ).first()

        if not image:
            from app.core.exceptions import NotFoundError
            raise NotFoundError(f"Image {image_id} not found")

        # 删除存储的文件
        if image.image_url:
            self.storage.delete_file(image.image_url)

        # 删除数据库记录
        db.delete(image)
        db.commit()

        return True
