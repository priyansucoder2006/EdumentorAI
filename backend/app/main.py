import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
from app.core.logging import logger
from app.core.security import get_password_hash
from app.core.mongodb import init_mongodb, MongoSyncService
from app.models.user import User
from app.models.learner_profile import LearnerProfile
from app.models.document import Document, DocumentChunk
from app.models.lesson import Lesson, LessonStep
from app.models.interaction import Interaction
from app.models.assessment import Assessment
from app.models.learning_progress import LearningProgress
from app.models.learning_path import LearningPath
from app.models.video_job import VideoJob
from app.api.v1 import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    # Initialize MongoDB Atlas
    init_mongodb()

    # Seed initial test user if database is completely empty
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == "student@edumentor.ai").first()
        if not existing_user:
            demo_user = User(
                id="demo-user-12345",
                name="Aarav Sharma",
                email="student@edumentor.ai",
                password_hash=get_password_hash("password123"),
                preferred_language="hinglish",
                education_level="beginner"
            )
            db.add(demo_user)
            db.flush()

            demo_profile = LearnerProfile(
                user_id=demo_user.id,
                knowledge_level="beginner",
                learning_goal="school_exam",
                preferred_depth="intuitive",
                available_time=20,
                learning_style="visual",
                preferred_language="hinglish",
                strong_topics=["Speed & Velocity", "Linear Graphs"],
                weak_topics=["Inertia", "Action-Reaction Pairs"]
            )
            db.add(demo_profile)
            db.commit()
            logger.info("Created default demo user: student@edumentor.ai / password123")
    except Exception as e:
        logger.error(f"Error during startup initialization: {e}")
    finally:
        db.close()

    yield
    logger.info("Application shutdown complete.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permissive for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static storage
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("./storage/videos", exist_ok=True)
app.mount("/storage", StaticFiles(directory="./storage"), name="storage")

# Register API Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs": f"{settings.API_V1_STR}/docs"
    }
