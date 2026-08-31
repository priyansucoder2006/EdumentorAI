from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class AssessmentGenerateRequest(BaseModel):
    lesson_id: str


class AssessmentQuestionItem(BaseModel):
    id: str
    concept: str
    difficulty: str = "beginner"  # "beginner", "intermediate", "advanced"
    type: str = "mcq"  # "mcq", "short_answer", "application"
    prompt: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str


class AssessmentStudentAnswer(BaseModel):
    question_id: str
    answer: str


class AssessmentSubmitRequest(BaseModel):
    answers: List[AssessmentStudentAnswer]


class AssessmentLLMOutput(BaseModel):
    title: str
    questions: List[AssessmentQuestionItem]


class AssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    lesson_id: str
    user_id: str
    score: float
    total_questions: int
    correct_count: int
    strong_concepts: List[str] = []
    weak_concepts: List[str] = []
    misconceptions_summary: List[str] = []
    recommendations: List[Dict[str, Any]] = []
    questions_data: List[Dict[str, Any]] = []
    student_responses: List[Dict[str, Any]] = []
    created_at: datetime
