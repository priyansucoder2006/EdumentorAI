# AI_ARCHITECTURE.md — Multi-Agent & Pedagogical Intelligence

## 1. Pedagogical Directives & Agent Matrix

EduMentor AI replaces standard monolithic LLM prompting with a pipeline of specialized, cooperating agents:

| Agent Name | Primary Responsibility | Input Context | Output Schema |
|---|---|---|---|
| **Lesson Planner** | Designs time-aware structured curriculum | Topic, Level, Time (5/20/60m), RAG chunks | `LessonPlanLLMOutput` |
| **Teacher Agent** | Delivers bite-sized progressive concept explanations | Active Step, Canonical concept, Learner Level | Spoken narration & Analogy |
| **Evaluator Agent** | Evaluates student answers semantically | Concept, Question, Expected Answer, Student Answer | `AnswerEvaluationResult` |
| **Misconception Diagnostician** | Diagnoses underlying cognitive root causes | Student wrong answer, Correct principle | `MisconceptionResult` |
| **Adaptation Engine** | Enforces deterministic remediation & progression policy | Evaluator score, Misconception severity | `AdaptiveDecisionOutput` |
| **Visual Engine** | Synthesizes subject-aware visual instructions | Concept domain (Math, Physics, CS, Bio) | `VisualDataSchema` |
| **Assessment Generator** | Generates tailored post-lesson quiz | Concepts taught in current session | `AssessmentLLMOutput` |
| **Curriculum Recommender** | Suggests revision drills & next topics | Real-time Mastery, Diagnosed gaps | `List[RecommendationItem]` |

---

## 2. Deterministic Adaptation Engine

Rather than allowing unconstrained LLM hallucinations to determine student grading, EduMentor AI implements a deterministic policy state machine:

- **Score < 0.40 OR Severe Misconception Detected**:
  - Triggers remedial analogy contrasting faulty intuition with reality.
  - Automatically simplifies the concept and provides a formative follow-up challenge.
  - State = `reteach`.
- **0.40 <= Score < 0.70 (Partial Understanding)**:
  - Highlights exact missing conceptual elements.
  - Provides a reinforcing concrete demonstration tip.
  - State = `provide_analogy`.
- **Score >= 0.85 (High Mastery)**:
  - Praises student reasoning.
  - Advances to next progressive module or increases difficulty level.
  - State = `continue` / `increase_difficulty`.

---

## 3. Transparent Multi-Factor Mastery Model

$$\text{Mastery} = 100 \times \Big( 0.35 \times C + 0.25 \times K + 0.20 \times D + 0.10 \times R + 0.10 \times E \Big)$$

Where:
- $C$ = Correctness score of the interaction (0.0 to 1.0)
- $K$ = Consistency ratio ($\text{correct attempts} / \text{total attempts}$)
- $D$ = Concept difficulty multiplier ($\text{Beginner}=0.60, \text{Intermediate}=0.85, \text{Advanced}=1.00$)
- $R$ = Reasoning depth score ($\text{Poor}=0.25, \text{Partial}=0.55, \text{Good}=0.85, \text{Excellent}=1.00$)
- $E$ = Ebbinghaus retention decay factor ($1.0 - 0.03 \times \text{days}$)
