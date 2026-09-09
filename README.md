# EduMentor AI — Adaptive AI Teacher, Code Execution & Video Masterclass Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=black)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Judge0](https://img.shields.io/badge/Judge0-Self--Hosted-blue?logo=docker&logoColor=white)](docs/judge0_setup.md)
[![YouTube API](https://img.shields.io/badge/YouTube%20Data%20API-v3-red?logo=youtube&logoColor=white)](https://developers.google.com/youtube/v3)

**EduMentor AI** is a production-grade, full-stack adaptive AI teaching system engineered to emulate a master human mentor. Rather than functioning as a standard question-and-answer chatbot, EduMentor AI executes continuous pedagogical feedback and multi-modal learning loops:

$$\text{UNDERSTAND} \rightarrow \text{PLAN} \rightarrow \text{EXPLAIN} \rightarrow \text{DEMONSTRATE} \rightarrow \text{QUESTION} \rightarrow \text{EVALUATE} \rightarrow \text{ADAPT} \rightarrow \text{CONTINUE} \rightarrow \text{ASSESS} \rightarrow \text{REMEMBER}$$

---

## 🎯 Key Capabilities & Innovations

### 1. 💻 Multi-Language Sandboxed Code Execution (Self-Hosted Judge0)
- **Architecture**:
  $$\text{AI Agent} \rightarrow \text{execute\_code Tool} \rightarrow \text{CodeExecutionService} \rightarrow \text{Judge0Provider} \rightarrow \text{Self-Hosted Judge0}$$
- **Zero Paid Dependencies**: EduMentorAI uses a self-hosted Judge0 instance for code execution. **No Judge0 API key or paid Judge0 cloud account is required.**
- **Supported Languages**: Python, C, C++, Java, JavaScript (Node.js), TypeScript, C#, Go, Rust, Ruby, PHP, Swift, Kotlin, Bash, SQL, and dynamically discovered compilers via `GET /languages/`.
- **Dynamic Language Resolution**: Automatic alias normalization (`c++`, `cpp`, `py`, `python3`, `node`, `golang`, etc.) with active version preference.
- **Strict Sandboxed Security**: All code runs in external Linux sandbox containers. Arbitrary code is NEVER executed on the EduMentorAI backend host.

### 2. 📺 AI-Powered Duration-Aware YouTube Learning Video Recommendation
- **Architecture**:
  $$\text{AI Agent} \rightarrow \text{find\_learning\_video Tool} \rightarrow \text{YouTubeService} \rightarrow \text{YouTube Data API v3}$$
- **Exact Duration Awareness**: Parses exact ISO 8601 durations (`PT21M14S` $\rightarrow$ 21:14) and respects user time constraints:
  - `exact` / `around`: Scores candidates based on duration proximity (e.g. "recursion in 20 minutes").
  - `under`: Strictly rejects any video exceeding the limit (e.g. "under 20 minutes").
  - `minimum`: Strictly prioritizes videos satisfying the minimum duration (e.g. "60 minutes or more", "at least 1 hour").
  - `short`: Targets concise overviews (5–18 mins).
  - `detailed`: Prioritizes comprehensive in-depth masterclasses ($\ge$45–60 mins).
- **Intelligent Candidate Ranking**: Ranks candidates based on topic relevance, duration accuracy, view metrics, and educational signals. Returns **EXACTLY ONE** best verified video with a real YouTube URL and educational rationale.

### 3. 🎬 Real AI Teaching Video Generation Pipeline
- Synthesizes playable **H.264/AAC MP4 video files** directly from structured lessons.
- Scene-by-scene storyboard (Intro, Concept Explanation, Demonstration, Formative Check, Summary).
- High-resolution 1280x720 visual cards: LaTeX derivations, code cards, and process diagrams.
- Synchronized neural voice narration (EdgeTTS / gTTS / OpenAI TTS).

### 4. 🧠 Deterministic Multi-Stage Adaptation Engine
- Works for **ANY arbitrary subject** with zero hardcoded subject strings.
- 10 adaptive pedagogical actions: `CONTINUE`, `RETEACH`, `SIMPLIFY`, `GIVE_ANALOGY`, `GIVE_EXAMPLE`, `GIVE_VISUAL`, `EASIER_QUESTION`, `SIMILAR_QUESTION`, `HARDER_QUESTION`, `ASK_FOLLOWUP`.

### 5. 📚 True Hybrid RAG & Multi-Format Ingestion
- Combines **Dense Semantic Vector Search** with **Sparse BM25 Keyword Retrieval** via **Reciprocal Rank Fusion (RRF)**.
- Supports PDF, DOCX, PPTX, TXT, MD with scanned OCR fallback.

---

## 🚀 Quick Start (Local Development)

### 1. Start Self-Hosted Judge0 (Docker)
```bash
docker compose -f docker-compose.judge0.yml up -d
```
Verify Judge0 is running:
```bash
curl http://localhost:2358/system_info
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```env
GROQ_API_KEY="your_groq_api_key"
YOUTUBE_API_KEY="your_youtube_data_api_v3_key"
JUDGE0_API_URL="http://localhost:2358"
```
*(Note: `JUDGE0_API_KEY` is NOT required).*

### 3. Start Backend API Server
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```
- Interactive Swagger API Documentation: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- Judge0 Health Check: [http://localhost:8000/api/code/health](http://localhost:8000/api/code/health)

### 4. Start Frontend Client Application
```bash
cd frontend
npm install
npm run dev
```
- Client Web Application: [http://localhost:5173](http://localhost:5173)

### 5. Stop Judge0 Stack
```bash
docker compose -f docker-compose.judge0.yml down
```

---

## 🧪 Running Automated Tests

```bash
cd backend
python -m pytest -v
```

All test suites cover:
- Multi-language compilation and execution (Python, C, C++, Java, JS, Ruby)
- Compilation and runtime error diagnostics
- Stdin input streaming
- Duration-aware YouTube recommendation ranking (20-min around, 60-min minimum, under 20-min)
- Single verified video constraint and fallback handling
- Hybrid RAG Vector + BM25 keyword fusion
- Critical 17-step end-to-end pedagogical loop

---

## 📚 Documentation Index
- [`docs/judge0_setup.md`](docs/judge0_setup.md) — Comprehensive guide to self-hosting Judge0 via Docker.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — High-level, video pipeline, and hybrid RAG architecture.
- [`docs/API.md`](docs/API.md) — RESTful API endpoint specifications.
- [`docs/AI_ARCHITECTURE.md`](docs/AI_ARCHITECTURE.md) — Multi-agent state machine & adaptation engine.