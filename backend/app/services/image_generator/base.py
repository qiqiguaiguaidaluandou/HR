from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class GenerationConfig:
    """图片生成配置"""
    prompt: str
    width: int = 1024
    height: int = 1024
    reference_image: Optional[str] = None
    num_images: int = 1
    model: Optional[str] = None


@dataclass
class GenerationResult:
    """图片生成结果"""
    success: bool
    images: list[str]  # Base64 编码的图片列表
    error: Optional[str] = None


class BaseImageGenerator(ABC):
    """图像生成器抽象基类"""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """返回提供者名称"""
        pass

    @abstractmethod
    async def generate(
        self,
        config: GenerationConfig
    ) -> GenerationResult:
        """
        生成图片

        Args:
            config: 生成配置

        Returns:
            GenerationResult: 包含生成结果的对象
        """
        pass

    async def generate_single(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        reference_image: Optional[str] = None
    ) -> Optional[str]:
        """
        生成单张图片（兼容性方法）

        Args:
            prompt: 图片描述
            width: 图片宽度
            height: 图片高度
            reference_image: 参考图 URL (可选)

        Returns:
            Base64 编码的图片数据，失败返回 None
        """
        config = GenerationConfig(
            prompt=prompt,
            width=width,
            height=height,
            reference_image=reference_image,
            num_images=1
        )
        result = await self.generate(config)
        if result.success and result.images:
            return result.images[0]
        return None

    def validate_config(self, config: GenerationConfig) -> None:
        """验证生成配置"""
        if not config.prompt or not config.prompt.strip():
            raise ValueError("Prompt cannot be empty")

        if config.width <= 0 or config.height <= 0:
            raise ValueError("Width and height must be positive")

        if config.num_images < 1 or config.num_images > 10:
            raise ValueError("Number of images must be between 1 and 10")
