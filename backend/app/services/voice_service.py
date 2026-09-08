from typing import Dict, Any, Optional
from app.services.voice.stt_provider import get_stt_provider
from app.services.voice.tts_provider import get_tts_provider
from app.core.logging import logger


class VoiceService:
    def __init__(self):
        self.stt_provider = get_stt_provider()
        self.tts_provider = get_tts_provider()

    async def transcribe_audio_blob(self, audio_bytes: bytes, language: str = "en") -> str:
        """
        Transcribes student voice recording using configured STT provider.
        """
        try:
            return await self.stt_provider.transcribe(audio_bytes, language)
        except Exception as e:
            logger.error(f"Voice transcription error: {e}")
            return ""

    async def synthesize_speech(self, text: str, language: str = "en") -> bytes:
        """
        Synthesizes speech audio bytes from text narration.
        """
        try:
            return await self.tts_provider.synthesize(text, language)
        except Exception as e:
            logger.error(f"Voice synthesis error: {e}")
            return b""

    def get_speech_synthesis_config(self, language: str = "en") -> Dict[str, Any]:
        """
        Returns TTS voice configuration parameters for client-side playback.
        """
        return self.tts_provider.get_voice_config(language)
