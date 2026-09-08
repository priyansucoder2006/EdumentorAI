from fastapi import APIRouter, Depends, UploadFile, File, Form, Response, HTTPException, status
from pydantic import BaseModel
from app.services.voice_service import VoiceService
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()


class TTSSynthesizeRequest(BaseModel):
    text: str
    language: str = "en"


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("en"),
    current_user: User = Depends(get_current_user)
):
    """
    Transcribes student audio recording.
    """
    audio_bytes = await file.read()
    voice_service = VoiceService()
    transcript = await voice_service.transcribe_audio_blob(audio_bytes, language=language)
    return {"transcript": transcript, "language": language}


@router.post("/synthesize")
async def synthesize_speech(
    req: TTSSynthesizeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Synthesizes teacher speech narration into audio MP3 stream.
    """
    voice_service = VoiceService()
    audio_bytes = await voice_service.synthesize_speech(req.text, language=req.language)
    if not audio_bytes:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Speech synthesis failed.")
    return Response(content=audio_bytes, media_type="audio/mpeg")


@router.get("/config")
def get_voice_config(
    language: str = "en",
    current_user: User = Depends(get_current_user)
):
    """
    Returns TTS voice playback parameters.
    """
    voice_service = VoiceService()
    return voice_service.get_speech_synthesis_config(language)
