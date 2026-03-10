from typing import Optional

from app.config import settings
from app.core.logs import get_logger
from .base import BaseImageGenerator
from .gemini import GeminiImageGenerator
from .banana import BananaImageGenerator
from .replicate import ReplicateImageGenerator

logger = get_logger(__name__)


class ImageGeneratorFactory:
    """图片生成器工厂"""

    _generators = {
        "gemini": GeminiImageGenerator,
        "banana": BananaImageGenerator,
        "replicate": ReplicateImageGenerator,
    }

    @classmethod
    def create_generator(
        cls,
        provider: Optional[str] = None
    ) -> BaseImageGenerator:
        """
        根据配置创建图片生成器

        Args:
            provider: 提供者名称 (gemini, banana, replicate)

        Returns:
            BaseImageGenerator 实例
        """
        provider = (provider or settings.IMAGE_GENERATOR_PROVIDER).lower()

        generator_class = cls._generators.get(provider)

        if generator_class is None:
            logger.warning(
                f"Unknown provider '{provider}', "
                f"available: {list(cls._generators.keys())}. "
                f"Using default (gemini)."
            )
            generator_class = GeminiImageGenerator

        logger.info(f"Creating image generator: {generator_class.__name__}")
        return generator_class()

    @classmethod
    def register_generator(
        cls,
        name: str,
        generator_class: type[BaseImageGenerator]
    ) -> None:
        """注册新的图片生成器"""
        cls._generators[name.lower()] = generator_class

    @classmethod
    def get_available_providers(cls) -> list[str]:
        """获取可用的提供者列表"""
        return list(cls._generators.keys())
