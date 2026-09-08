import os
import re
import asyncio
import tempfile
import httpx
from typing import Tuple, Optional, List
from gtts import gTTS
import edge_tts
from app.core.config import settings
from app.core.logging import logger


class TTSRenderer:
    """
    High-Speed Parallel TTS Engine supporting EdgeTTS, ElevenLabs API, and gTTS.
    """

    VOICE_MAP = {
        "en": "en-US-JennyNeural",
        "hi": "hi-IN-SwaraNeural",
        "hinglish": "hi-IN-MadhurNeural",
        "bn": "bn-IN-TanishaaNeural"
    }

    GTTS_LANG_MAP = {
        "en": "en",
        "hi": "hi",
        "hinglish": "hi",
        "bn": "bn"
    }

    @staticmethod
    def clean_text_for_speech(text: str) -> str:
        # Convert LaTeX and math symbols to natural readable spoken text
        cleaned = text.replace('$', '')
        cleaned = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1 divided by \2', cleaned)
        cleaned = re.sub(r'\\sqrt\{([^}]+)\}', r'square root of \1', cleaned)
        cleaned = re.sub(r'[\*\#\`\_]', '', cleaned)
        cleaned = re.sub(r'\\[a-zA-Z]+', ' ', cleaned)
        cleaned = cleaned.replace('=', ' equals ')
        cleaned = cleaned.replace('≠', ' does not equal ')
        cleaned = cleaned.replace('≈', ' approximately equals ')
        cleaned = cleaned.replace('->', ' leads to ')
        cleaned = cleaned.replace('=>', ' implies ')
        cleaned = cleaned.replace('&', ' and ')
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned or "Let's explore this concept."

    async def synthesize_all_scenes_parallel(
        self,
        narrations_with_languages: List[Tuple[str, str]]
    ) -> List[Tuple[str, float]]:
        """
        Synthesizes audio for all scenes in parallel using asyncio.gather.
        Reduces total TTS time from 30s+ down to ~1-2 seconds.
        """
        tasks = [
            self.synthesize_scene_audio(narration=narr, language=lang)
            for narr, lang in narrations_with_languages
        ]
        return await asyncio.gather(*tasks)

    async def synthesize_scene_audio(
        self,
        narration: str,
        language: str = "en",
        output_filepath: Optional[str] = None
    ) -> Tuple[str, float]:
        clean_text = self.clean_text_for_speech(narration)
        
        if not output_filepath:
            fd, output_filepath = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)

        lang_key = language.lower() if language else "en"
        duration = max(3.5, len(clean_text.split()) * 0.35)

        # 1. ElevenLabs API (if a valid non-empty key is provided)
        if settings.ELEVENLABS_API_KEY and len(settings.ELEVENLABS_API_KEY) > 20 and not settings.ELEVENLABS_API_KEY.startswith("sk_dummy"):
            try:
                eleven_url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
                headers = {
                    "xi-api-key": settings.ELEVENLABS_API_KEY,
                    "Content-Type": "application/json"
                }
                payload = {
                    "text": clean_text,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
                }
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.post(eleven_url, json=payload, headers=headers)
                    if resp.status_code == 200:
                        with open(output_filepath, "wb") as f:
                            f.write(resp.content)
                        measured = self._measure_audio_duration(output_filepath)
                        return output_filepath, measured or duration
            except Exception as e:
                logger.warning(f"ElevenLabs TTS failed: {e}. Falling back to EdgeTTS...")

        # 2. EdgeTTS (Fast, High-Fidelity Microsoft Neural Voice)
        try:
            voice_name = self.VOICE_MAP.get(lang_key, "en-US-JennyNeural")
            communicate = edge_tts.Communicate(clean_text, voice_name)
            await communicate.save(output_filepath)
            
            if os.path.exists(output_filepath) and os.path.getsize(output_filepath) > 1000:
                measured_duration = self._measure_audio_duration(output_filepath)
                return output_filepath, measured_duration or duration
        except Exception as e:
            logger.warning(f"EdgeTTS failed: {e}. Falling back to gTTS...")

        # 3. gTTS Fallback
        try:
            gtts_lang = self.GTTS_LANG_MAP.get(lang_key, "en")
            tts = gTTS(text=clean_text, lang=gtts_lang, slow=False)
            tts.save(output_filepath)

            if os.path.exists(output_filepath) and os.path.getsize(output_filepath) > 1000:
                measured_duration = self._measure_audio_duration(output_filepath)
                return output_filepath, measured_duration or duration
        except Exception as e:
            logger.warning(f"gTTS failed: {e}. Generating silent fallback...")

        # 4. Silent fallback
        self._generate_silent_wav(output_filepath, duration)
        return output_filepath, duration

    def _measure_audio_duration(self, filepath: str) -> Optional[float]:
        try:
            import imageio_ffmpeg
            import subprocess

            cmd = [
                imageio_ffmpeg.get_ffmpeg_exe(),
                "-i", filepath,
                "-f", "null", "-"
            ]
            res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            match = re.search(r'Duration:\s*(\d+):(\d+):(\d+\.\d+)', res.stderr)
            if match:
                hours, mins, secs = match.groups()
                return int(hours) * 3600 + int(mins) * 60 + float(secs)
        except Exception:
            pass
        return None

    def _generate_silent_wav(self, filepath: str, duration_sec: float):
        import wave
        import struct

        sample_rate = 22050
        num_samples = int(duration_sec * sample_rate)
        with wave.open(filepath, "w") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            silence_data = struct.pack(f"<{num_samples}h", *[0] * num_samples)
            wav_file.writeframes(silence_data)
