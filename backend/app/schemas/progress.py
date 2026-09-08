from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class ConceptMasteryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    topic: str
    concept: str
    mastery_score: float
    attempts: int
    correct_attempts: int
    difficulty_level: str
    last_studied: datetime


class MasteryOverviewResponse(BaseModel):
    overall_mastery: float
    total_topics_studied: int
    total_concepts_learned: int
    strong_topics: List[str]
    weak_topics: List[str]
    concept_details: List[ConceptMasteryItem]


class RecommendationItem(BaseModel):
    type: str  # "revision", "next_topic", "practice_problem", "prerequisite"
    topic: str
    concept: Optional[str] = None
    reason: str
    suggested_difficulty: str
    estimated_minutes: int


class LearningPathNode(BaseModel):
    id: str
    title: str
    phase_name: Optional[str] = None  # e.g. "Month 1 (Weeks 1-4): Python & Math Foundations"
    time_commitment: Optional[str] = None  # e.g. "10 hrs/week • 40 hours total"
    description: str
    difficulty: str  # "beginner", "intermediate", "advanced"
    status: str  # "locked", "in_progress", "completed"
    progress: int = 0
    concepts: List[str] = []
    practical_project: Optional[str] = None
    tools_and_resources: List[str] = []
    prerequisites: List[str] = []


class RoadmapGenerateRequest(BaseModel):
    topic: str
    duration_months: Optional[int] = 6
    duration_label: Optional[str] = "6 Months"
    hours_per_week: Optional[int] = 10
    current_level: Optional[str] = "beginner"  # "beginner", "intermediate", "advanced"
    learning_goal: Optional[str] = "career"  # "career", "exam", "projects", "mastery"
    target_role: Optional[str] = None


class NodeStatusUpdateRequest(BaseModel):
    status: str  # "completed", "in_progress", "locked"
    progress: Optional[int] = None


class LearningPathResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    topic: str
    description: Optional[str] = None
    nodes: List[Dict[str, Any]]
    current_node_id: Optional[str] = None
    status: str
    progress_percentage: int
    created_at: datetime
