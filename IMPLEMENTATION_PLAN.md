# IMPLEMENTATION_PLAN.md

# EduMentor AI — Adaptive AI Teacher

EduMentor AI is a full-stack, production-quality adaptive AI teaching system designed to emulate a master human teacher. Rather than functioning as a standard question-and-answer chatbot, EduMentor AI executes a continuous pedagogical feedback loop:

$$\text{UNDERSTAND} \rightarrow \text{PLAN} \rightarrow \text{EXPLAIN} \rightarrow \text{DEMONSTRATE} \rightarrow \text{QUESTION} \rightarrow \text{EVALUATE} \rightarrow \text{ADAPT} \rightarrow \text{CONTINUE} \rightarrow \text{ASSESS} \rightarrow \text{REMEMBER}$$

---

## 1. System Architecture

```
                                  AI TEACHER
                                      │
                           ┌──────────┴──────────┐
                           │                     │
                      KNOWLEDGE                 LEARNER
                           │                     │
                          RAG              PROFILE/MEMORY
                           │                     │
                           └──────────┬──────────┘
                                      ↓
                               LESSON PLANNER
                                      ↓
                                TEACHING AGENT
                                      ↓
                             ┌────────┴────────┐
                             ↓                 ↓
                          VISUALS            VOICE
                             ↓                 ↓
                             └────────┬────────┘
                                      ↓
                                   AVATAR
                                      ↓
                                 QUESTION
                                      ↓
                              STUDENT RESPONSE
                                      ↓
                                 EVALUATOR
                                      ↓
                             MISCONCEPTION AI
                                      ↓
                              ADAPTATION ENGINE
                                      ↓
                           ┌──────────┴──────────┐
                           ↓                     ↓
                        RE-TEACH              CONTINUE
                           │                     │
                           └──────────┬──────────┘
                                      ↓
                                  ASSESSMENT
                                      ↓
                                MASTERY MODEL
                                      ↓
                              STUDENT MEMORY
                                      ↓
                               NEXT LESSON
```

---

## 2. Technology Stack

### Frontend
- **Framework**: React + TypeScript + Vite
- **Routing**: React Router v6
- **State & Data**: TanStack Query (React Query)
- **Styling**: Modular Modern CSS with CSS Custom Properties, Clean Design System
- **Subject-Aware Visuals**:
  - KaTeX for LaTeX mathematical formulas & step-by-step derivations
  - Monaco Editor for programming lessons & code execution tracing
  - Recharts / Canvas for dynamic graphs & statistics
  - Mermaid.js & SVG for Flowcharts, Timelines, Physics Diagrams, Biology Structures
- **Interactive Avatar & Voice**:
  - Animated Canvas/SVG Teacher Avatar with lip-sync, expressive states (idle, talking, questioning, praising, encouraging)
  - Web Speech API + EdgeTTS / OpenAI TTS for natural voice narration
  - MediaRecorder + Whisper / Web Speech API for voice input

### Backend
- **Framework**: Python 3.12 + FastAPI
- **Data Validation**: Pydantic v2 (Strict schemas for all inputs and LLM structured outputs)
- **Database & ORM**: SQLAlchemy 2.0
  - Primary: PostgreSQL + pgvector
  - Fallback / Standalone: SQLite + local cosine similarity vector engine for zero-dependency local dev
- **Cache & Queues**: Redis + Background worker tasks for video generation & heavy document indexing
- **Security**: Passlib (Bcrypt) password hashing, PyJWT authentication, CORS middleware, strict input validation

### AI & Agents
- **LLM Provider Abstraction**:
  - OpenAI (GPT-4o, GPT-4o-mini)
  - Google Gemini (Gemini 2.0 Flash, Gemini 1.5 Pro)
  - Groq (Llama-3.3-70B)
  - Local / Mock Pedagogical Provider (offline development & automated tests)
- **Embedding Provider Abstraction**:
  - HuggingFace (bge-m3 / multilingual-e5)
  - OpenAI (text-embedding-3-small)
  - Local FastEmbed / Cosine provider
- **Specialized AI Agents**:
  1. Orchestrator Agent
  2. RAG Knowledge Agent
  3. Lesson Planner Agent (5m, 20m, 60m, 7-day)
  4. Teacher & Explanation Agent
  5. Evaluator Agent (Semantic answer evaluation)
  6. Misconception Diagnostician Agent
  7. Deterministic Adaptation Engine
  8. Subject-Aware Visual Planner
  9. Assessment Generator
  10. Curriculum & Recommendation Engine

---

## 3. Database Schema

1. **`users`**: id, name, email, password_hash, preferred_language, education_level, created_at, updated_at
2. **`learner_profiles`**: id, user_id, knowledge_level, learning_goal, preferred_depth, available_time, learning_style, strong_topics, weak_topics, current_learning_path_id, preferred_language
3. **`documents`**: id, user_id, filename, file_type, language, storage_path, processing_status, page_count, metadata, created_at
4. **`document_chunks`**: id, document_id, chunk_text, page_number, section_title, embedding, metadata
5. **`lessons`**: id, user_id, topic, document_id, language, difficulty, duration_minutes, objectives, status, current_step_index, created_at
6. **`lesson_steps`**: id, lesson_id, step_number, concept, explanation, example, visual_type, visual_data, question, expected_answer, difficulty, state
7. **`interactions`**: id, lesson_id, step_id, user_id, question, student_answer, evaluation, misconception, confidence, created_at
8. **`assessments`**: id, lesson_id, user_id, score, total_questions, strong_concepts, weak_concepts, recommendations, questions_data, created_at
9. **`learning_progress`**: id, user_id, topic, concept, mastery_score, attempts, correct_attempts, difficulty, last_studied
10. **`learning_paths`**: id, user_id, topic, nodes, current_node_id, status, created_at
11. **`video_jobs`**: id, lesson_id, status, scene_data, video_url, created_at, updated_at

---

## 4. Phase-by-Phase Execution Plan

- **Phase 1**: Foundation & Project Architecture (FastAPI backend, DB schema, JWT auth, React Vite frontend, Docker config, .env.example)
- **Phase 2**: Document Ingestion & Chunking (PDF, DOCX, PPTX, TXT, OCR, hierarchical chunking, vector embeddings)
- **Phase 3**: RAG Engine & Grounding (Hybrid retrieval, BM25, semantic search, reranking, source citation grounding)
- **Phase 4**: Teaching Brain (Learner profile, time-aware lesson planner [5m, 20m, 60m, 7-day], teaching state machine)
- **Phase 5**: Interactive Evaluation, Misconception Diagnosis & Adaptive Engine (Question engine, semantic evaluation, root cause misconception detection, deterministic adaptation policy)
- **Phase 6**: Assessment, Mastery Model & Learning Paths (Final quiz, 5-factor mastery model, recommendations, roadmaps)
- **Phase 7**: Subject-Aware Visual Engine (KaTeX math, Monaco editor code runner, Recharts dynamic graphs, Mermaid & SVG diagrams)
- **Phase 8**: Multimodal Voice Pipeline (STT mic input, TTS speech synthesis with fallback)
- **Phase 9**: Interactive AI Teacher Avatar & Video Job System (Animated Canvas avatar, lip-sync, scene-based composite video queue)
- **Phase 10**: Multilingual & Concept Preservation (English, Hindi, Hinglish, Bengali canonical translations)
- **Phase 11**: UI/UX Polish, Diagnostics & Complete Classroom Experience (Dashboard, Documents, Classroom, Diagnostics AI trace)
- **Phase 12**: Verification, Testing & Documentation (Backend unit tests, E2E critical scenario test, API/Architecture docs)
