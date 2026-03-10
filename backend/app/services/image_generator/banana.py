import httpx
from typing import Optional

from app.config import settings
from app.core.logs import get_logger
from .base import BaseImageGenerator, GenerationConfig, GenerationResult

logger = get_logger(__name__)


class BananaImageGenerator(BaseImageGenerator):
    """Banana.dev Stable Diffusion 图像生成器"""

    def __init__(self, api_key: Optional[str] = None, model_key: Optional[str] = None):
        self.api_key = api_key or settings.BANANA_API_KEY
        self.model_key = model_key or settings.BANANA_MODEL_KEY

    @property
    def provider_name(self) -> str:
        return "banana"

    async def generate(
        self,
        config: GenerationConfig
    ) -> GenerationResult:
        """使用 Banana.dev 生成图片"""
        if not self.api_key or self.api_key == "your-banana-api-key":
            logger.error("Banana API key not configured")
            return GenerationResult(
                success=False,
                images=[],
                error="Banana API key not configured"
            )

        try:
            self.validate_config(config)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.banana.dev/api/v4/inference/stable-diffusion",
                    json={
                        "api_key": self.api_key,
                        "model_key": self.model_key,
                        "prompt": config.prompt,
                        "width": config.width,
                        "height": config.height,
                        "num_inference_steps": 25,
                        "guidance_scale": 7.5
                    },
                    timeout=120.0
                )

                if response.status_code != 200:
                    error_msg = f"Banana API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return GenerationResult(
                        success=False,
                        images=[],
                        error=error_msg
                    )

                result = response.json()

                if result.get("outputs") and len(result["outputs"]) > 0:
                    # 返回多张图片（如果生成了多张）
                    generated_images = result["outputs"][:config.num_images]
                    return GenerationResult(
                        success=True,
                        images=generated_images
                    )

                return GenerationResult(
                    success=False,
                    images=[],
                    error="No images generated"
                )

        except Exception as e:
            error_msg = f"Error calling Banana API: {str(e)}"
            logger.exception(error_msg)
            return GenerationResult(
                success=False,
                images=[],
                error=error_msg
            )
