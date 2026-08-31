from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    knowledge_level = Column(String(50), default="beginner")  # beginner, intermediate, advanced
    learning_goal = Column(String(255), default="mastery")
    preferred_depth = Column(String(50), default="balanced")  # intuitive, balanced, rigorous
    available_time = Column(Integer, default=20)  # default minutes (e.g. 5, 20, 60, 10080)
    learning_style = Column(String(50), default="visual")  # visual, practical, conceptual
    strong_topics = Column(JSON, default=list)
    weak_topics = Column(JSON, default=list)
    current_learning_path_id = Column(String(36), nullable=True)
    preferred_language = Column(String(50), default="en")  # en, hi, hinglish, bn
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="profile")
