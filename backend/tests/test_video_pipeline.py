import os
import pytest
import asyncio
from app.models.lesson import Lesson, LessonStep
from app.services.video.scene_planner import ScenePlanner, VideoScene
from app.services.video.tts_renderer import TTSRenderer
from app.services.video.visual_renderer import VisualRenderer
from app.services.video.avatar_renderer import AvatarRenderer
from app.services.video.video_compositor import VideoCompositor
from app.services.video.pipeline import VideoPipeline
from app.services.video_worker import VideoGenerationService
from app.models.video_job import VideoJob


@pytest.mark.asyncio
async def test_scene_planner_creates_valid_storyboard(db_session, test_user):
    lesson = Lesson(
        id="test-lesson-vid-1",
        user_id=test_user.id,
        topic="Cellular Respiration & ATP Synthesis",
        language="en",
        difficulty="intermediate",
        duration_minutes=20,
        objectives=["Understand Glycolysis", "Master the Krebs Cycle", "Trace the Electron Transport Chain"],
        status="in_progress",
        current_step_index=0,
        state="EXPLAIN"
    )
    step1 = LessonStep(
        lesson_id=lesson.id,
        step_number=1,
        concept="Glycolysis in Cytoplasm",
        explanation="Glycolysis converts one molecule of glucose into two molecules of pyruvate, yielding a net of 2 ATP and 2 NADH.",
        analogy="Like splitting a 100-dollar bill into two 50-dollar bills with a small transaction bonus.",
        visual_type="diagram",
        visual_data={"title": "Glycolysis Pathway", "steps": [{"title": "Glucose", "desc": "6-Carbon sugar"}]},
        question={"prompt": "What is the net ATP yield of glycolysis?", "options": ["2 ATP", "36 ATP", "0 ATP", "4 ATP"], "correct_answer": "2 ATP"},
        expected_answer="Net 2 ATP molecules.",
        difficulty="intermediate"
    )
    lesson.steps = [step1]
    db_session.add(lesson)
    db_session.commit()

    scenes = ScenePlanner.plan_scenes_for_lesson(lesson)
    assert len(scenes) >= 3
    assert scenes[0].scene_type == "intro"
    assert "Cellular Respiration" in scenes[0].title
    assert scenes[1].scene_type == "concept_explanation"
    assert "Glycolysis" in scenes[1].concept
    assert scenes[-1].scene_type == "summary"


@pytest.mark.asyncio
async def test_real_mp4_file_generation_and_composition():
    scene = VideoScene(
        scene_id="scene_test_exec",
        scene_number=1,
        scene_type="concept_explanation",
        title="Ohm's Law Fundamentals",
        concept="Electric Potential & Current",
        narration="Ohm's law states that current is directly proportional to voltage across a conductor.",
        on_screen_text="V = I * R\n\nVoltage = Current x Resistance",
        visual_type="math",
        visual_data={"equation": "V = I \\times R", "steps": ["1. V: Volts", "2. I: Amperes", "3. R: Ohms"]},
        avatar_mood="explaining",
        estimated_duration_seconds=3.5
    )

    tts = TTSRenderer()
    audio_path, dur = await tts.synthesize_scene_audio(scene.narration, language="en")
    assert os.path.exists(audio_path)
    assert dur > 1.0

    compositor = VideoCompositor(fps=10, width=1280, height=720)
    output_mp4 = "./storage/videos/test_e2e_video_generated.mp4"

    final_path = compositor.render_and_compose_video(
        scenes_with_audio=[(scene, audio_path, min(dur, 3.5))],
        output_mp4_path=output_mp4
    )

    # CRITICAL VERIFICATION: File MUST exist and have real non-zero binary size
    assert os.path.exists(final_path), f"Video file {final_path} does not exist!"
    file_size = os.path.getsize(final_path)
    assert file_size > 10000, f"Generated video file size ({file_size} bytes) is too small!"
    print(f"Verified Real MP4 Created: {final_path} ({file_size} bytes)")


@pytest.mark.asyncio
async def test_video_worker_service_end_to_end(db_session, test_user):
    lesson = Lesson(
        id="test-vid-worker-lesson",
        user_id=test_user.id,
        topic="Photosynthesis Light Reactions",
        language="en",
        difficulty="beginner",
        duration_minutes=5,
        objectives=["Understand light absorption by chlorophyll"],
        status="in_progress",
        current_step_index=0,
        state="EXPLAIN"
    )
    step1 = LessonStep(
        lesson_id=lesson.id,
        step_number=1,
        concept="Chlorophyll Photon Capture",
        explanation="Chlorophyll in the thylakoid membrane absorbs blue and red wavelengths of light, exciting electrons.",
        analogy="Like a solar panel capturing sunlight to charge a battery.",
        visual_type="diagram",
        visual_data={"title": "Thylakoid Membrane"},
        question={"prompt": "Which organelle houses chlorophyll?", "options": ["Chloroplast", "Mitochondria", "Nucleus", "Ribosome"], "correct_answer": "Chloroplast"},
        expected_answer="Chloroplast organelle.",
        difficulty="beginner"
    )
    lesson.steps = [step1]
    db_session.add(lesson)
    db_session.commit()

    service = VideoGenerationService(db_session)
    job, is_new = service.queue_video_generation(user_id=test_user.id, lesson_id=lesson.id)
    job_id = str(job.id)
    assert job.status == "queued"
    assert is_new is True

    # Process job asynchronously with test db session
    await service.process_job_async(job_id, db=db_session)

    updated_job = db_session.query(VideoJob).filter(VideoJob.id == job_id).first()
    assert updated_job.status == "completed", f"Job failed with error: {updated_job.error_message}"
    assert updated_job.progress == 100
    assert updated_job.video_url is not None
    assert "/storage/videos/" in updated_job.video_url

    # Check physical file on disk
    disk_path = "." + updated_job.video_url
    assert os.path.exists(disk_path), f"Expected file on disk does not exist: {disk_path}"
    assert os.path.getsize(disk_path) > 10000
