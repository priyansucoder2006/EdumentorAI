import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "EduMentor AI — Adaptive AI Teacher"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DEBUG: bool = True
    SECRET_KEY: str = "edumentor-super-secure-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Database
    DATABASE_URL: str = "sqlite:///./edumentor.db"
    MONGODB_URL: str = ""
    MONGODB_DB_NAME: str = "edumentor_db"

    # AI Providers
    LLM_PROVIDER: str = "groq"  # "mock", "openai", "gemini", "groq"
    LLM_MODEL: str = "openai/gpt-oss-20b"
    LLM_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    
    # Embeddings
    EMBEDDING_PROVIDER: str = "local"  # "local", "openai", "mock"
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_DIM: int = 384

    # Multimodal Providers
    STT_PROVIDER: str = "webspeech"
    TTS_PROVIDER: str = "webspeech"
    TTS_API_KEY: str = ""
    AVATAR_PROVIDER: str = "canvas"
    AVATAR_API_KEY: str = ""

    # Video & Speech Generation Providers
    VIDEO_ENGINE: str = "fast_local"  # "fast_local", "d_id", "heygen"
    D_ID_API_KEY: str = ""
    HEYGEN_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    VIDEO_FPS: int = 12
    VIDEO_MAX_SCENES: int = 5

    # Document Storage
    UPLOAD_DIR: str = "./storage/uploads"
    MAX_UPLOAD_SIZE_MB: int = 25

    # Self-Hosted Judge0 Code Execution
    JUDGE0_API_URL: str = "http://localhost:2358"
    MAX_CODE_SIZE_BYTES: int = 65536  # 64 KB max source code
    MAX_STDIN_SIZE_BYTES: int = 65536  # 64 KB max standard input
    MAX_OUTPUT_SIZE_BYTES: int = 131072  # 128 KB max output truncate limit
    CODE_EXECUTION_TIMEOUT_SECONDS: float = 15.0

    # YouTube Learning Video Recommendation
    YOUTUBE_API_KEY: str = ""

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )


settings = Settings()

# Ensure required directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs("./storage/videos", exist_ok=True)
