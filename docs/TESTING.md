# TESTING.md — Automated Test Suite & Verification Matrix

## 1. Automated Test Suite Overview

All unit, integration, and critical end-to-end scenario tests are located under `/backend/tests/`:

```bash
cd backend
python -m pytest tests/ -v
```

### Verified Test Cases
1. `test_auth.py::test_register_and_login` — User registration, profile initialization, password hashing, JWT creation & token authentication.
2. `test_documents.py::test_document_upload_and_rag` — Ingestion of multi-page text notes, structural parsing, vector embedding, and hybrid semantic retrieval.
3. `test_lesson_planner.py::test_lesson_planner_and_time_adaptation` — Validates duration scaling (5m single-check vs 20m multi-step derivation vs 60m comprehensive plan).
4. `test_evaluator.py::test_semantic_evaluation` — Semantic answer grading without rigid keyword matching.
5. `test_evaluator.py::test_misconception_diagnosis` — Root cause diagnosis of common scientific and technical misconceptions.
6. `test_evaluator.py::test_deterministic_adaptation_policy` — Verifies that low scores ($< 0.40$) mathematically trigger remedial analogies and simpler follow-up checks.
7. `test_evaluator.py::test_mastery_model_formula` — Validates the 5-factor normalized mastery formula.
8. `test_e2e_teaching_flow.py::test_critical_e2e_teaching_scenario` — Complete 17-step critical path loop from profile creation to wrong answer misconception remediation, difficulty adaptation, assessment, mastery calculation, and recommendation generation.

---

## 2. Frontend Production Verification

```bash
cd frontend
npm run build
```
Validates TypeScript typings, component exports, KaTeX CSS assets, Monaco Editor bundling, and asset minification.
