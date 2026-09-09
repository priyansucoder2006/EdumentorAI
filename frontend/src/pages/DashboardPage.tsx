import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { progressService } from '../services/progressService';
import { lessonService } from '../services/lessonService';
import { learningVideoService } from '../services/learningVideoService';
import { YouTubeVideoCard } from '../components/visual_renderers/YouTubeVideoCard';
import { MasteryOverview, Lesson, RecommendationItem, YouTubeVideoMetadata } from '../types';
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
  Youtube,
  Loader2,
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

  // YouTube Video Recommendation State
  const [ytTopic, setYtTopic] = useState<string>('Recursion in Python');
  const [ytDuration, setYtDuration] = useState<number>(20);
  const [ytPref, setYtPref] = useState<string>('around');
  const [ytLoading, setYtLoading] = useState<boolean>(false);
  const [ytResult, setYtResult] = useState<YouTubeVideoMetadata | null>(null);
  const [ytError, setYtError] = useState<string | null>(null);

  const handleVideoSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ytTopic.trim()) return;
    setYtLoading(true);
    setYtError(null);
    try {
      const resp = await learningVideoService.findLearningVideo(ytTopic, ytDuration, ytPref);
      if (resp.found && resp.video) {
        setYtResult(resp.video);
      } else {
        setYtError(resp.reason || 'No suitable video found.');
      }
    } catch (err: any) {
      setYtError(err.message || 'Failed to fetch YouTube recommendation.');
    } finally {
      setYtLoading(false);
    }
  };


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

          {/* AI-Powered YouTube Video Recommendation Hub */}
          <div className="dashboard-section-box bg-slate-900 border border-slate-700/80 rounded-xl p-5 mb-5 shadow-lg">
            <div className="flex justify-between items-center mb-2">
              <h3 className="section-title flex items-center gap-2 text-base font-bold text-white">
                <span className="p-1 rounded-md bg-red-600/20 text-red-400 border border-red-500/30">
                  <Youtube size={16} />
                </span>
                <span>AI YouTube Learning Recommendation</span>
              </h3>
              <span className="text-xs text-slate-400 font-medium">Duration-Aware • Exactly 1 Video</span>
            </div>
            <p className="text-xs text-slate-300 mb-4">
              Need deeper understanding? Search the official YouTube Data API v3 for <strong>exactly ONE</strong> verified educational video matching your exact target time.
            </p>

            <form onSubmit={handleVideoSearch} className="flex flex-col sm:flex-row gap-2 mb-4">
              <input
                type="text"
                placeholder="Topic (e.g. Recursion in Python, React Hooks, Docker)..."
                value={ytTopic}
                onChange={(e) => setYtTopic(e.target.value)}
                className="flex-1 bg-slate-950 text-slate-100 text-xs rounded-lg px-3 py-2 border border-slate-700 focus:outline-none focus:border-red-500"
              />
              <select
                value={ytDuration}
                onChange={(e) => setYtDuration(Number(e.target.value))}
                className="bg-slate-950 text-slate-200 text-xs rounded-lg px-2.5 py-2 border border-slate-700 focus:outline-none focus:border-red-500"
              >
                <option value={10}>~10 mins</option>
                <option value={20}>~20 mins</option>
                <option value={30}>~30 mins</option>
                <option value={60}>~60 mins</option>
                <option value={90}>~90 mins</option>
              </select>
              <select
                value={ytPref}
                onChange={(e) => setYtPref(e.target.value)}
                className="bg-slate-950 text-slate-200 text-xs rounded-lg px-2.5 py-2 border border-slate-700 focus:outline-none focus:border-red-500"
              >
                <option value="around">Around Time</option>
                <option value="under">Under (Max)</option>
                <option value="minimum">At least (60m+)</option>
                <option value="short">Short</option>
                <option value="detailed">Detailed</option>
              </select>
              <button
                type="submit"
                disabled={ytLoading || !ytTopic.trim()}
                className="px-3.5 py-2 bg-red-600 hover:bg-red-500 text-white text-xs font-semibold rounded-lg flex items-center justify-center gap-1.5 shadow transition-all disabled:opacity-50"
              >
                {ytLoading ? <Loader2 size={13} className="animate-spin" /> : <Sparkles size={13} />}
                <span>{ytLoading ? 'Finding...' : 'Recommend Video'}</span>
              </button>
            </form>

            {/* Video Result display */}
            {ytResult && (
              <div className="mt-3">
                <YouTubeVideoCard video={ytResult} />
              </div>
            )}
            {ytError && (
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs text-amber-400">
                {ytError}
              </div>
            )}
          </div>

          {/* Quick Recommended Topics */}
          <div className="dashboard-section-box">
            <div className="flex justify-between items-center mb-3">
              <h3 className="section-title flex items-center gap-2">
                <Sparkles size={18} className="text-blue-400" /> Recommended Lessons for You
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
