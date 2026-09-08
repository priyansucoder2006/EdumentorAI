import os
import asyncio
from typing import Callable, Optional, Dict, Any, List
from app.models.lesson import Lesson
from app.services.video.scene_planner import ScenePlanner, VideoScene
from app.services.video.tts_renderer import TTSRenderer
from app.services.video.video_compositor import VideoCompositor
from app.services.video.external_providers import CloudVideoProvider
from app.core.config import settings
from app.core.logging import logger


class VideoPipeline:
    """
    High-Performance AI Video Generation Pipeline.
    Supports:
    1. Ultra-fast local synthesis (Parallel TTS + Cached Visual Boards + Ultrafast H.264)
    2. Cloud AI Video Engines (D-ID, HeyGen) if API keys are configured.
    """

    def __init__(self, fps: int = 12):
        self.scene_planner = ScenePlanner()
        self.tts_renderer = TTSRenderer()
        self.compositor = VideoCompositor(fps=fps or settings.VIDEO_FPS or 12)

    async def generate_lesson_video(
        self,
        lesson: Lesson,
        output_mp4_path: str,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> Dict[str, Any]:
        if progress_callback:
            progress_callback(5, f"Planning storyboard for '{lesson.topic}'...")

        # 1. Plan focused, high-impact scenes
        scenes = self.scene_planner.plan_scenes_for_lesson(lesson)
        logger.info(f"Planned {len(scenes)} streamlined scenes for lesson {lesson.id}")

        # Check for Cloud Video Provider (D-ID / HeyGen) only if explicitly selected
        if settings.VIDEO_ENGINE == "d_id" and settings.D_ID_API_KEY:
            if progress_callback:
                progress_callback(15, "Generating photorealistic AI Teacher video with D-ID API...")
            full_script = " ".join([s.narration for s in scenes])
            cloud_url = await CloudVideoProvider.generate_avatar_video_did(
                script_text=full_script,
                language=lesson.language or "en"
            )
            if cloud_url:
                if progress_callback:
                    progress_callback(95, "Downloading high-resolution MP4 stream...")
                import httpx
                async with httpx.AsyncClient() as client:
                    r = await client.get(cloud_url)
                    with open(output_mp4_path, "wb") as vf:
                        vf.write(r.content)
                return {
                    "status": "completed",
                    "video_url": f"/storage/videos/{os.path.basename(output_mp4_path)}",
                    "video_path": output_mp4_path,
                    "file_size": os.path.getsize(output_mp4_path),
                    "scenes_data": [s.model_dump() for s in scenes],
                    "total_scenes": len(scenes),
                    "duration_seconds": sum(s.estimated_duration_seconds for s in scenes)
                }

        # 2. Parallel TTS Voice Synthesis
        if progress_callback:
            progress_callback(12, f"Synthesizing voice narration for {len(scenes)} scenes in parallel...")

        audio_temp_files = []
        scenes_with_audio = []

        try:
            narr_lang_pairs = [(s.narration, lesson.language or "en") for s in scenes]
            tts_results = await self.tts_renderer.synthesize_all_scenes_parallel(narr_lang_pairs)

            for s, (audio_file, dur) in zip(scenes, tts_results):
                audio_temp_files.append(audio_file)
                # Keep visual frame on screen for duration of voice narration plus small pause
                scene_dur = max(3.5, dur + 0.3)
                scenes_with_audio.append((s, audio_file, scene_dur))

            if progress_callback:
                progress_callback(25, "Rendering visual boards & animated avatar stream...")

            # 3. Fast video composition in thread pool
            loop = asyncio.get_event_loop()
            final_file = await loop.run_in_executor(
                None,
                self.compositor.render_and_compose_video,
                scenes_with_audio,
                output_mp4_path,
                progress_callback
            )

            if not os.path.exists(final_file) or os.path.getsize(final_file) < 1000:
                raise RuntimeError(f"Video file was not generated: {final_file}")

            file_size_bytes = os.path.getsize(final_file)
            logger.info(f"Lesson {lesson.id} video generated in record time: {final_file} ({file_size_bytes} bytes)")

            return {
                "status": "completed",
                "video_url": f"/storage/videos/{os.path.basename(final_file)}",
                "video_path": final_file,
                "file_size": file_size_bytes,
                "scenes_data": [sc.model_dump() for sc, _, _ in scenes_with_audio],
                "total_scenes": len(scenes),
                "duration_seconds": sum(dur for _, _, dur in scenes_with_audio)
            }

        finally:
            for a_tmp in audio_temp_files:
                if os.path.exists(a_tmp):
                    try: os.remove(a_tmp)
                    except Exception: pass
