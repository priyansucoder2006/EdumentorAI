# API.md — RESTful API Specification

Base URL: `http://localhost:8000/api`

---

## 1. Authentication & Profile
- `POST /auth/register` — Register a new student account and create learner profile.
- `POST /auth/login` — Authenticate and receive JWT bearer token.
- `POST /auth/logout` — Invalidate session.
- `GET /auth/me` — Retrieve current authenticated user record.
- `GET /auth/profile` — Retrieve detailed learner profile (level, goal, weak topics).
- `PUT /auth/profile` — Update learner goals, knowledge level, and language preference.

---

## 2. Documents & RAG
- `POST /documents/upload` — Multipart file upload (PDF, DOCX, PPTX, TXT) with automatic chunking.
- `GET /documents` — List uploaded documents and indexing status.
- `GET /documents/{id}` — Get document details and chunk previews.
- `DELETE /documents/{id}` — Delete document and remove vector chunks.
- `POST /rag/query` — Test hybrid semantic search across uploaded notes.

---

## 3. Lessons & State Machine
- `POST /lessons` — Plan and initialize a structured lesson from topic or document.
- `GET /lessons` — List student lesson history.
- `GET /lessons/{id}` — Get active lesson steps and metadata.
- `POST /lessons/{id}/state` — Advance step (`next_step`) or transition state.
- `POST /lessons/{id}/language` — Switch lesson language (`en`, `hinglish`, `hi`, `bn`) with state preservation.

---

## 4. Interactions & Evaluation
- `POST /interactions/answer` — Submit answer for formative check; executes semantic evaluation, misconception diagnosis, deterministic adaptation, and mastery updates.
- `GET /interactions/{lesson_id}` — Get interaction history for a lesson.

---

## 5. Assessments & Progress
- `POST /assessments/generate` — Synthesize post-lesson mastery quiz.
- `POST /assessments/{id}/submit` — Grade assessment, calculate final score, and generate recommendations.
- `GET /assessments/{id}` — Get assessment summary report.
- `GET /progress` — Get composite mastery overview, strong topics, and concept details.
- `GET /progress/paths` — Get curriculum roadmap nodes.
- `GET /recommendations` — Get personalized next topics and revision recommendations.

---

## 6. Video Jobs & Diagnostics
- `POST /videos/generate` — Queue multi-scene video generation job.
- `GET /videos/{id}` — Get video job status.
- `GET /diagnostics/system` — System telemetry and health.
- `GET /diagnostics/ai-trace` — Developer AI trace inspector.
