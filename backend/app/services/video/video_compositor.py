import os
import subprocess
import tempfile
from typing import List, Tuple, Callable, Optional
import numpy as np
import imageio
import imageio_ffmpeg
from PIL import Image
from app.services.video.scene_planner import VideoScene
from app.services.video.visual_renderer import VisualRenderer
from app.services.video.avatar_renderer import AvatarRenderer
from app.core.config import settings
from app.core.logging import logger


class VideoCompositor:
    """
    High-Speed Video Compositor.
    Uses cached scene visual boards, ultrafast H.264 encoding, and multithreaded FFmpeg muxing.
    """

    def __init__(self, fps: int = 12, width: int = 1280, height: int = 720):
        self.fps = fps or settings.VIDEO_FPS or 12
        self.width = width
        self.height = height
        self.visual_renderer = VisualRenderer(width=width, height=height)
        self.avatar_renderer = AvatarRenderer()
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    def render_and_compose_video(
        self,
        scenes_with_audio: List[Tuple[VideoScene, str, float]],
        output_mp4_path: str,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(output_mp4_path)), exist_ok=True)
        
        temp_video_only = output_mp4_path + ".temp_video.mp4"
        audio_concat_list_file = output_mp4_path + ".audio_list.txt"
        temp_merged_audio = output_mp4_path + ".temp_audio.mp3"

        total_scenes = len(scenes_with_audio)
        total_duration = sum(dur for _, _, dur in scenes_with_audio)
        logger.info(f"Fast video composition for {total_scenes} scenes, duration: {total_duration:.1f}s at {self.fps} FPS")

        # Standard compliant H.264 video writer
        writer = imageio.get_writer(
            temp_video_only,
            fps=self.fps,
            codec="libx264",
            pixelformat="yuv420p",
            macro_block_size=None,
            ffmpeg_params=[
                "-preset", "veryfast",
                "-crf", "22",
                "-profile:v", "main",
                "-pix_fmt", "yuv420p",
                "-threads", "0"
            ]
        )

        global_frame_idx = 0
        audio_files: List[str] = []

        try:
            for s_idx, (scene, audio_path, scene_dur) in enumerate(scenes_with_audio):
                audio_files.append(audio_path)
                scene_frames_count = max(1, int(scene_dur * self.fps))

                if progress_callback:
                    pct = int(25 + (s_idx / total_scenes) * 55)
                    progress_callback(pct, f"Rendering Scene {scene.scene_number}/{total_scenes}: {scene.concept[:25]}")

                # 1. Pre-render static base visual board ONCE per scene for ultra-high speed
                cached_base_frame = self.visual_renderer.render_scene_frame(
                    scene=scene,
                    time_sec=0.0,
                    total_scene_sec=scene_dur
                )

                for f_idx in range(scene_frames_count):
                    time_in_scene = f_idx / float(self.fps)

                    # 2. Fast copy cached frame and draw animated avatar
                    frame_copy = cached_base_frame.copy()
                    final_frame = self.avatar_renderer.draw_avatar_overlay(
                        base_img=frame_copy,
                        time_sec=time_in_scene + (s_idx * 10.0),
                        mood=scene.avatar_mood,
                        is_speaking=True
                    )

                    # 3. Write frame
                    writer.append_data(np.array(final_frame))
                    global_frame_idx += 1

            writer.close()
            logger.info(f"Video stream encoded: {temp_video_only} ({global_frame_idx} frames)")

            if progress_callback:
                progress_callback(85, "Finalizing MP4 video & audio synchronization...")

            # 2. Mux audio and video streams
            self._mux_video_and_audio(temp_video_only, audio_files, output_mp4_path)

            if not os.path.exists(output_mp4_path) or os.path.getsize(output_mp4_path) < 1000:
                if os.path.exists(temp_video_only) and os.path.getsize(temp_video_only) > 1000:
                    os.replace(temp_video_only, output_mp4_path)
                else:
                    raise RuntimeError(f"Video composition failed: {output_mp4_path}")

            return output_mp4_path

        finally:
            for p in [temp_video_only, audio_concat_list_file, temp_merged_audio]:
                if os.path.exists(p):
                    try: os.remove(p)
                    except Exception: pass

    def _mux_video_and_audio(self, video_file: str, audio_files: List[str], output_file: str):
        valid_audios = [f for f in audio_files if os.path.exists(f) and os.path.getsize(f) > 500]
        
        if not valid_audios:
            logger.warning("No valid audio files found to mux with video.")
            os.replace(video_file, output_file)
            return

        merged_audio_path = output_file + ".merged_audio.wav"
        concat_list_path = output_file + ".concat.txt"

        try:
            # 1. Merge all scene audio files with volume boost and 44.1kHz Stereo normalization
            if len(valid_audios) == 1:
                cmd_audio = [
                    self.ffmpeg_exe, "-y",
                    "-i", valid_audios[0],
                    "-af", "volume=1.8",
                    "-ar", "44100",
                    "-ac", "2",
                    merged_audio_path
                ]
                res_audio = subprocess.run(cmd_audio, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            else:
                # Use FFmpeg filter_complex for seamless multi-input concat with cross-platform safety
                cmd_audio = [self.ffmpeg_exe, "-y"]
                filter_inputs = ""
                for idx, a_path in enumerate(valid_audios):
                    cmd_audio.extend(["-i", a_path])
                    filter_inputs += f"[{idx}:a]"

                full_filter = f"{filter_inputs}concat=n={len(valid_audios)}:v=0:a=1[concata];[concata]volume=1.8[outa]"
                cmd_audio.extend([
                    "-filter_complex", full_filter,
                    "-map", "[outa]",
                    "-ar", "44100",
                    "-ac", "2",
                    merged_audio_path
                ])
                res_audio = subprocess.run(cmd_audio, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                # Fallback to concat file demuxer if filter_complex had any issue
                if res_audio.returncode != 0 or not os.path.exists(merged_audio_path):
                    logger.warning(f"Filter complex audio merge fallback: {res_audio.stderr[:200]}")
                    with open(concat_list_path, "w", encoding="utf-8") as cf:
                        for a_path in valid_audios:
                            safe_path = os.path.abspath(a_path).replace("\\", "/")
                            cf.write(f"file '{safe_path}'\n")
                    cmd_fallback = [
                        self.ffmpeg_exe, "-y",
                        "-f", "concat", "-safe", "0",
                        "-i", concat_list_path,
                        "-af", "volume=1.8",
                        "-ar", "44100",
                        "-ac", "2",
                        merged_audio_path
                    ]
                    subprocess.run(cmd_fallback, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

            # 2. Mux video with high-quality AAC stereo audio and +faststart flag
            if os.path.exists(merged_audio_path) and os.path.getsize(merged_audio_path) > 1000:
                cmd_mux = [
                    self.ffmpeg_exe, "-y",
                    "-i", video_file,
                    "-i", merged_audio_path,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-ar", "44100",
                    "-ac", "2",
                    "-movflags", "+faststart",
                    "-shortest",
                    output_file
                ]
                res = subprocess.run(cmd_mux, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if res.returncode == 0 and os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
                    logger.info(f"Successfully muxed video with loud, synchronized AAC audio: {output_file}")
                else:
                    logger.error(f"FFmpeg muxing failed ({res.returncode}): {res.stderr[:250]}")
                    if os.path.exists(video_file):
                        os.replace(video_file, output_file)
            else:
                logger.warning("Merged audio file was not generated; falling back to video-only stream.")
                os.replace(video_file, output_file)

        except Exception as e:
            logger.error(f"Muxing error: {e}", exc_info=True)
            if os.path.exists(video_file):
                os.replace(video_file, output_file)
        finally:
            for p in [concat_list_path, merged_audio_path]:
                if os.path.exists(p):
                    try: os.remove(p)
                    except Exception: pass
