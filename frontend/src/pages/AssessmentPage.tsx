import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { lessonService } from '../services/lessonService';
import { Assessment, AssessmentQuestion } from '../types';
import confetti from 'canvas-confetti';
import {
  Award,
  CheckCircle2,
  XCircle,
  Sparkles,
  ArrowRight,
  TrendingUp,
  AlertTriangle,
  RotateCcw,
  BookOpen,
} from 'lucide-react';

export const AssessmentPage: React.FC = () => {
  const { lessonId } = useParams<{ lessonId: string }>();
  const navigate = useNavigate();

  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [userAnswers, setUserAnswers] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [isCompleted, setIsCompleted] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (!lessonId) return;
    const initAssessment = async () => {
      try {
        const gen = await lessonService.generateAssessment(lessonId);
        setAssessment(gen);
      } catch (err) {
        console.error('Error loading assessment:', err);
      } finally {
        setLoading(false);
      }
    };
    initAssessment();
  }, [lessonId]);

  const handleSelectAnswer = (qId: string, answer: string) => {
    setUserAnswers((prev) => ({ ...prev, [qId]: answer }));
  };

  const handleSubmit = async () => {
    if (!assessment) return;
    setIsSubmitting(true);

    const answersPayload = Object.entries(userAnswers).map(([question_id, answer]) => ({
      question_id,
      answer,
    }));

    try {
      const result = await lessonService.submitAssessment(assessment.id, answersPayload);
      setAssessment(result);
      setIsCompleted(true);

      // Trigger Confetti Celebration if passed
      if (result.score >= 60) {
        confetti({
          particleCount: 100,
          spread: 70,
          origin: { y: 0.6 },
        });
      }
    } catch (err) {
      console.error('Assessment submit error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading || !assessment) {
    return (
      <div className="assessment-loading-screen">
        <span className="spinner-lg" />
        <h3>Synthesizing Comprehensive Lesson Assessment...</h3>
      </div>
    );
  }

  const questions: AssessmentQuestion[] = assessment.questions_data || [];

  return (
    <div className="assessment-page-container">
      {!isCompleted ? (
        /* Quiz Interface */
        <div className="assessment-quiz-card">
          <div className="quiz-header">
            <div className="quiz-badge">
              <Award size={20} className="text-blue-400" />
            </div>
            <h2>Final Mastery Assessment</h2>
            <p>Demonstrate your understanding across the concepts covered during this lesson.</p>
          </div>

          <div className="questions-stack">
            {questions.map((q, idx) => (
              <div key={q.id || idx} className="question-item-card">
                <div className="q-number-bar">
                  <span className="q-index">Question {idx + 1} of {questions.length}</span>
                  <span className="q-concept-tag">{q.concept}</span>
                </div>
                <h4 className="q-prompt">{q.prompt}</h4>

                {q.options && q.options.length > 0 ? (
                  <div className="q-options-grid">
                    {q.options.map((opt, optIdx) => {
                      const isSelected = userAnswers[q.id] === opt;
                      return (
                        <button
                          key={optIdx}
                          type="button"
                          className={`q-opt-btn ${isSelected ? 'selected' : ''}`}
                          onClick={() => handleSelectAnswer(q.id, opt)}
                        >
                          <span className="opt-letter">{String.fromCharCode(65 + optIdx)}</span>
                          <span className="opt-text">{opt}</span>
                        </button>
                      );
                    })}
                  </div>
                ) : (
                  <input
                    type="text"
                    className="q-text-input"
                    placeholder="Enter your concise answer..."
                    value={userAnswers[q.id] || ''}
                    onChange={(e) => handleSelectAnswer(q.id, e.target.value)}
                  />
                )}
              </div>
            ))}
          </div>

          <div className="quiz-submit-bar">
            <button
              className="btn-primary-large w-full"
              disabled={isSubmitting || Object.keys(userAnswers).length < questions.length}
              onClick={handleSubmit}
            >
              <Sparkles size={18} />
              <span>{isSubmitting ? 'Evaluating Assessment...' : 'Submit & Generate Mastery Report'}</span>
            </button>
          </div>
        </div>
      ) : (
        /* Post-Quiz Learning & Mastery Report */
        <div className="assessment-report-card animate-fade-in">
          <div className="report-hero">
            <div className="report-score-ring">
              <span className="score-number">{Math.round(assessment.score)}%</span>
              <span className="score-label">Mastery Score</span>
            </div>
            <div className="report-title-group">
              <h2>Lesson Completed! 🎉</h2>
              <p>
                You answered <strong>{assessment.correct_count}</strong> out of{' '}
                <strong>{assessment.total_questions}</strong> questions correctly.
              </p>
            </div>
          </div>

          {/* Concepts Breakdown Grid */}
          <div className="concept-breakdown-grid">
            {/* Strong Concepts */}
            <div className="breakdown-card strong">
              <div className="flex items-center gap-2 text-emerald-400 font-bold mb-2">
                <CheckCircle2 size={18} /> Mastered Concepts
              </div>
              {assessment.strong_concepts && assessment.strong_concepts.length > 0 ? (
                <ul className="concept-list">
                  {assessment.strong_concepts.map((c, i) => (
                    <li key={i} className="concept-pill strong">{c}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-slate-400">Keep practicing to achieve full mastery!</p>
              )}
            </div>

            {/* Weak Concepts */}
            <div className="breakdown-card weak">
              <div className="flex items-center gap-2 text-amber-400 font-bold mb-2">
                <AlertTriangle size={18} /> Areas for Revision
              </div>
              {assessment.weak_concepts && assessment.weak_concepts.length > 0 ? (
                <ul className="concept-list">
                  {assessment.weak_concepts.map((c, i) => (
                    <li key={i} className="concept-pill weak">{c}</li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-emerald-400">No weak areas detected! Excellent job.</p>
              )}
            </div>
          </div>

          {/* Targeted Curriculum Recommendations */}
          {assessment.recommendations && assessment.recommendations.length > 0 && (
            <div className="report-recommendations-section">
              <h3 className="section-title flex items-center gap-2">
                <Sparkles size={18} className="text-blue-400" /> Recommended Next Steps
              </h3>
              <div className="recommendations-cards-grid">
                {assessment.recommendations.map((rec, idx) => (
                  <div key={idx} className="rec-card">
                    <span className="rec-type-badge">{rec.type}</span>
                    <h4>{rec.topic}</h4>
                    <p>{rec.reason}</p>
                    <Link
                      to="/create-lesson"
                      state={{ topic: rec.topic, duration_minutes: rec.estimated_minutes }}
                      className="btn-primary btn-sm mt-3 inline-flex items-center gap-1"
                    >
                      <span>Start ({rec.estimated_minutes}m)</span>
                      <ArrowRight size={14} />
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="report-footer-actions">
            <Link to="/dashboard" className="btn-secondary">
              Back to Dashboard
            </Link>
            <Link to="/analytics" className="btn-primary">
              View Analytics & Retention →
            </Link>
          </div>
        </div>
      )}
    </div>
  );
};
