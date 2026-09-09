from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.learning_video import LearningVideoRequest, LearningVideoResponse
from app.services.youtube_service import YouTubeService
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/video", response_model=LearningVideoResponse)
async def find_learning_video_endpoint(
    req: LearningVideoRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Duration-aware YouTube learning video search and ranking.
    Returns exactly ONE best verified video for deeper educational study.
    """
    service = YouTubeService()
    result = await service.find_learning_video(
        topic=req.topic,
        target_duration_minutes=req.target_duration_minutes,
        duration_preference=req.duration_preference,
        learner_level=req.learner_level
    )
    return result
