from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.api.v1 import api_router
from app.db.database import init_db
from app.core.config import settings

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI Image Generator API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static files directory for generated images
os.makedirs(settings.IMAGE_STORAGE_PATH, exist_ok=True)
app.mount("/images", StaticFiles(directory=settings.IMAGE_STORAGE_PATH), name="images")

# Include API router
app.include_router(api_router, prefix="/api/v1")


# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def root():
    return {"message": "Welcome to AI Image Generator API", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
