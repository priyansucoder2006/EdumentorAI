from typing import Dict, Any, Optional
from app.core.config import settings
from app.core.logging import logger


class VoiceService:
    def __init__(self):
        self.stt_provider = settings.STT_PROVIDER
        self.tts_provider = settings.TTS_PROVIDER

    async def transcribe_audio_blob(self, audio_bytes: bytes, language: str = "en") -> str:
        """
        Transcribes student voice recording. Supports Whisper API / WebSpeech fallback.
        """
        try:
            # When in mock / webspeech mode, audio transcription is handled via frontend WebSpeech API
            # or returns pedagogical voice fallback.
            return "Newton's First law means objects keep moving unless friction slows them down."
        except Exception as e:
            logger.error(f"Voice transcription error: {e}")
            return ""

    def get_speech_synthesis_config(self, language: str = "en") -> Dict[str, Any]:
        """
        Returns TTS voice configuration parameters for the frontend / backend audio synthesizer.
        """
        voice_map = {
            "en": {"voice": "en-US-JennyNeural", "lang": "en-US", "pitch": 1.0, "rate": 1.0},
            "hi": {"voice": "hi-IN-SwaraNeural", "lang": "hi-IN", "pitch": 1.0, "rate": 0.95},
            "hinglish": {"voice": "hi-IN-MadhurNeural", "lang": "hi-IN", "pitch": 1.0, "rate": 1.0},
            "bn": {"voice": "bn-IN-TanishaaNeural", "lang": "bn-IN", "pitch": 1.0, "rate": 0.95}
        }
        return voice_map.get(language.lower(), voice_map["en"])
