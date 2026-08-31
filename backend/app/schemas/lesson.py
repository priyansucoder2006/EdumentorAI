from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class QuestionSchema(BaseModel):
    id: str = "q1"
    type: str = "mcq"  # "mcq", "conceptual", "numerical", "code", "short_answer"
    prompt: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation_guide: Optional[str] = None
    hint: Optional[str] = None
    difficulty: str = "beginner"


class LessonStepLLMOutput(BaseModel):
    step_number: int
    concept: str
    explanation: str
    example: Optional[str] = None
    analogy: Optional[str] = None
    visual_type: str = "none"
    visual_data: Dict[str, Any] = {}
    question: QuestionSchema
    expected_answer: str
    difficulty: str = "beginner"


class LessonPlanLLMOutput(BaseModel):
    topic: str
    duration_minutes: int
    language: str
    difficulty: str
    objectives: List[str]
    prerequisites: List[str] = []
    summary: str
    steps: List[LessonStepLLMOutput]


class LessonCreate(BaseModel):
    topic: str = Field(..., min_length=2, max_length=255)
    document_id: Optional[str] = None
    language: str = "en"  # "en", "hi", "hinglish", "bn"
    difficulty: str = "beginner"  # "beginner", "intermediate", "advanced"
    duration_minutes: int = 20  # 5, 20, 60, 10080 (7 days)
    learning_goal: Optional[str] = "mastery"
    target_audience: Optional[str] = None  # e.g. "Class 8 student", "Technical interview"


class LessonStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    lesson_id: str
    step_number: int
    concept: str
    explanation: str
    example: Optional[str] = None
    analogy: Optional[str] = None
    visual_type: str
    visual_data: Dict[str, Any] = {}
    question: Dict[str, Any] = {}
    expected_answer: Optional[str] = None
    difficulty: str
    state: str
    created_at: datetime


class LessonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    topic: str
    document_id: Optional[str] = None
    language: str
    difficulty: str
    duration_minutes: int
    objectives: List[str] = []
    status: str
    current_step_index: int
    state: str
    lesson_metadata: Dict[str, Any] = {}
    steps: List[LessonStepResponse] = []
    created_at: datetime
    updated_at: datetime


class LessonLanguageSwitch(BaseModel):
    target_language: str  # "en", "hi", "hinglish", "bn"


class LessonStateTransitionRequest(BaseModel):
    action: str  # "next_step", "prev_step", "start", "complete", "switch_language"
    target_language: Optional[str] = None
