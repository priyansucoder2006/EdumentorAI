from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.mongodb import get_mongo_db, get_mongo_client
from app.models.user import User
from app.models.document import Document, DocumentChunk
from app.models.lesson import Lesson
from app.models.interaction import Interaction
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/system")
def get_system_diagnostics(db: Session = Depends(get_db)):
    doc_count = db.query(Document).count()
    chunk_count = db.query(DocumentChunk).count()
    lesson_count = db.query(Lesson).count()
    interaction_count = db.query(Interaction).count()

    # MongoDB Atlas Status
    mongo_status = "disconnected"
    mongo_collections = {}
    try:
        mongo_db = get_mongo_db()
        if mongo_db is not None:
            mongo_status = "connected"
            mongo_collections = {
                "users": mongo_db.users.count_documents({}),
                "profiles": mongo_db.learner_profiles.count_documents({}),
                "interactions": mongo_db.interactions.count_documents({}),
                "audit_logs": mongo_db.audit_logs.count_documents({})
            }
    except Exception as e:
        mongo_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "database_url": settings.DATABASE_URL.split("://")[0] + "://...",
        "mongodb": {
            "status": mongo_status,
            "database": settings.MONGODB_DB_NAME,
            "collections": mongo_collections
        },
        "storage": {
            "documents_indexed": doc_count,
            "chunks_stored": chunk_count,
            "lessons_conducted": lesson_count,
            "interactions_evaluated": interaction_count
        }
    }


@router.get("/ai-trace")
def get_ai_traces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_interactions = (
        db.query(Interaction)
        .filter(Interaction.user_id == current_user.id)
        .order_by(Interaction.created_at.desc())
        .limit(20)
        .all()
    )
    traces = []
    for it in user_interactions:
        traces.append({
            "interaction_id": it.id,
            "question": it.question,
            "student_answer": it.student_answer,
            "evaluation": it.evaluation,
            "misconception": it.misconception,
            "adaptive_decision": it.adaptive_decision,
            "confidence": it.confidence,
            "created_at": it.created_at
        })
    return {"total_recent_traces": len(traces), "traces": traces}
