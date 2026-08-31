# DEPLOYMENT.md — Deployment & Local Setup Guide

## 1. Quickstart (Standalone Local Development)

EduMentor AI is engineered for immediate zero-dependency execution out of the box.

### Prerequisites
- Python 3.12+
- Node.js 20+ and npm

### Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
API Documentation will be live at: `http://localhost:8000/api/docs`

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Client Application will be live at: `http://localhost:5173`

---

## 2. Production Docker Deployment

A complete multi-container orchestration is configured via `docker-compose.yml`:

```bash
# Start PostgreSQL (pgvector), Redis, FastAPI Backend, and Nginx Frontend
docker-compose up --build -d
```

### Services Map
- **Frontend (Nginx)**: `http://localhost:5173`
- **Backend (FastAPI)**: `http://localhost:8000`
- **PostgreSQL + pgvector**: `localhost:5432`
- **Redis Cache**: `localhost:6379`

---

## 3. Environment Configuration (`.env`)

```env
PROJECT_NAME="EduMentor AI — Adaptive AI Teacher"
API_V1_STR="/api"
SECRET_KEY="your-production-secret-key"
DATABASE_URL="postgresql://postgres:postgrespassword@localhost:5432/edumentordb"

# AI Providers: "mock", "openai", "gemini", "groq"
LLM_PROVIDER="gemini"
LLM_MODEL="gemini-2.0-flash"
LLM_API_KEY="your-gemini-api-key"

# Embeddings: "local", "openai"
EMBEDDING_PROVIDER="local"
EMBEDDING_DIM=384
```
