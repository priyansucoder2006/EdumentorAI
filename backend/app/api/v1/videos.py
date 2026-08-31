from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.video_job import VideoJob
from app.schemas.video import VideoGenerateRequest, VideoJobResponse
from app.services.video_worker import VideoGenerationService
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/generate", response_model=VideoJobResponse)
def generate_video(
    req: VideoGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    video_service = VideoGenerationService(db)
    job = video_service.queue_video_generation(user_id=current_user.id, lesson_id=req.lesson_id)
    background_tasks.add_task(video_service.process_job_async, job.id)
    return job


@router.get("/{job_id}", response_model=VideoJobResponse)
def get_video_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(VideoJob).filter(VideoJob.id == job_id, VideoJob.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video job not found.")
    return job


@router.get("/{job_id}/status")
def get_video_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(VideoJob).filter(VideoJob.id == job_id, VideoJob.user_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video job not found.")
    return {
        "job_id": job.id,
        "status": job.status,
        "progress": job.progress,
        "video_url": job.video_url,
        "error_message": job.error_message
    }
