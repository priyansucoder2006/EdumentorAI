# ARCHITECTURE.md — System Architecture & Design

## 1. High-Level Architecture Overview

EduMentor AI is an adaptive AI teaching system constructed as an intelligent continuous pedagogical feedback loop:
$$\text{UNDERSTAND} \rightarrow \text{PLAN} \rightarrow \text{EXPLAIN} \rightarrow \text{DEMONSTRATE} \rightarrow \text{QUESTION} \rightarrow \text{EVALUATE} \rightarrow \text{ADAPT} \rightarrow \text{CONTINUE} \rightarrow \text{ASSESS} \rightarrow \text{REMEMBER}$$

```
                                  AI TEACHER
                                      │
                           ┌──────────┴──────────┐
                           │                     │
                      KNOWLEDGE                 LEARNER
                           │                     │
                    HYBRID RAG (VEC+BM25)  PROFILE/MEMORY
                           │                     │
                           └──────────┬──────────┘
                                      ↓
                                LESSON PLANNER
                                      ↓
                         ┌────────────┴────────────┐
                         ↓                         ↓
                   TEACH LIVE             GENERATE VIDEO
                         ↓                         ↓
                   TEACHING AGENT           SCENE PLANNER
                         │                         ↓
                  ┌──────┴──────┐           VISUAL RENDERER
                  ↓             ↓                  ↓
               VISUALS        VOICE          TTS AUDIO SYNTH
                  ↓             ↓                  ↓
                  └──────┬──────┘           AVATAR ANIMATOR
                         ↓                         ↓
                      AVATAR                VIDEO COMPOSITOR
                         ↓                         ↓
                      QUESTION                 ACTUAL MP4
                         ↓
                  STUDENT RESPONSE
                         ↓
                     EVALUATOR
                         ↓
                 MISCONCEPTION AI
                         ↓
                 ADAPTATION ENGINE
                         ↓
               ┌─────────┴─────────┐
               ↓                   ↓
            RE-TEACH            CONTINUE
               │                   │
               └─────────┬─────────┘
                         ↓
                     ASSESSMENT
                         ↓
                   MASTERY MODEL
                         ↓
                  STUDENT MEMORY
                         ↓
               DYNAMIC RECOMMENDATIONS
                         ↓
                    NEXT LESSON
```

---

## 2. Real AI Teaching Video Pipeline (`/backend/app/services/video`)

The video engine creates standard H.264/AAC MP4 masterclasses from structured lessons:

1. **Scene Planner (`scene_planner.py`)**: Breaks arbitrary lessons into pedagogical scene sequences:
   - `INTRO`: Topic overview, learning objectives, target persona.
   - `CONCEPT_EXPLANATION`: Core concept breakdown and step derivations.
   - `DEMONSTRATION`: Real-world intuitive analogies and applied examples.
   - `FORMATIVE_CHECK`: Diagnostic checkpoint questions.
   - `SUMMARY`: Concept mastery celebration and personalized next steps.
2. **Visual Renderer (`visual_renderer.py`)**: Generates 1280x720 graphic cards:
   - Mathematical LaTeX/KaTeX equation derivations.
   - Syntax-colored code cards with line numbers and execution outputs.
   - Interactive process diagrams and flowcharts with glowing state nodes.
   - Conceptual bullet cards and analogy callouts.
   - Bottom subtitle narration banner with animated typed text.
3. **TTS Renderer (`tts_renderer.py`)**: High-definition neural voice synthesis per scene using EdgeTTS / gTTS with exact audio timing measurements.
4. **Avatar Renderer (`avatar_renderer.py`)**: Picture-in-Picture animated AI Teacher avatar with natural eye blinking, speech lip-sync mouth oscillation, audio waveform indicators, and emotion-responsive mood states (`Explaining`, `Questioning`, `Praising`, `Remedial Coaching`).
5. **Video Compositor (`video_compositor.py`)**: Assembles frame sequences at 12–24 FPS, muxes audio narration tracks synchronously using FFmpeg, and writes a valid, playable `.mp4` file to `./storage/videos/`.
6. **Video Pipeline Coordinator (`pipeline.py`)**: High-level async orchestrator reporting granular real-time progress (`0%` -> `100%`).

---

## 3. Real Text-to-Speech & Speech-to-Text (`/backend/app/services/voice`)

- **Pluggable STT Architecture (`stt_provider.py`)**:
  - `SpeechToTextProvider` base interface.
  - `OpenAIWhisperSTTProvider`: OpenAI / Groq Whisper speech transcription.
  - `LocalBrowserFallbackSTTProvider`: Client WebSpeech fallback.
