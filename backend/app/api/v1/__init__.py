from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.rag import router as rag_router
from app.api.v1.lessons import router as lessons_router
from app.api.v1.interactions import router as interactions_router
from app.api.v1.assessments import router as assessments_router
from app.api.v1.progress import router as progress_router
from app.api.v1.recommendations import router as recommendations_router
from app.api.v1.videos import router as videos_router
from app.api.v1.diagnostics import router as diagnostics_router
from app.api.v1.voice import router as voice_router
from app.api.v1.code import router as code_router
from app.api.v1.learning_video import router as learning_video_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
api_router.include_router(rag_router, prefix="/rag", tags=["RAG"])
api_router.include_router(lessons_router, prefix="/lessons", tags=["Lessons"])
api_router.include_router(interactions_router, prefix="/interactions", tags=["Interactions & Evaluation"])
api_router.include_router(assessments_router, prefix="/assessments", tags=["Assessments"])
api_router.include_router(progress_router, prefix="/progress", tags=["Progress & Mastery"])
api_router.include_router(recommendations_router, prefix="/recommendations", tags=["Recommendations"])
api_router.include_router(videos_router, prefix="/videos", tags=["Video Generation"])
api_router.include_router(diagnostics_router, prefix="/diagnostics", tags=["Diagnostics & Traces"])
api_router.include_router(voice_router, prefix="/voice", tags=["Voice TTS & STT"])
api_router.include_router(code_router, prefix="/code", tags=["Code Execution (Judge0)"])
api_router.include_router(learning_video_router, prefix="/learning", tags=["Learning Video Recommendation"])

