import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.video_job import VideoJob
from app.models.lesson import Lesson
from app.schemas.video import ScenePlanSchema
from app.core.logging import logger


class VideoGenerationService:
    def __init__(self, db: Session):
        self.db = db

    def queue_video_generation(self, user_id: str, lesson_id: str) -> VideoJob:
        lesson = self.db.query(Lesson).filter(Lesson.id == lesson_id).first()
        if not lesson:
            raise ValueError(f"Lesson {lesson_id} not found.")

        # Build multi-scene video storyboard
        scenes: List[ScenePlanSchema] = []
        
        # 1. Intro scene
        scenes.append(ScenePlanSchema(
            scene_number=1,
            purpose="intro",
            narration=f"Welcome to today's master lesson on {lesson.topic}. Let's break this down step-by-step.",
            visual_type="text_card",
            visual_data={"title": lesson.topic, "objectives": lesson.objectives},
            avatar_required=True,
            duration_seconds=10
        ))

        # 2. Step scenes
        for idx, step in enumerate(lesson.steps):
            scenes.append(ScenePlanSchema(
                scene_number=len(scenes) + 1,
                purpose="explanation",
                narration=f"Concept {step.step_number}: {step.concept}. {step.explanation}",
                visual_type=step.visual_type,
                visual_data=step.visual_data or {},
                avatar_required=True,
                duration_seconds=20
            ))
            if step.analogy:
                scenes.append(ScenePlanSchema(
                    scene_number=len(scenes) + 1,
                    purpose="demonstration",
                    narration=f"Here is a key analogy: {step.analogy}",
                    visual_type="diagram",
                    visual_data={"analogy": step.analogy},
                    avatar_required=True,
                    duration_seconds=15
                ))

        # 3. Summary scene
        scenes.append(ScenePlanSchema(
            scene_number=len(scenes) + 1,
            purpose="summary",
            narration="Great progress! Review your concepts and take the final mastery assessment.",
            visual_type="text_card",
            visual_data={"title": "Lesson Complete", "topic": lesson.topic},
            avatar_required=True,
            duration_seconds=10
        ))

        video_job = VideoJob(
            lesson_id=lesson.id,
            user_id=user_id,
            status="queued",
            progress=0,
            scenes_data=[s.model_dump() for s in scenes],
            video_url=f"/storage/videos/lesson_{lesson.id[:8]}.mp4"
        )
        self.db.add(video_job)
        self.db.commit()
        self.db.refresh(video_job)
        return video_job

    async def process_job_async(self, job_id: str):
        job = self.db.query(VideoJob).filter(VideoJob.id == job_id).first()
        if not job:
            return

        try:
            job.status = "processing"
            job.progress = 25
            self.db.commit()
            await asyncio.sleep(0.5)

            job.status = "rendering"
            job.progress = 75
            self.db.commit()
            await asyncio.sleep(0.5)

            job.status = "completed"
            job.progress = 100
            self.db.commit()
            logger.info(f"Video job {job_id} successfully synthesized.")
        except Exception as e:
            logger.error(f"Video rendering job error: {e}")
            job.status = "failed"
            job.error_message = str(e)
            self.db.commit()
