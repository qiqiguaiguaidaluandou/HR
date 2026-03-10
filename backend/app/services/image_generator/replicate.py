import httpx
import os
from typing import Optional

from app.config import settings
from app.core.logs import get_logger
from .base import BaseImageGenerator, GenerationConfig, GenerationResult

logger = get_logger(__name__)


class ReplicateImageGenerator(BaseImageGenerator):
    """Replicate 图像生成器

    支持多种模型，如:
    - Stability AI Stable Diffusion
    - Playground v2
    - DALL-E 3 (通过 Replicate)
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.REPLICATE_API_KEY

    @property
    def provider_name(self) -> str:
        return "replicate"

    async def generate(
        self,
        config: GenerationConfig
    ) -> GenerationResult:
        """使用 Replicate 生成图片"""
        if not self.api_key:
            logger.error("Replicate API key not configured")
            return GenerationResult(
                success=False,
                images=[],
                error="Replicate API key not configured"
            )

        try:
            self.validate_config(config)

            # Replicate 需要两步：
            # 1. 创建预测 (prediction)
            # 2. 轮询获取结果

            async with httpx.AsyncClient() as client:
                # 启动预测
                headers = {
                    "Authorization": f"Token {self.api_key}",
                    "Content-Type": "application/json"
                }

                # 使用默认的 Stable Diffusion 模型
                model_version = "stability-ai/stable-diffusion-3.5-medium"

                create_response = await client.post(
                    "https://api.replicate.com/v1/predictions",
                    headers=headers,
                    json={
                        "version": model_version,
                        "input": {
                            "prompt": config.prompt,
                            "width": config.width,
                            "height": config.height,
                            "num_outputs": config.num_images
                        }
                    },
                    timeout=30.0
                )

                if create_response.status_code != 201:
                    error_msg = f"Replicate API error: {create_response.status_code} - {create_response.text}"
                    logger.error(error_msg)
                    return GenerationResult(
                        success=False,
                        images=[],
                        error=error_msg
                    )

                prediction = create_response.json()
                prediction_url = prediction["urls"]["get"]

                # 轮询获取结果
                max_attempts = 60  # 最多等待 60 次 (约 60 秒)
                for _ in range(max_attempts):
                    await client.sleep(1)

                    status_response = await client.get(
                        prediction_url,
                        headers=headers,
                        timeout=30.0
                    )

                    if status_response.status_code != 200:
                        continue

                    status_data = status_response.json()
                    status = status_data["status"]

                    if status == "succeeded":
                        output = status_data["output"]
                        # 输出可能是单张图片或图片列表
                        if isinstance(output, list):
                            images = output
                        else:
                            images = [output]
                        return GenerationResult(
                            success=True,
                            images=images
                        )
                    elif status == "failed":
                        error_msg = status_data.get("error", "Generation failed")
                        return GenerationResult(
                            success=False,
                            images=[],
                            error=error_msg
                        )

                return GenerationResult(
                    success=False,
                    images=[],
                    error="Generation timeout"
                )

        except Exception as e:
            error_msg = f"Error calling Replicate API: {str(e)}"
            logger.exception(error_msg)
            return GenerationResult(
                success=False,
                images=[],
                error=error_msg
            )
