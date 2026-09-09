# EduMentor AI — Adaptive AI Teacher, Code Execution & Video Masterclass Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=black)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Judge0](https://img.shields.io/badge/Judge0-Self--Hosted-blue?logo=docker&logoColor=white)](docs/judge0_setup.md)
[![YouTube API](https://img.shields.io/badge/YouTube%20Data%20API-v3-red?logo=youtube&logoColor=white)](https://developers.google.com/youtube/v3)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**EduMentor AI** is a production-grade, full-stack adaptive AI teaching system engineered to emulate a master human mentor. Rather than functioning as a standard question-and-answer chatbot, EduMentor AI executes continuous pedagogical feedback, sandboxed multi-language code compilation, AI video synthesis, and multi-modal learning loops:

> `UNDERSTAND` ➔ `PLAN` ➔ `EXPLAIN` ➔ `DEMONSTRATE` ➔ `QUESTION` ➔ `EVALUATE` ➔ `ADAPT` ➔ `CONTINUE` ➔ `ASSESS` ➔ `REMEMBER`

---

## 🌐 Live Deployment & Demo Links

| Service | Live URL | Description |
| :--- | :--- | :--- |
| 🚀 **Frontend Web Application** | [https://edumentor-frontend-fzvv.onrender.com](https://edumentor-frontend-fzvv.onrender.com) | React 18 + Vite + Tailwind CSS interactive student classroom |
| ⚡ **Backend REST API** | [https://edumentor-backend-ma4l.onrender.com](https://edumentor-backend-ma4l.onrender.com) | FastAPI backend service with AI agent orchestration |

### 🔑 Instant Demo Account (For Evaluation)
Judges and evaluators can log in immediately with the pre-seeded account or click the **"Quick Demo Account"** button on the login screen:
- **Email:** `student@edumentor.ai`
- **Password:** `password123`

---

## 🎯 Key Capabilities & Innovations

### 1. 👩‍🏫 Adaptive AI Master Teacher (Prof. Elena) & Live Doubt Clearing
- **Dynamic Dialogue & Audio Speech**: Employs real-time lip-synced canvas avatar animations with synchronized Web Speech / Neural TTS voice synthesis.
- **Contextual Answer Evaluation**: Replaces generic canned praise with semantic, concept-specific evaluation feedback analyzing the student's exact reasoning.
- **Live Doubt-Clearing Hub**: Students can ask questions directly about any concept during the lesson via `POST /api/interactions/ask` and receive immediate intuitive analogies and explanations.
- **Multilingual Delivery**: Supports on-the-fly language switching (English, Hinglish, Hindi, Bengali, Spanish, etc.) across the full curriculum.

### 2. 💻 Multi-Language Sandboxed Code Execution (Self-Hosted Judge0)
- **Architecture Flow**:
  > `AI Agent` ➔ `execute_code Tool` ➔ `CodeExecutionService` ➔ `Judge0Provider` ➔ `Self-Hosted Judge0`
- **Zero Paid Dependencies**: EduMentor AI uses a self-hosted Judge0 instance for code execution. **No Judge0 API key or paid Judge0 cloud account is required.**
- **Supported Languages**: Python, C, C++, Java, JavaScript (Node.js), TypeScript, C#, Go, Rust, Ruby, PHP, Swift, Kotlin, Bash, SQL, and dynamically discovered compilers via `GET /api/code/languages`.
- **Dynamic Language Resolution**: Automatic alias normalization (`c++`, `cpp`, `py`, `python3`, `node`, `golang`, etc.) with active compiler version preference.
- **Strict Sandboxed Security**: All code runs in external Linux sandbox containers. Arbitrary code is NEVER executed on the EduMentor AI backend host.

### 3. 📺 AI-Powered Duration-Aware YouTube Learning Video Recommendation
- **Architecture Flow**:
  > `AI Agent` ➔ `find_learning_video Tool` ➔ `YouTubeService` ➔ `YouTube Data API v3`
- **Exact Duration Awareness**: Parses exact ISO 8601 durations (`PT21M14S` $\rightarrow$ 21:14) and respects student time constraints:
  - `exact` / `around`: Scores candidates based on duration proximity (e.g., "recursion in 20 minutes").
  - `under`: Strictly rejects any video exceeding the limit (e.g., "under 20 minutes").
  - `minimum`: Strictly prioritizes videos satisfying the minimum duration (e.g., "60 minutes or more", "at least 1 hour").
  - `short`: Targets concise overviews (5–18 mins).
  - `detailed`: Prioritizes comprehensive in-depth masterclasses ($\ge$45–60 mins).
- **Intelligent Candidate Ranking**: Ranks candidates based on topic relevance, duration accuracy, view metrics, and educational signals. Returns **EXACTLY ONE** best verified video with a real YouTube URL and pedagogical rationale.

### 4. 🎬 Real AI Teaching Video Generation Pipeline
- Synthesizes playable **H.264/AAC MP4 video files** directly from structured lessons.
- Scene-by-scene storyboard (Intro, Concept Explanation, Demonstration, Formative Check, Summary).
- High-resolution 1280x720 visual cards: LaTeX derivations, code cards, and process diagrams.
- Synchronized neural voice narration (EdgeTTS / gTTS / OpenAI TTS) with asynchronous progress reporting.

### 5. 🧠 Deterministic Multi-Stage Adaptation Engine
- Works for **ANY arbitrary subject** with zero hardcoded subject strings.
- 10 adaptive pedagogical actions: `CONTINUE`, `RETEACH`, `SIMPLIFY`, `GIVE_ANALOGY`, `GIVE_EXAMPLE`, `GIVE_VISUAL`, `EASIER_QUESTION`, `SIMILAR_QUESTION`, `HARDER_QUESTION`, `ASK_FOLLOWUP`.
- Fine-grained misconception diagnostic agent identifying root causes and prescribing intuitive analogies.

### 6. 📚 True Hybrid RAG & Multi-Format Ingestion
- Combines **Dense Semantic Vector Search** (BGE-M3 / OpenAI embeddings) with **Sparse BM25 Keyword Retrieval** via **Reciprocal Rank Fusion (RRF)**.
- Supports PDF, DOCX, PPTX, TXT, MD with scanned OCR fallback for textbook grounding and lesson citation.

---

## 🏛️ System Architecture

```
                                  +-----------------------------+
                                  |     React 18 + Vite UI      |
                                  | (Classroom, Code, Video, RAG)|
                                  +--------------+--------------+
                                                 |
                                     HTTP REST / JSON / JWT
                                                 |
                                  +--------------v--------------+
                                  |    FastAPI Backend Server   |
                                  +--------------+--------------+
                                                 |
       +--------------------+--------------------+--------------------+--------------------+
       |                    |                    |                    |                    |
+------v------+      +------v------+      +------v------+      +------v------+      +------v------+
|  AI Agents  |      |   Judge0    |      |   YouTube   |      |  MP4 Video  |      | Hybrid RAG  |
|  Orchestrator|     | Code Sandbox|      | Recommender |      | Synthesizer |      | Vector+BM25 |
| (Groq / LLM)|      | (Port 2358) |      | (Data API v3|      | (FFmpeg+TTS)|      | (Documents) |
+-------------+      +-------------+      +-------------+      +-------------+      +-------------+
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- **Python:** 3.11 or 3.12
- **Node.js:** v18+ (v20+ recommended)
- **Docker & Docker Compose** (Optional, for self-hosted Judge0 code execution)
- **FFmpeg** (Optional, for MP4 video generation)

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/rohancoder19/EduMentorAI.git
cd EduMentorAI
```

---

### Step 2: Set Up Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Configure your environment variables in `.env`:
```env
# Project Core
PROJECT_NAME="EduMentor AI — Adaptive AI Teacher"
DEBUG=true
SECRET_KEY="your-super-secure-jwt-secret-key"

# Database
DATABASE_URL="sqlite:///./edumentor.db"

# LLM Providers (Groq is recommended for ultra-fast response times)
LLM_PROVIDER="groq"
LLM_MODEL="openai/gpt-oss-20b"
GROQ_API_KEY="your_groq_api_key_here"

# Self-Hosted Judge0 (Docker)
JUDGE0_API_URL="http://localhost:2358"

# YouTube Data API v3 (For video recommendations)
YOUTUBE_API_KEY="your_youtube_data_api_v3_key_here"
```
*(Note: A Judge0 API key is **NOT** required for the self-hosted instance).*

---

### Step 3: (Optional) Start Self-Hosted Judge0 (Docker)
To enable sandboxed multi-language code execution:
```bash
docker compose -f docker-compose.judge0.yml up -d
```
Verify Judge0 is healthy:
```bash
curl http://localhost:2358/system_info
```

---

### Step 4: Start Backend API Server
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
- Interactive Swagger API Documentation: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- Code Execution Health Check: [http://localhost:8000/api/code/health](http://localhost:8000/api/code/health)

---

### Step 5: Start Frontend Client Application
Open a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
- Client Web Application: [http://localhost:5173](http://localhost:5173)

Log in using the pre-seeded demo credentials or click **Quick Demo Account**!

---

## 🧪 Running Automated Tests

The test suite covers the complete teaching flow, code execution sandbox, duration-aware YouTube ranking, video pipeline, and multi-tenant isolation:

```bash
cd backend
python -m pytest -v
```

### Test Suite Coverage
| Test Module | Coverage Area |
| :--- | :--- |
| `test_code_execution.py` | Multi-language compilation (Python, C, C++, Java, JS, Ruby), stdin streaming, runtime error handling |
| `test_youtube_recommendation.py` | Exact duration scoring, under/over limit constraints, single verified video return |
| `test_video_pipeline.py` | Storyboard creation, audio-video muxing, background worker status handling |
| `test_hybrid_rag_and_ocr.py` | Dense vector + BM25 sparse retrieval fusion, document chunking |
| `test_e2e_teaching_flow.py` | Critical 17-step end-to-end adaptive pedagogical loop |
| `test_user_isolation.py` | Multi-tenant security, profile and progress isolation |
| `test_auth.py` | JWT issuance, password hashing, route protection |

---

## 📁 Repository Structure

```
EduMentorAI/
├── backend/
│   ├── app/
│   │   ├── ai/               # AI Agents (Planner, Evaluator, Misconception, Recommender)
│   │   ├── api/v1/           # REST API endpoints (auth, lessons, interactions, code, videos)
│   │   ├── core/             # Database, config, security, logging
│   │   ├── models/           # SQLAlchemy database models
│   │   ├── schemas/          # Pydantic validation schemas
│   │   └── services/         # Adaptation engine, Judge0 execution, RAG, video compositor
│   ├── tests/                # Automated pytest test suites
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile.backend    # Backend container definition
├── frontend/
│   ├── src/
│   │   ├── components/       # UI components (AvatarTeacher, VisualBoard, QuestionEngine)
│   │   ├── pages/            # Views (Classroom, Dashboard, Sandbox, Analytics, Documents)
│   │   └── services/         # API client layer & Web Speech voice manager
│   ├── package.json          # Node dependencies & build scripts
│   └── vite.config.ts        # Vite build configuration
├── docs/                     # Architectural documentation & Judge0 setup guide
├── docker-compose.judge0.yml # Self-hosted Judge0 Docker orchestration
├── render.yaml               # Render Cloud deployment blueprint
└── README.md                 # Project documentation
```

---

## 📚 Documentation Index
- [`docs/judge0_setup.md`](docs/judge0_setup.md) — Comprehensive guide to self-hosting Judge0 via Docker.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — High-level system architecture & data flows.
- [`docs/API.md`](docs/API.md) — Complete RESTful API endpoint specifications.
- [`docs/AI_ARCHITECTURE.md`](docs/AI_ARCHITECTURE.md) — Multi-agent state machine & deterministic adaptation engine.

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.