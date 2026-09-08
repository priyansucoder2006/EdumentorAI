import os
import io
import re
import tempfile
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from gtts import gTTS
import edge_tts
from app.core.config import settings
from app.core.logging import logger


class TextToSpeechProvider(ABC):
    """Abstract provider interface for Text-to-Speech synthesis."""

    @abstractmethod
    async def synthesize(self, text: str, language: str = "en") -> bytes:
        """Synthesize text into raw audio bytes (MP3 / WAV)."""
        pass

    @abstractmethod
    def get_voice_config(self, language: str = "en") -> Dict[str, Any]:
        """Returns client-side voice metadata for WebSpeech fallback."""
        pass


class EdgeTTSProvider(TextToSpeechProvider):
    """Synthesizes high-definition neural speech using EdgeTTS."""

    VOICE_MAP = {
        "en": "en-US-JennyNeural",
        "hi": "hi-IN-SwaraNeural",
        "hinglish": "hi-IN-MadhurNeural",
        "bn": "bn-IN-TanishaaNeural"
    }

    async def synthesize(self, text: str, language: str = "en") -> bytes:
        clean_text = self._clean_text(text)
        voice = self.VOICE_MAP.get(language.lower(), "en-US-JennyNeural")
        communicate = edge_tts.Communicate(clean_text, voice)
        
        audio_stream = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_stream.write(chunk["data"])
        
        return audio_stream.getvalue()

    def get_voice_config(self, language: str = "en") -> Dict[str, Any]:
        voice = self.VOICE_MAP.get(language.lower(), "en-US-JennyNeural")
        return {"voice": voice, "lang": language, "pitch": 1.0, "rate": 0.95}

    def _clean_text(self, text: str) -> str:
        cleaned = re.sub(r'\$([^\$]+)\$', r'\1', text)
        cleaned = re.sub(r'[\*\#\`\_]', '', cleaned)
        cleaned = re.sub(r'\\[a-zA-Z]+', ' ', cleaned)
        return re.sub(r'\s+', ' ', cleaned).strip() or "Let us review this."


class GTTSProvider(TextToSpeechProvider):
    """Synthesizes audio using Google Text-to-Speech."""

    LANG_MAP = {
        "en": "en",
        "hi": "hi",
        "hinglish": "hi",
        "bn": "bn"
    }

    async def synthesize(self, text: str, language: str = "en") -> bytes:
        clean_text = re.sub(r'[\*\#\`\_\$]', '', text).strip() or "Explanation"
        lang_code = self.LANG_MAP.get(language.lower(), "en")
        
        tts = gTTS(text=clean_text, lang=lang_code, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()

    def get_voice_config(self, language: str = "en") -> Dict[str, Any]:
        return {"voice": "Google Natural", "lang": language, "pitch": 1.0, "rate": 1.0}


class OpenAITTSProvider(TextToSpeechProvider):
    """Synthesizes audio using OpenAI / external TTS endpoint."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.TTS_API_KEY or settings.LLM_API_KEY

    async def synthesize(self, text: str, language: str = "en") -> bytes:
        import httpx

        if not self.api_key:
            raise ValueError("OpenAI API key not configured for TTS.")

        url = "https://api.openai.com/v1/audio/speech"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "tts-1",
            "input": text[:4000],
            "voice": "alloy",
            "response_format": "mp3"
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, headers=headers, json=payload)
            res.raise_for_status()
            return res.content

    def get_voice_config(self, language: str = "en") -> Dict[str, Any]:
        return {"voice": "alloy", "lang": language, "pitch": 1.0, "rate": 1.0}


def get_tts_provider() -> TextToSpeechProvider:
    provider_type = (settings.TTS_PROVIDER or "edge_tts").lower()
    if provider_type == "openai" and (settings.TTS_API_KEY or settings.LLM_API_KEY):
        return OpenAITTSProvider()
    elif provider_type == "gtts":
        return GTTSProvider()
    # Default to EdgeTTS with gTTS fallback
    return EdgeTTSProvider()
