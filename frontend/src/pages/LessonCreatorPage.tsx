import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { lessonService } from '../services/lessonService';
import { documentService } from '../services/documentService';
import { DocumentItem } from '../types';
import {
  Sparkles,
  BookOpen,
  Clock,
  Globe,
  Award,
  Target,
  FileText,
  ArrowRight,
  CheckCircle2,
} from 'lucide-react';

export const LessonCreatorPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const stateData = (location.state as any) || {};

  const [topic, setTopic] = useState<string>(stateData.topic || "Newton's Laws of Motion");
  const [duration, setDuration] = useState<number>(stateData.duration_minutes || 20);
  const [language, setLanguage] = useState<string>('hinglish');
  const [difficulty, setDifficulty] = useState<string>('beginner');
  const [targetAudience, setTargetAudience] = useState<string>('Class 8 student');
  const [learningGoal, setLearningGoal] = useState<string>('mastery');
  const [selectedDocId, setSelectedDocId] = useState<string>(stateData.document_id || '');
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isPlanning, setIsPlanning] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    documentService.getDocuments().then(setDocuments).catch(console.warn);
  }, []);

  const handleCreateLesson = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setIsPlanning(true);
    setError(null);

    try {
      const lesson = await lessonService.createLesson({
        topic,
        document_id: selectedDocId || undefined,
        duration_minutes: duration,
        language,
        difficulty,
        target_audience: targetAudience,
        learning_goal: learningGoal,
      });

      // Navigate straight to classroom
      navigate(`/classroom/${lesson.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to design lesson plan.');
      setIsPlanning(false);
    }
  };

  const samplePresets = [
    { topic: "Newton's Laws of Motion", level: 'beginner', aud: 'Class 8 student', lang: 'hinglish', dur: 20 },
    { topic: 'React Components & State Management', level: 'intermediate', aud: 'Frontend Developer', lang: 'en', dur: 20 },
    { topic: "Ohm's Law & Electric Circuits", level: 'beginner', aud: 'High School Physics', lang: 'hi', dur: 5 },
    { topic: 'Machine Learning Fundamentals', level: 'intermediate', aud: 'CS Undergrad', lang: 'en', dur: 60 },
  ];

  return (
    <div className="creator-page-container">
      <div className="creator-card">
        <div className="creator-header">
          <div className="creator-badge">
            <Sparkles size={20} className="text-blue-400" />
          </div>
          <h2>Design Your Adaptive Lesson</h2>
          <p>The AI Curriculum Planner will synthesize a time-aware, level-tailored pedagogical sequence.</p>
        </div>

        {/* Quick Presets */}
        <div className="presets-strip">
          <span className="text-xs font-semibold text-slate-400">Popular Presets:</span>
          {samplePresets.map((p, idx) => (
            <button
              key={idx}
              type="button"
              className="preset-btn"
              onClick={() => {
                setTopic(p.topic);
                setDifficulty(p.level);
                setTargetAudience(p.aud);
                setLanguage(p.lang);
                setDuration(p.dur);
              }}
            >
              {p.topic} ({p.dur}m)
            </button>
          ))}
        </div>

        {error && <div className="auth-error-alert">{error}</div>}

        <form onSubmit={handleCreateLesson} className="creator-form">
          {/* Topic Input */}
          <div className="form-group">
            <label><BookOpen size={16} /> Topic or Concept</label>
            <input
              type="text"
              required
              className="form-input-lg"
              placeholder="e.g. Newton's Laws of Motion, Binary Search Trees, Photosynthesis"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
          </div>

          {/* Document Attachment (Optional) */}
          {documents.length > 0 && (
            <div className="form-group">
              <label><FileText size={16} /> Ground in Uploaded Document (Optional)</label>
              <select value={selectedDocId} onChange={(e) => setSelectedDocId(e.target.value)}>
                <option value="">No document (Use General AI Knowledge)</option>
                {documents.map((d) => (
                  <option key={d.id} value={d.id}>
                    📄 {d.filename} ({d.page_count} pages)
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Duration Selector */}
          <div className="form-group">
            <label><Clock size={16} /> Session Duration (Time-Aware Planner)</label>
            <div className="duration-pill-selector">
              {[
                { val: 5, label: '5 Mins', desc: 'Core intuition & 1 check' },
                { val: 20, label: '20 Mins', desc: 'Step derivations & mini-quiz' },
                { val: 60, label: '60 Mins', desc: 'Deep dive, visuals & practice' },
              ].map((d) => (
                <button
                  type="button"
                  key={d.val}
                  className={`duration-pill ${duration === d.val ? 'active' : ''}`}
                  onClick={() => setDuration(d.val)}
                >
                  <span className="pill-title">{d.label}</span>
                  <span className="pill-desc">{d.desc}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Language & Difficulty Row */}
          <div className="form-row-3">
            <div className="form-group">
              <label><Globe size={16} /> Language</label>
              <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                <option value="hinglish">Hinglish (Hindi + English)</option>
                <option value="en">English</option>
                <option value="hi">हिन्दी (Hindi)</option>
                <option value="bn">বাংলা (Bengali)</option>
              </select>
            </div>

            <div className="form-group">
              <label><Award size={16} /> Difficulty</label>
              <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
                <option value="beginner">Beginner (Foundations & Analogies)</option>
                <option value="intermediate">Intermediate (Applications & Math)</option>
                <option value="advanced">Advanced (Deep Rigor & Edge Cases)</option>
              </select>
            </div>

            <div className="form-group">
              <label><Target size={16} /> Target Persona</label>
              <input
                type="text"
                value={targetAudience}
                onChange={(e) => setTargetAudience(e.target.value)}
                placeholder="e.g. Class 8 student, Job Interview"
              />
            </div>
          </div>

          <button type="submit" className="btn-plan-start" disabled={isPlanning}>
            {isPlanning ? (
              <div className="flex items-center gap-2">
                <span className="spinner" />
                <span>Architecting Personalized Curriculum...</span>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <span>Begin Teaching Session</span>
                <ArrowRight size={18} />
              </div>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};
