from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class LearnerProfileBase(BaseModel):
    knowledge_level: str = Field("beginner", description="beginner, intermediate, advanced")
    learning_goal: str = Field("mastery", description="e.g. interview_prep, school_exam, general_mastery")
    preferred_depth: str = Field("balanced", description="intuitive, balanced, rigorous")
    available_time: int = Field(20, description="Session time in minutes: 5, 20, 60, etc.")
    learning_style: str = Field("visual", description="visual, practical, conceptual")
    preferred_language: str = Field("en", description="en, hi, hinglish, bn")
    strong_topics: List[str] = []
    weak_topics: List[str] = []


class LearnerProfileCreate(LearnerProfileBase):
    pass


class LearnerProfileUpdate(BaseModel):
    knowledge_level: Optional[str] = None
    learning_goal: Optional[str] = None
    preferred_depth: Optional[str] = None
    available_time: Optional[int] = None
    learning_style: Optional[str] = None
    preferred_language: Optional[str] = None
    strong_topics: Optional[List[str]] = None
    weak_topics: Optional[List[str]] = None


class LearnerProfileResponse(LearnerProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    current_learning_path_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
