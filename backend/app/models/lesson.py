from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, Text, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(255), nullable=False)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    language = Column(String(50), default="en")
    difficulty = Column(String(50), default="beginner")  # beginner, intermediate, advanced
    duration_minutes = Column(Integer, default=20)
    objectives = Column(JSON, default=list)
    status = Column(String(50), default="created")  # created, in_progress, completed
    current_step_index = Column(Integer, default=0)
    state = Column(String(50), default="PLAN")  # INTRODUCE, EXPLAIN, DEMONSTRATE, ASK, EVALUATE, RETEACH, ASSESS, etc.
    lesson_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="lessons")
    document = relationship("Document", back_populates="lessons")
    steps = relationship("LessonStep", back_populates="lesson", cascade="all, delete-orphan", order_by="LessonStep.step_number")
    interactions = relationship("Interaction", back_populates="lesson", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="lesson", cascade="all, delete-orphan")
    video_jobs = relationship("VideoJob", back_populates="lesson", cascade="all, delete-orphan")


class LessonStep(Base):
    __tablename__ = "lesson_steps"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    lesson_id = Column(String(36), ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    step_number = Column(Integer, nullable=False)
    concept = Column(String(255), nullable=False)
    explanation = Column(Text, nullable=False)
    example = Column(Text, nullable=True)
    analogy = Column(Text, nullable=True)
    visual_type = Column(String(50), default="none")  # math, code, diagram, graph, simulation, none
    visual_data = Column(JSON, default=dict)
    question = Column(JSON, default=dict)
    expected_answer = Column(Text, nullable=True)
    difficulty = Column(String(50), default="beginner")
    state = Column(String(50), default="pending")  # pending, active, completed, reteach
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    lesson = relationship("Lesson", back_populates="steps")
    interactions = relationship("Interaction", back_populates="step", cascade="all, delete-orphan")
