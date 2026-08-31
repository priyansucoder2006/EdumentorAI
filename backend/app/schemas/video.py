from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class ScenePlanSchema(BaseModel):
    scene_number: int
    purpose: str  # "intro", "explanation", "demonstration", "question", "summary"
    narration: str
    visual_type: str  # "diagram", "math", "code", "graph", "text_card"
    visual_data: Dict[str, Any] = {}
    avatar_required: bool = True
    duration_seconds: int = 15


class VideoGenerateRequest(BaseModel):
    lesson_id: str
    include_subtitles: bool = True
    voice_style: str = "friendly_teacher"


class VideoJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    lesson_id: str
    status: str  # "queued", "processing", "rendering", "completed", "failed"
    progress: int
    scenes_data: List[Dict[str, Any]] = []
    video_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
