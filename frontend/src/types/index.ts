export interface User {
  id: string;
  name: string;
  email: string;
  preferred_language: string;
  education_level: string;
  created_at: string;
}

export interface LearnerProfile {
  id: string;
  user_id: string;
  knowledge_level: string;
  learning_goal: string;
  preferred_depth: string;
  available_time: number;
  learning_style: string;
  preferred_language: string;
  strong_topics: string[];
  weak_topics: string[];
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Question {
  id: string;
  type: string;
  prompt: string;
  options?: string[];
  correct_answer: string;
  explanation_guide?: string;
  difficulty: string;
}

export interface VisualData {
  type: string; // 'math' | 'code' | 'diagram' | 'graph' | 'physics_sim' | 'none'
  title?: string;
  data: Record<string, any>;
  caption?: string;
}

export interface LessonStep {
  id: string;
  lesson_id: string;
  step_number: number;
  concept: string;
  explanation: string;
  example?: string;
  analogy?: string;
  visual_type: string;
  visual_data: Record<string, any>;
  question: Question;
  expected_answer?: string;
  difficulty: string;
  state: string;
  created_at: string;
}

export interface Lesson {
  id: string;
  user_id: string;
  topic: string;
  document_id?: string;
  language: string;
  difficulty: string;
  duration_minutes: number;
  objectives: string[];
  status: string;
  current_step_index: number;
  state: string;
  lesson_metadata: {
    summary?: string;
    prerequisites?: string[];
    target_audience?: string;
  };
  steps: LessonStep[];
  created_at: string;
  updated_at: string;
}

export interface AnswerEvaluation {
  is_correct: boolean;
  score: number;
  confidence: number;
  feedback: string;
  missing_concepts: string[];
  reasoning_quality: string;
}

export interface MisconceptionResult {
  detected: boolean;
  root_cause?: string;
  misconception_title?: string;
  severity: string;
  pedagogical_analogy?: string;
  recommended_reteach_strategy?: string;
}

export interface AdaptiveDecision {
  action: string;
  rationale: string;
  next_question?: Question;
  remedial_explanation?: string;
  visual_override?: Record<string, any>;
  new_mastery_estimate: number;
}

export interface Interaction {
  id: string;
  lesson_id: string;
  step_id?: string;
  question: string;
  student_answer: string;
  evaluation: AnswerEvaluation;
  misconception: MisconceptionResult;
  adaptive_decision: AdaptiveDecision;
  confidence: number;
  current_mastery: number;
  created_at: string;
}

export interface AssessmentQuestion {
  id: string;
  concept: string;
  difficulty: string;
  type: string;
  prompt: string;
  options?: string[];
  correct_answer: string;
  explanation: string;
}

export interface RecommendationItem {
  type: string;
  topic: string;
  concept?: string;
  reason: string;
  suggested_difficulty: string;
  estimated_minutes: number;
}

export interface Assessment {
  id: string;
  lesson_id: string;
  user_id: string;
  score: number;
  total_questions: number;
  correct_count: number;
  strong_concepts: string[];
  weak_concepts: string[];
  misconceptions_summary: string[];
  recommendations: RecommendationItem[];
  questions_data: AssessmentQuestion[];
  student_responses: Array<{
    question_id: string;
    prompt: string;
    student_answer: string;
    correct_answer: string;
    is_correct: boolean;
    explanation: string;
  }>;
  created_at: string;
}

export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  language: string;
  processing_status: string;
  page_count: number;
  doc_metadata: Record<string, any>;
  created_at: string;
}

export interface ConceptMastery {
  topic: string;
  concept: string;
  mastery_score: number;
  attempts: number;
  correct_attempts: number;
  difficulty_level: string;
  last_studied: string;
}

export interface MasteryOverview {
  overall_mastery: number;
  total_topics_studied: number;
  total_concepts_learned: number;
  strong_topics: string[];
  weak_topics: string[];
  concept_details: ConceptMastery[];
}

export interface LearningPathNode {
  id: string;
  title: string;
  difficulty: string;
  status: string;
  progress: number;
}

export interface LearningPath {
  id: string;
  topic: string;
  description?: string;
  nodes: LearningPathNode[];
  current_node_id?: string;
  status: string;
  progress_percentage: number;
  created_at: string;
}
