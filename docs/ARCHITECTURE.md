# ARCHITECTURE.md — System Architecture & Design

## 1. High-Level Architecture Overview

EduMentor AI is an adaptive AI teaching system constructed as an intelligent feedback loop:
$$\text{UNDERSTAND} \rightarrow \text{PLAN} \rightarrow \text{EXPLAIN} \rightarrow \text{DEMONSTRATE} \rightarrow \text{QUESTION} \rightarrow \text{EVALUATE} \rightarrow \text{ADAPT} \rightarrow \text{CONTINUE} \rightarrow \text{ASSESS} \rightarrow \text{REMEMBER}$$

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

## 2. Frontend Layer (`/frontend`)
- **React 18 + Vite + TypeScript**: High performance, type-safe client application.
- **Client-Side Rendering Engines**:
  - **KaTeX**: LaTeX mathematical equation rendering & derivations.
  - **Monaco Editor**: Interactive programming editor with code simulation.
  - **Recharts**: Responsive mastery analytics & trajectory graphs.
  - **Interactive SVG**: Real-time Physics simulation (air track glider, vector forces).
- **Audio & Media**:
  - Web Speech API + EdgeTTS / OpenAI abstraction for bidirectional voice conversations.
  - Interactive Canvas animated AI Teacher avatar with dynamic phoneme lip-sync and mood expressions.

---

## 3. Backend Core & API Gateway (`/backend`)
- **FastAPI**: Async ASGI web framework with automatic OpenAPI documentation.
- **Pydantic v2 Validation**: Strict schemas for all request payloads, database responses, and LLM structured outputs.
- **SQLAlchemy 2.0 ORM**: Dual-support for PostgreSQL + pgvector and zero-dependency SQLite.
- **Teaching State Machine**: Explicit pedagogical lifecycle management.

---

## 4. AI Subsystem & Specialized Agents (`/backend/app/ai`)
1. **Orchestrator**: Manages state transitions and active context.
2. **RAG Agent**: Retrieves semantic knowledge with hybrid cosine similarity, metadata filtering, and strict grounding verification.
3. **Lesson Planner Agent**: Constructs time-aware (5m, 20m, 60m, 7d) curriculum blueprints tailored to learner persona.
4. **Teacher Agent**: Generates bite-sized concept explanations with canonical formulas and intuitive analogies.
5. **Evaluator Agent**: Evaluates student responses semantically (score 0.0–1.0, partial correctness, reasoning quality).
6. **Misconception Agent**: Diagnoses root cognitive errors and provides targeted analogies.
7. **Deterministic Adaptation Engine**: Enforces mathematical policy rules around LLM decisions.
8. **Mastery Model**: Multi-factor cognitive progress tracking.
