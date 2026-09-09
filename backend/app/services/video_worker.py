import os
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.video_job import VideoJob
from app.models.lesson import Lesson
from app.schemas.video import ScenePlanSchema
from app.services.video.pipeline import VideoPipeline
from app.core.database import SessionLocal
from app.core.logging import logger


class VideoGenerationService:
    def __init__(self, db: Session):
        self.db = db
        self.pipeline = VideoPipeline(fps=12)

    def queue_video_generation(self, user_id: str, lesson_id: str, force_regenerate: bool = False) -> Tuple[VideoJob, bool]:
        lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found.")

        # Check if there is already a completed video for this lesson with a valid file on disk
        if not force_regenerate:
            existing_completed = (
                self.db.query(VideoJob)
                .filter(VideoJob.lesson_id == lesson_id, VideoJob.status == "completed")
                .order_by(VideoJob.created_at.desc())
                .first()
            )
            if existing_completed and existing_completed.video_url:
                local_path = os.path.join(".", existing_completed.video_url.lstrip("/"))
                if os.path.exists(local_path) and os.path.getsize(local_path) > 10000:
                    logger.info(f"Returning existing completed video for lesson {lesson_id}: {existing_completed.id}")
                    return existing_completed, False

            # Check if there is already an active job running for this lesson
            existing_active = (
                self.db.query(VideoJob)
                .filter(VideoJob.lesson_id == lesson_id, VideoJob.status.in_(["queued", "processing", "rendering"]))
                .order_by(VideoJob.created_at.desc())
                .first()
            )
            if existing_active:
                logger.info(f"Attaching to existing active video job {existing_active.id} for lesson {lesson_id}")
                return existing_active, False

        # Plan scenes to store initial storyboard data
        scenes = self.pipeline.scene_planner.plan_scenes_for_lesson(lesson)
        scenes_data = [
            ScenePlanSchema(
                scene_number=s.scene_number,
                purpose=s.scene_type,
                narration=s.narration,
                visual_type=s.visual_type,
                visual_data=s.visual_data,
                avatar_required=True,
                duration_seconds=int(s.estimated_duration_seconds)
            ).model_dump()
            for s in scenes
        ]

        video_filename = f"lesson_{lesson.id[:8]}_{int(datetime.now(timezone.utc).timestamp())}.mp4"
        video_url = f"/storage/videos/{video_filename}"

        video_job = VideoJob(
            lesson_id=lesson.id,
            user_id=user_id,
            status="queued",
            progress=5,
            scenes_data=scenes_data,
            video_url=video_url
        )
        self.db.add(video_job)
        self.db.commit()
        self.db.refresh(video_job)
        return video_job, True

    async def process_job_async(self, job_id: str, db: Optional[Session] = None):
        """
        Background task worker that executes real video rendering pipeline and updates database.
        Always uses thread-safe isolated sessions so progress commits work reliably in real-time.
        """
        worker_db = db or SessionLocal()
        should_close_main = (db is None)
        try:
            job = worker_db.query(VideoJob).filter(VideoJob.id == job_id).first()
            if not job:
                logger.error(f"Video job {job_id} not found in worker thread.")
                return

            lesson = worker_db.query(Lesson).filter(Lesson.id == job.lesson_id).first()
            if not lesson:
                job.status = "failed"
                job.error_message = "Lesson not found."
                worker_db.commit()
                return

            job.status = "processing"
            job.progress = 10
            worker_db.commit()

            video_storage_dir = "./storage/videos"
            os.makedirs(video_storage_dir, exist_ok=True)
            video_filename = os.path.basename(job.video_url or f"lesson_{lesson.id[:8]}.mp4")
            output_mp4_path = os.path.join(video_storage_dir, video_filename)

            def progress_callback(pct: int, message: str):
                # Thread-safe database progress commit inside callback worker thread
                if db is not None:
                    job.progress = min(99, max(job.progress, pct))
                    if pct >= 20 and job.status != "rendering":
                        job.status = "rendering"
                    worker_db.commit()
                    return
                p_db = SessionLocal()
                try:
                    p_job = p_db.query(VideoJob).filter(VideoJob.id == job_id).first()
                    if p_job:
                        p_job.progress = min(99, max(p_job.progress, pct))
                        if pct >= 20 and p_job.status != "rendering":
                            p_job.status = "rendering"
                        p_db.commit()
                        logger.info(f"[VideoJob {job_id[:8]}] {pct}%: {message}")
                except Exception as ex:
                    logger.warning(f"Error updating video job progress: {ex}")
                finally:
                    p_db.close()

            # Run actual video rendering pipeline
            result = await self.pipeline.generate_lesson_video(
                lesson=lesson,
                output_mp4_path=output_mp4_path,
                progress_callback=progress_callback
            )

            # Final completion commit
            if db is not None:
                job.status = "completed"
                job.progress = 100
                job.video_url = result["video_url"]
                job.scenes_data = result["scenes_data"]
                job.updated_at = datetime.now(timezone.utc)
                worker_db.commit()
                logger.info(f"Video job {job_id} successfully finished! Playable MP4: {output_mp4_path} ({result['file_size']} bytes)")
            else:
                final_db = SessionLocal()
                try:
                    final_job = final_db.query(VideoJob).filter(VideoJob.id == job_id).first()
                    if final_job:
                        final_job.status = "completed"
                        final_job.progress = 100
                        final_job.video_url = result["video_url"]
                        final_job.scenes_data = result["scenes_data"]
                        final_job.updated_at = datetime.now(timezone.utc)
                        final_db.commit()
                        logger.info(f"Video job {job_id} successfully finished! Playable MP4: {output_mp4_path} ({result['file_size']} bytes)")
                finally:
                    final_db.close()

        except Exception as e:
            logger.error(f"Error executing video job {job_id}: {e}", exc_info=True)
            if db is not None:
                job.status = "failed"
                job.error_message = str(e)
                worker_db.commit()
            else:
                err_db = SessionLocal()
                try:
                    err_job = err_db.query(VideoJob).filter(VideoJob.id == job_id).first()
                    if err_job:
                        err_job.status = "failed"
                        err_job.error_message = str(e)
                        err_db.commit()
                except Exception:
                    pass
                finally:
                    err_db.close()
        finally:
            if should_close_main:
                worker_db.close()
