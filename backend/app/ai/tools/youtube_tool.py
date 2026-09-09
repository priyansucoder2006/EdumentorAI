from typing import Optional, Dict, Any
from app.services.youtube_service import YouTubeService
from app.core.logging import logger


async def find_learning_video(
    topic: str,
    target_duration_minutes: Optional[float] = None,
    duration_preference: Optional[str] = "around",
    learner_level: Optional[str] = "beginner"
) -> Dict[str, Any]:
    """
    Searches YouTube via YouTube Data API v3 and recommends exactly ONE best video
    matching the learner's topic and duration constraints.

    Parameters:
        topic: The educational topic (e.g. 'recursion', 'React hooks', 'Docker')
        target_duration_minutes: Target duration in minutes (e.g. 20, 30, 60, 90)
        duration_preference: Duration mode: 'exact', 'around', 'under', 'minimum' (>= target), 'short', 'detailed'
        learner_level: Learner proficiency: 'beginner', 'intermediate', 'advanced'

    Returns:
        Structured result with verified video title, channel, duration, thumbnail, URL, and reason.
    """
    service = YouTubeService()
    result = await service.find_learning_video(
        topic=topic,
        target_duration_minutes=target_duration_minutes,
        duration_preference=duration_preference,
        learner_level=learner_level
    )

    if result.found and result.video:
        return {
            "found": True,
            "title": result.video.title,
            "channel": result.video.channel,
            "video_id": result.video.video_id,
            "url": result.video.url,
            "duration": result.video.duration,
            "duration_minutes": result.video.duration_minutes,
            "thumbnail": result.video.thumbnail,
            "reason": result.video.reason or "Best match for the requested topic and duration."
        }
    else:
        return {
            "found": False,
            "reason": result.reason or "No suitable video was found for the requested topic and duration."
        }
