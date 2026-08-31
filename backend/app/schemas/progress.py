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
    description: str
    difficulty: str
    status: str  # "locked", "in_progress", "completed"
    prerequisites: List[str] = []
    concepts: List[str] = []


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
