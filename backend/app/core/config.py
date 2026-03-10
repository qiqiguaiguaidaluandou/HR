# 向后兼容 - 重新导出新配置
# 所有新代码应该直接使用 app.config
from app.config import settings, Settings

__all__ = ["settings", "Settings"]
