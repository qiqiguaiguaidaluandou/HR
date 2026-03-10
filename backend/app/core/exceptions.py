from typing import Optional


class AppException(Exception):
    """基础异常类"""

    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        status_code: int = 500,
        details: Optional[dict] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self):
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details
        }


class ImageGenerationError(AppException):
    """图片生成异常"""

    def __init__(self, message: str = "Image generation failed", details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="IMAGE_GENERATION_ERROR",
            status_code=500,
            details=details
        )


class StorageError(AppException):
    """存储异常"""

    def __init__(self, message: str = "Storage operation failed", details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="STORAGE_ERROR",
            status_code=500,
            details=details
        )


class AuthenticationError(AppException):
    """认证异常"""

    def __init__(self, message: str = "Authentication failed", details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class NotFoundError(AppException):
    """资源不存在异常"""

    def __init__(self, message: str = "Resource not found", details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details=details
        )


class ValidationError(AppException):
    """验证异常"""

    def __init__(self, message: str = "Validation failed", details: Optional[dict] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )
