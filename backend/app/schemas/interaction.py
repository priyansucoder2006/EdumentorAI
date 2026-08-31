from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class AnswerEvaluationResult(BaseModel):
    is_correct: bool
    score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(1.0, ge=0.0, le=1.0)
    feedback: str
    missing_concepts: List[str] = []
    reasoning_quality: str = "good"  # "poor", "partial", "good", "excellent"


class MisconceptionResult(BaseModel):
    detected: bool
    root_cause: Optional[str] = None
    misconception_title: Optional[str] = None
    severity: str = "none"  # "none", "low", "medium", "high"
    pedagogical_analogy: Optional[str] = None
    recommended_reteach_strategy: Optional[str] = None


class AdaptiveDecisionOutput(BaseModel):
    action: str  # "continue", "reteach", "provide_analogy", "simplify", "ask_easier_question", "increase_difficulty"
    rationale: str
    next_question: Optional[Dict[str, Any]] = None
    remedial_explanation: Optional[str] = None
    visual_override: Optional[Dict[str, Any]] = None
    new_mastery_estimate: float


class AnswerSubmitRequest(BaseModel):
    step_id: str
    student_answer: str
    response_mode: str = "text"  # "text", "voice", "option_select"


class InteractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    lesson_id: str
    step_id: Optional[str] = None
    question: str
    student_answer: str
    evaluation: AnswerEvaluationResult
    misconception: MisconceptionResult
    adaptive_decision: AdaptiveDecisionOutput
    confidence: float
    current_mastery: float
    created_at: datetime
