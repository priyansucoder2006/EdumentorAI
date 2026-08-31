from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Float, Text, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lesson_id = Column(String(36), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    step_id = Column(String(36), ForeignKey("lesson_steps.id", ondelete="CASCADE"), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    student_answer = Column(Text, nullable=False)
    evaluation = Column(JSON, default=dict)  # is_correct, score, feedback, missing_concepts
    misconception = Column(JSON, default=dict)  # detected, root_cause, analogy, severity
    adaptive_decision = Column(String(100), default="continue")  # continue, reteach, simplify, increase_difficulty
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    lesson = relationship("Lesson", back_populates="interactions")
    step = relationship("LessonStep", back_populates="interactions")
    user = relationship("User", back_populates="interactions")
