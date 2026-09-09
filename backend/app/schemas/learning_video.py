from typing import Optional, List
from pydantic import BaseModel, Field


class LearningVideoRequest(BaseModel):
    topic: str = Field(..., description="Educational subject or topic to search for")
    target_duration_minutes: Optional[float] = Field(
        default=None,
        alias="targetDurationMinutes",
        description="Target duration in minutes (e.g. 20, 30, 60, 90)"
    )
    duration_preference: Optional[str] = Field(
        default="around",
        alias="durationPreference",
        description="Duration preference mode: 'exact', 'around', 'under', 'minimum', 'short', 'detailed'"
    )
    learner_level: Optional[str] = Field(
        default="beginner",
        alias="learnerLevel",
        description="Learner knowledge level: 'beginner', 'intermediate', 'advanced'"
    )

    model_config = {
        "populate_by_name": True
    }


class VideoMetadata(BaseModel):
    video_id: str
    title: str
    channel: str
    description: str = ""
    thumbnail: str = ""
    duration: str  # Formatted duration e.g. "21:14" or "1:05:30"
    duration_minutes: float  # Exact duration in fractional minutes e.g. 21.23
    duration_seconds: int
    view_count: Optional[int] = 0
    like_count: Optional[int] = 0
    published_at: Optional[str] = None
    embeddable: bool = True
    url: str
    reason: Optional[str] = None
    score: Optional[float] = None


class LearningVideoResponse(BaseModel):
    found: bool
    title: Optional[str] = None
    channel: Optional[str] = None
    video_id: Optional[str] = None
    url: Optional[str] = None
    duration: Optional[str] = None
    duration_minutes: Optional[float] = None
    thumbnail: Optional[str] = None
    reason: Optional[str] = None
    video: Optional[VideoMetadata] = None
