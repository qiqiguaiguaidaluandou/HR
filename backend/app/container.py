from typing import Optional
from functools import lru_cache

from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import SessionLocal
from app.services.image_generator.factory import ImageGeneratorFactory
from app.services.storage import StorageService
from app.services.image_service import ImageService


class Container:
    """依赖注入容器"""

    _instance: Optional['Container'] = None
    _storage_service: Optional[StorageService] = None
    _image_service: Optional[ImageService] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_db(self) -> Session:
        """获取数据库会话"""
        return SessionLocal()

    @property
    def storage_service(self) -> StorageService:
        """获取存储服务单例"""
        if self._storage_service is None:
            self._storage_service = StorageService(
                storage_path=settings.IMAGE_STORAGE_PATH
            )
        return self._storage_service

    @property
    def image_generator(self):
        """获取图片生成器"""
        return ImageGeneratorFactory.create_generator(
            provider=settings.IMAGE_GENERATOR_PROVIDER
        )

    @property
    def image_service(self) -> ImageService:
        """获取图片服务单例"""
        if self._image_service is None:
            self._image_service = ImageService(
                generator=self.image_generator,
                storage=self.storage_service
            )
        return self._image_service


# 全局容器实例
container = Container()


def get_db() -> Session:
    """FastAPI 依赖注入函数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_storage_service() -> StorageService:
    """获取存储服务"""
    return container.storage_service


def get_image_service() -> ImageService:
    """获取图片服务"""
    return container.image_service


def get_image_generator():
    """获取图片生成器"""
    return container.image_generator
