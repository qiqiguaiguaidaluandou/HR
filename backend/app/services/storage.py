import uuid
import base64
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from app.core.logs import get_logger
from app.core.exceptions import StorageError

logger = get_logger(__name__)


@dataclass
class StoredFile:
    """存储的文件信息"""
    filename: str
    url: str
    path: str


class StorageService:
    """文件存储服务"""

    def __init__(self, storage_path: str = "./generated_images"):
        self.storage_path = Path(storage_path)
        self._ensure_storage_dir()

    def _ensure_storage_dir(self) -> None:
        """确保存储目录存在"""
        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Storage directory: {self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to create storage directory: {e}")
            raise StorageError(f"Failed to create storage directory: {e}")

    def save_base64_image(
        self,
        base64_data: str,
        prefix: str = "img"
    ) -> StoredFile:
        """
        保存 base64 编码的图片

        Args:
            base64_data: base64 编码的图片数据
            prefix: 文件名前缀

        Returns:
            StoredFile: 存储的文件信息
        """
        try:
            filename = f"{prefix}_{uuid.uuid4().hex}.png"
            file_path = self.storage_path / filename

            # 解码并保存
            image_data = base64.b64decode(base64_data)
            with open(file_path, "wb") as f:
                f.write(image_data)

            url = f"/images/{filename}"
            logger.info(f"Saved image: {filename}")

            return StoredFile(
                filename=filename,
                url=url,
                path=str(file_path)
            )

        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            raise StorageError(f"Failed to save image: {e}")

    async def save_uploaded_file(
        self,
        file_content: bytes,
        filename: str,
        prefix: str = "upload"
    ) -> StoredFile:
        """
        保存上传的文件

        Args:
            file_content: 文件内容
            filename: 原始文件名
            prefix: 文件名前缀

        Returns:
            StoredFile: 存储的文件信息
        """
        try:
            # 获取文件扩展名
            ext = filename.split(".")[-1] if "." in filename else "png"

            # 生成新文件名
            new_filename = f"{prefix}_{uuid.uuid4().hex}.{ext}"
            file_path = self.storage_path / new_filename

            # 保存文件
            with open(file_path, "wb") as f:
                f.write(file_content)

            url = f"/images/{new_filename}"
            logger.info(f"Saved uploaded file: {new_filename}")

            return StoredFile(
                filename=new_filename,
                url=url,
                path=str(file_path)
            )

        except Exception as e:
            logger.error(f"Failed to save uploaded file: {e}")
            raise StorageError(f"Failed to save uploaded file: {e}")

    def delete_file(self, url: str) -> bool:
        """
        删除文件

        Args:
            url: 文件 URL (如 /images/xxx.png)

        Returns:
            bool: 是否删除成功
        """
        try:
            if url.startswith("/images/"):
                filename = url.replace("/images/", "")
                file_path = self.storage_path / filename
            else:
                return False

            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file: {filename}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False

    def get_file_path(self, url: str) -> Optional[str]:
        """
        获取文件的完整路径

        Args:
            url: 文件 URL

        Returns:
            文件完整路径，如果不存在返回 None
        """
        if url.startswith("/images/"):
            filename = url.replace("/images/", "")
            file_path = self.storage_path / filename
            if file_path.exists():
                return str(file_path)
        return None

    def file_exists(self, url: str) -> bool:
        """检查文件是否存在"""
        return self.get_file_path(url) is not None
