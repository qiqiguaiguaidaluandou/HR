from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.db.database import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    aspect_ratio = Column(String(10), default="1:1")
    is_favorite = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    owner = relationship("User", back_populates="images")

    # Composite index for common queries
    __table_args__ = (
        Index('ix_images_user_created', 'user_id', 'created_at'),
        Index('ix_images_user_favorite', 'user_id', 'is_favorite'),
    )
