from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Integer, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(255), nullable=False)
    description = Column(String(512), nullable=True)
    nodes = Column(JSON, default=list)  # List of {id, title, status, prerequisites, concepts, difficulty}
    current_node_id = Column(String(100), nullable=True)
    status = Column(String(50), default="active")  # active, completed, archived
    progress_percentage = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("User", back_populates="learning_paths")
