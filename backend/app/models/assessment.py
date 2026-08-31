from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Float, Integer, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lesson_id = Column(String(36), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(Float, default=0.0)  # Percentage 0-100
    total_questions = Column(Integer, default=5)
    correct_count = Column(Integer, default=0)
    strong_concepts = Column(JSON, default=list)
    weak_concepts = Column(JSON, default=list)
    misconceptions_summary = Column(JSON, default=list)
    recommendations = Column(JSON, default=list)
    questions_data = Column(JSON, default=list)
    student_responses = Column(JSON, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    lesson = relationship("Lesson", back_populates="assessments")
    user = relationship("User", back_populates="assessments")
