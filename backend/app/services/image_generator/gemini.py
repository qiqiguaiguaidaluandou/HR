import httpx
import base64
import json
from typing import Optional

from app.config import settings
from app.core.logs import get_logger
from .base import BaseImageGenerator, GenerationConfig, GenerationResult

logger = get_logger(__name__)


class GeminiImageGenerator(BaseImageGenerator):
    """Google Gemini 图像生成器

    支持以下模型:
    - gemini-2.0-flash-exp (实验版)
    - gemini-2.5-flash-preview-05-20
    - imagen-3.0-generate-002
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def generate(
        self,
        config: GenerationConfig
    ) -> GenerationResult:
        """使用 Gemini 生成图片"""
        if not self.api_key:
            logger.error("Gemini API key not configured")
            return GenerationResult(
                success=False,
                images=[],
                error="Gemini API key not configured"
            )

        try:
            self.validate_config(config)

            # 构建请求
            headers = {
                "Content-Type": "application/json"
            }

            # 准备文本和可选的参考图
            contents = []

            # 如果有参考图，添加图片
            if config.reference_image:
                # 检查是否是 base64 数据 URL 还是 URL
                if config.reference_image.startswith("data:image") or config.reference_image.startswith("http"):
                    image_data = await self._load_image_as_base64(config.reference_image)
                    if image_data:
                        contents.append({
                            "role": "user",
                            "parts": [
                                {
                                    "inlineData": {
                                        "mime_type": "image/jpeg",
                                        "data": image_data
                                    }
                                },
                                {"text": config.prompt}
                            ]
                        })

            # 如果没有参考图，只发送文本
            if not contents:
                contents.append({
                    "role": "user",
                    "parts": [{"text": config.prompt}]
                })

            # 构建请求体
            request_body = {
                "contents": contents,
                "generationConfig": {
                    "responseModalities": ["image"],
                    "responseMimeType": "image/png"
                }
            }

            async with httpx.AsyncClient() as client:
                url = f"{self.base_url}/models/{self.model}:generateContent"
                params = {"key": self.api_key}

                logger.info(f"Calling Gemini API: model={self.model}, prompt={config.prompt[:50]}...")

                response = await client.post(
                    url,
                    headers=headers,
                    json=request_body,
                    params=params,
                    timeout=120.0
                )

                if response.status_code != 200:
                    error_msg = f"Gemini API error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    return GenerationResult(
                        success=False,
                        images=[],
                        error=error_msg
                    )

                result = response.json()

                # 解析响应
                images = self._parse_response(result)

                if not images:
                    logger.warning("No images generated from Gemini API")
                    return GenerationResult(
                        success=False,
                        images=[],
                        error="No images generated"
                    )

                return GenerationResult(
                    success=True,
                    images=images
                )

        except Exception as e:
            error_msg = f"Error generating image: {str(e)}"
            logger.exception(error_msg)
            return GenerationResult(
                success=False,
                images=[],
                error=error_msg
            )

    async def _load_image_as_base64(self, image_source: str) -> Optional[str]:
        """加载图片并转换为 base64"""
        try:
            # 如果已经是 data URL，提取 base64 部分
            if image_source.startswith("data:image"):
                return image_source.split(",", 1)[1]

            # 如果是 URL，下载图片
            async with httpx.AsyncClient() as client:
                response = await client.get(image_source, timeout=30.0)
                if response.status_code == 200:
                    return base64.b64encode(response.content).decode("utf-8")

            return None
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            return None

    def _parse_response(self, result: dict) -> list[str]:
        """解析 Gemini API 响应"""
        images = []

        try:
            candidates = result.get("candidates", [])
            if not candidates:
                return images

            content = candidates[0].get("content", {})
            parts = content.get("parts", [])

            for part in parts:
                if "inlineData" in part:
                    inline_data = part["inlineData"]
                    data = inline_data.get("data")
                    if data:
                        images.append(data)

        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")

        return images
