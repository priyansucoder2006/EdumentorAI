# DATABASE.md — Relational Schema & Storage

## 1. Relational Entities & Data Dictionary

### `users`
- `id` (UUID PK): Unique student identifier.
- `name` (VARCHAR): Student full name.
- `email` (VARCHAR UNIQUE): Email credential.
- `password_hash` (VARCHAR): Bcrypt salted password hash.
- `preferred_language` (VARCHAR): Default language (`en`, `hinglish`, `hi`, `bn`).
- `education_level` (VARCHAR): Academic tier (`beginner`, `intermediate`, `advanced`).
- `created_at`, `updated_at` (TIMESTAMP).

### `learner_profiles`
- `id` (UUID PK)
- `user_id` (UUID FK -> users.id, ON DELETE CASCADE)
- `knowledge_level` (VARCHAR): `beginner`, `intermediate`, `advanced`.
- `learning_goal` (VARCHAR): `school_exam`, `mastery`, `interview_prep`.
- `preferred_depth` (VARCHAR): `intuitive`, `balanced`, `rigorous`.
- `available_time` (INTEGER): Default minutes (5, 20, 60).
- `strong_topics` (JSON): List of mastered concepts (mastery $\ge 75\%$).
- `weak_topics` (JSON): List of concepts needing remediation (mastery $< 50\%$).

### `documents` & `document_chunks`
- `documents`: Stores file metadata (`id`, `user_id`, `filename`, `file_type`, `storage_path`, `page_count`, `processing_status`).
- `document_chunks`: Stores atomic chunks (`id`, `document_id`, `chunk_text`, `page_number`, `section_title`, `embedding`, `chunk_metadata`).

### `lessons` & `lesson_steps`
- `lessons`: Stores session configuration (`id`, `user_id`, `topic`, `document_id`, `language`, `difficulty`, `duration_minutes`, `status`, `current_step_index`, `state`).
- `lesson_steps`: Stores sequential concept nodes (`id`, `lesson_id`, `step_number`, `concept`, `explanation`, `example`, `analogy`, `visual_type`, `visual_data`, `question`, `expected_answer`, `state`).

### `interactions`
- `id` (UUID PK)
- `lesson_id`, `step_id`, `user_id` (FKs)
- `question` (TEXT): Prompt presented to student.
- `student_answer` (TEXT): Response submitted by student.
- `evaluation` (JSON): `{is_correct, score, confidence, feedback, missing_concepts, reasoning_quality}`.
- `misconception` (JSON): `{detected, root_cause, analogy, severity}`.
- `adaptive_decision` (VARCHAR): Action decided by deterministic engine (`continue`, `reteach`, `provide_analogy`, `increase_difficulty`).

### `assessments`
- `id` (UUID PK), `lesson_id`, `user_id`
- `score` (FLOAT 0–100): Composite percentage score.
- `correct_count`, `total_questions` (INTEGER)
- `strong_concepts`, `weak_concepts`, `recommendations`, `questions_data`, `student_responses` (JSON).

### `learning_progress`
- `id` (UUID PK), `user_id`, `topic`, `concept`, `mastery_score` (FLOAT), `attempts`, `correct_attempts`, `difficulty_level`, `last_studied`.

### `learning_paths`
- `id` (UUID PK), `user_id`, `topic`, `nodes` (JSON DAG), `current_node_id`, `progress_percentage`.

### `video_jobs`
- `id` (UUID PK), `lesson_id`, `user_id`, `status` (`queued`, `processing`, `rendering`, `completed`), `scenes_data`, `video_url`.
