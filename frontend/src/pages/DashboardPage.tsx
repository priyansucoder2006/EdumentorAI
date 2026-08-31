import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { progressService } from '../services/progressService';
import { lessonService } from '../services/lessonService';
import { MasteryOverview, Lesson, RecommendationItem } from '../types';
import {
  Sparkles,
  BookOpen,
  Award,
  Clock,
  ArrowRight,
  TrendingUp,
  AlertTriangle,
  Play,
  CheckCircle2,
  FolderOpen,
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { user, profile } = useAuth();
  const navigate = useNavigate();

  const [mastery, setMastery] = useState<MasteryOverview | null>(null);
  const [recentLessons, setRecentLessons] = useState<Lesson[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [quickTopic, setQuickTopic] = useState('');
  const [quickTime, setQuickTime] = useState<number>(20);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        const [m, l, r] = await Promise.all([
          progressService.getMasteryOverview(),
          lessonService.getLessons(),
          progressService.getRecommendations(),
        ]);
        setMastery(m);
        setRecentLessons(l);
        setRecommendations(r);
      } catch (err) {
        console.warn('Dashboard load error:', err);
      } finally {
        setLoading(false);
      }
    };
    loadDashboardData();
  }, []);

  const handleQuickLaunch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickTopic.trim()) return;
    navigate('/create-lesson', {
      state: { topic: quickTopic, duration_minutes: quickTime },
    });
  };

  const activeLesson = recentLessons.find((l) => l.status === 'in_progress') || recentLessons[0];

  return (
    <div className="dashboard-page-container">
      {/* Welcome Banner */}
      <section className="dashboard-welcome-hero">
        <div className="welcome-content">
          <div className="flex items-center gap-2 text-blue-300 font-semibold text-sm mb-1">
            <Sparkles size={16} /> Adaptive Learning Center
          </div>
          <h1>Namaste, {user?.name || 'Learner'}! 👋</h1>
          <p>
            Your AI teacher is ready. Teaching level calibrated to{' '}
            <strong>{profile?.knowledge_level || 'Beginner'}</strong> in{' '}
            <strong>{user?.preferred_language?.toUpperCase() || 'HINGLISH'}</strong>.
          </p>

          {/* Quick Launch Search */}
          <form onSubmit={handleQuickLaunch} className="quick-launch-form">
            <input
              type="text"
              placeholder="What would you like to master today? (e.g. Newton's Laws, React Hooks, Ohm's Law)"
              value={quickTopic}
              onChange={(e) => setQuickTopic(e.target.value)}
              className="quick-topic-input"
            />
            <select
              value={quickTime}
              onChange={(e) => setQuickTime(parseInt(e.target.value))}
              className="quick-time-select"
            >
              <option value={5}>5 min (Speed Concept)</option>
              <option value={20}>20 min (Deep Mastery)</option>
              <option value={60}>60 min (Masterclass)</option>
            </select>
            <button type="submit" className="btn-launch-lesson">
              <span>Teach Me</span>
              <ArrowRight size={16} />
            </button>
          </form>
        </div>
      </section>

      {/* Metrics Row */}
      <div className="dashboard-metrics-grid">
        <div className="metric-stat-card">
          <div className="metric-icon-box bg-blue-500/10 text-blue-400">
            <Award size={24} />
          </div>
          <div className="metric-info">
            <span className="metric-label">Overall Concept Mastery</span>
            <span className="metric-value">{mastery?.overall_mastery || 78}%</span>
          </div>
        </div>

        <div className="metric-stat-card">
          <div className="metric-icon-box bg-emerald-500/10 text-emerald-400">
            <BookOpen size={24} />
          </div>
          <div className="metric-info">
            <span className="metric-label">Topics Mastered</span>
            <span className="metric-value">{mastery?.total_topics_studied || 3}</span>
          </div>
        </div>

        <div className="metric-stat-card">
          <div className="metric-icon-box bg-purple-500/10 text-purple-400">
            <TrendingUp size={24} />
          </div>
          <div className="metric-info">
            <span className="metric-label">Concepts Learned</span>
            <span className="metric-value">{mastery?.total_concepts_learned || 8}</span>
          </div>
        </div>
      </div>

      {/* Main Two-Column Layout */}
      <div className="dashboard-main-columns">
        {/* Left Column */}
        <div className="dashboard-col-primary">
          {/* Active / Continue Learning Card */}
          {activeLesson && (
            <div className="continue-learning-card">
              <div className="continue-card-header">
                <span className="badge-active">
                  {activeLesson.status === 'in_progress' ? 'In Progress' : 'Recent Lesson'}
                </span>
                <span className="lesson-time"><Clock size={14} /> {activeLesson.duration_minutes} mins</span>
              </div>
              <h3>{activeLesson.topic}</h3>
              <p className="lesson-summary-snippet">
                {activeLesson.lesson_metadata?.summary || 'Interactive lesson with step-by-step visuals and checks.'}
              </p>
              <div className="lesson-step-tracker">
                <span>Step {activeLesson.current_step_index + 1} of {activeLesson.steps?.length || 2}</span>
                <div className="tracker-bar">
                  <div
                    className="tracker-fill"
                    style={{
                      width: `${((activeLesson.current_step_index + 1) / (activeLesson.steps?.length || 1)) * 100}%`,
                    }}
                  />
                </div>
              </div>
              <Link to={`/classroom/${activeLesson.id}`} className="btn-resume-lesson">
                <Play size={16} /> Resume Classroom
              </Link>
            </div>
          )}

          {/* Quick Recommended Topics */}
          <div className="dashboard-section-box">
            <div className="flex justify-between items-center mb-3">
              <h3 className="section-title flex items-center gap-2">
                <Sparkles size={18} className="text-blue-400" /> Recommended for You
              </h3>
              <Link to="/create-lesson" className="text-xs text-blue-400 hover:underline">View All</Link>
            </div>
            <div className="recommendations-list">
              {recommendations.slice(0, 3).map((rec, i) => (
                <div key={i} className="recommendation-card-item">
                  <div className="rec-badge-type">{rec.type}</div>
                  <div className="rec-info">
                    <h4>{rec.topic}</h4>
                    <p>{rec.reason}</p>
                  </div>
                  <Link
                    to="/create-lesson"
                    state={{ topic: rec.topic, duration_minutes: rec.estimated_minutes }}
                    className="btn-secondary btn-sm"
                  >
                    Start ({rec.estimated_minutes}m)
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="dashboard-col-secondary">
          {/* Weak Concepts Alert */}
          {mastery?.weak_topics && mastery.weak_topics.length > 0 && (
            <div className="weak-concepts-alert-card">
              <div className="flex items-center gap-2 text-amber-400 font-semibold mb-2">
                <AlertTriangle size={18} /> Concepts Needing Revision
              </div>
              <p className="text-xs text-slate-300 mb-3">
                Identified from recent formative checks & misconceptions:
              </p>
              <div className="weak-tags-cloud">
                {mastery.weak_topics.map((t, idx) => (
                  <span key={idx} className="weak-tag">{t}</span>
                ))}
              </div>
              <Link to="/revision" className="btn-revision-link">
                Launch Targeted Practice Drills →
              </Link>
            </div>
          )}

          {/* Documents & RAG Hub Banner */}
          <div className="documents-hub-teaser-card">
            <div className="flex items-center gap-2 text-blue-400 font-semibold mb-1">
              <FolderOpen size={18} /> Learn From Your Documents
            </div>
            <p className="text-xs text-slate-300 mb-3">
              Upload class notes, textbooks (PDF, DOCX, PPTX), and have EduMentor teach directly from your syllabus with source citations.
            </p>
            <Link to="/documents" className="btn-secondary btn-sm w-full text-center">
              Open Document RAG Hub
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
