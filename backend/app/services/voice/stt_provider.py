import os
import io
import tempfile
from abc import ABC, abstractmethod
from typing import Optional
from app.core.config import settings
from app.core.logging import logger


class SpeechToTextProvider(ABC):
    """Abstract provider interface for Speech-to-Text transcription."""

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> str:
        """Transcribe raw audio bytes into text."""
        pass


class OpenAIWhisperSTTProvider(SpeechToTextProvider):
    """Transcribes audio using OpenAI / Groq Whisper API."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.LLM_API_KEY
        self.base_url = base_url or ("https://api.groq.com/openai/v1" if settings.LLM_PROVIDER == "groq" else "https://api.openai.com/v1")

    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> str:
        import httpx

        if not self.api_key:
            raise ValueError("OpenAI/Groq API key not configured for Whisper STT.")

        url = f"{self.base_url}/audio/transcriptions"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        # Determine model
        model = "whisper-large-v3" if "groq" in self.base_url else "whisper-1"

        files = {"file": ("recording.wav", audio_bytes, "audio/wav")}
        data = {"model": model, "language": language[:2]}

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, headers=headers, files=files, data=data)
            res.raise_for_status()
            res_data = res.json()
            return res_data.get("text", "").strip()


class LocalBrowserFallbackSTTProvider(SpeechToTextProvider):
    """Fallback STT provider when browser WebSpeech handles live input or offline development."""

    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> str:
        # If no external Whisper API is configured, return an informational notice
        logger.info(f"Local STT received {len(audio_bytes)} bytes of audio for language {language}.")
        if not audio_bytes:
            return ""
        return ""


def get_stt_provider() -> SpeechToTextProvider:
    provider_type = (settings.STT_PROVIDER or "webspeech").lower()
    if (provider_type in ["whisper", "openai", "groq"]) and settings.LLM_API_KEY:
        return OpenAIWhisperSTTProvider()
    return LocalBrowserFallbackSTTProvider()