- **Pluggable TTS Architecture (`tts_provider.py`)**:
  - `TextToSpeechProvider` base interface.
  - `EdgeTTSProvider`: High-quality neural voices (`en-US-JennyNeural`, `hi-IN-SwaraNeural`, `hi-IN-MadhurNeural`, `bn-IN-TanishaaNeural`).
  - `GTTSProvider`: Google Text-to-Speech fallback.
  - `OpenAITTSProvider`: OpenAI `tts-1` / `tts-1-hd`.
- REST API Endpoints: `/api/voice/transcribe`, `/api/voice/synthesize`, `/api/voice/config`.

---

## 4. True Hybrid RAG & Document Processing (`/backend/app/services`)

- **Dense Semantic Vector Search**: High-dimensional embeddings with cosine similarity.
- **Sparse BM25 Keyword Search (`hybrid_retriever.py`)**: Term frequency (TF), inverse document frequency (IDF), and document length normalization.
- **Reciprocal Rank Fusion (RRF)**: Combines dense vector and sparse keyword score ranks:
  $$\text{RRF\_Score}(d) = \frac{\alpha}{60 + \text{rank}_{\text{dense}}(d)} + \frac{1 - \alpha}{60 + \text{rank}_{\text{bm25}}(d)}$$
- **Document Ingestion (`document_ingestion.py`)**:
  - Supports: PDF, DOCX, PPTX, TXT, MD.
  - Scanned PDF detection: Identifies low text-density pages and triggers OCR fallback.
  - Slide & Page Metadata: Preserves exact slide/page numbers and section headings.
  - Legacy `.doc` rejection: Gracefully rejects legacy binary OLE `.doc` files with clear instructions to save as `.docx` or `.pdf`.

---

## 5. Multilingual Localization with Formula Shielding (`/backend/app/services/language_adapter.py`)

- Supports: **English**, **Hindi**, **Hinglish**, and **Bengali**.
- **Formula & Code Shielding**: Automatically tokenizes and protects mathematical formulas ($F=ma$, $E=mc^2$), LaTeX expressions, and code snippets (`function calculate()`) from corrupted translations during language switching.
- **Zero Hardcoding**: Dynamically translates arbitrary subjects while preserving lesson step index, mastery scores, and diagnostic state.

---

## 6. Deterministic Adaptive Teaching Policy (`/backend/app/services/adaptation_engine.py`)

Deterministic rules wrapping LLM evaluations across arbitrary topics:
- **Low Mastery ($\text{Score} < 40\%$) or Severe Misconception**:
  - Actions: `RETEACH`, `SIMPLIFY`, `GIVE_ANALOGY` + `EASIER_QUESTION`.
  - Generates targeted intuition analogy and root-cause remediation.
- **Partial Mastery ($40\% \le \text{Score} < 70\%$)**:
  - Actions: `GIVE_EXAMPLE`, `SIMILAR_QUESTION`, `ASK_FOLLOWUP`.
  - Clarifies missing subtleties and reinforces with concrete application example.
- **Mastery Satisfied ($70\% \le \text{Score} < 85\%$)**:
  - Action: `CONTINUE`.
- **High Proficiency ($\text{Score} \ge 85\%$)**:
  - Actions: `INCREASE_DIFFICULTY`, `HARDER_QUESTION`, `MASTERY_ACHIEVED`.

---

## 7. Dynamic Recommendations & Learning Paths

- **Recommender Agent (`recommender_agent.py`)**: Dynamically generates `NEXT_TOPIC`, `REVISION_TOPIC`, `PRACTICE_PROBLEM`, and `ADVANCED_TOPIC` based on weak concepts, prerequisites, and learner goals for ANY subject.
- **Dynamic Learning Paths (`progress.py`)**: Sequentially generates 5-stage curriculum node graphs for broad topics with live progress tracking.

---

## 8. Frontend Architecture (`/frontend`)

- **React 18 + TypeScript + Vite**: Single-page application with modular component hierarchy.
- **Classroom Stage (`ClassroomPage.tsx`)**:
  - Dual Mode: **Teach Live** vs **Generate Teaching Video**.
  - Visible Pedagogical States: `EXPLAINING`, `DEMONSTRATING`, `CHECKING_UNDERSTANDING`, `EVALUATING`, `DIAGNOSING`, `RE_TEACHING`, `INCREASING_DIFFICULTY`, `MASTERY_ACHIEVED`.
  - Subject-Aware Visual Board (`VisualBoard.tsx`) with MathRenderer, CodeRunner, GraphRenderer, DiagramRenderer, PhysicsSim.
  - Video Player Modal (`VideoPlayerModal.tsx`) with live progress tracker and HTML5 MP4 video player.
