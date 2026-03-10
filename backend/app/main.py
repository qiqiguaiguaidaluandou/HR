from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os

from app.api.v1 import api_router
from app.db.database import init_db
from app.config import settings
from app.core.logs import setup_logging, get_logger
from app.core.exceptions import AppException

# 配置日志
setup_logging(
    level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE
)
logger = get_logger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    description="AI Image Generator API",
    version="1.0.0",
    debug=settings.DEBUG
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 统一异常处理
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


# 创建静态文件目录
os.makedirs(settings.IMAGE_STORAGE_PATH, exist_ok=True)
app.mount("/images", StaticFiles(directory=settings.IMAGE_STORAGE_PATH), name="images")

# 包含 API 路由
app.include_router(api_router, prefix="/api/v1")


# 应用启动事件
@app.on_event("startup")
def startup_event():
    logger.info(f"Starting {settings.APP_NAME}")
    init_db()
    logger.info("Database initialized")


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
