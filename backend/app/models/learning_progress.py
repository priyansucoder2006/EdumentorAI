from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Float, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class LearningProgress(Base):
    __tablename__ = "learning_progress"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(255), nullable=False, index=True)
    concept = Column(String(255), nullable=False, index=True)
    mastery_score = Column(Float, default=0.0)  # 0.0 to 100.0
    attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    difficulty_level = Column(String(50), default="beginner")
    last_studied = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="progress")
