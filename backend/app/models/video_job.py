from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class VideoJob(Base):
    __tablename__ = "video_jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lesson_id = Column(String(36), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default="queued")  # queued, processing, rendering, completed, failed
    progress = Column(Integer, default=0)  # 0 to 100
    scenes_data = Column(JSON, default=list)  # List of scene definitions with narration, visual, duration
    video_url = Column(String(512), nullable=True)
    error_message = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    lesson = relationship("Lesson", back_populates="video_jobs")
