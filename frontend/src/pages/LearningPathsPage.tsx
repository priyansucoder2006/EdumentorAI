import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { progressService } from '../services/progressService';
import { LearningPath, LearningPathNode } from '../types';
import {
  Compass,
  Sparkles,
  Calendar,
  Clock,
  Target,
  Award,
  BookOpen,
  CheckCircle2,
  Circle,
  Lock,
  ArrowRight,
  Code,
  Layers,
  Wrench,
  Trash2,
  PlusCircle,
  ChevronRight,
  GraduationCap
} from 'lucide-react';

export const LearningPathsPage: React.FC = () => {
  const navigate = useNavigate();
  const [paths, setPaths] = useState<LearningPath[]>([]);
  const [selectedPathIndex, setSelectedPathIndex] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Roadmap Form state
  const [topic, setTopic] = useState<string>('Data Science & Machine Learning');
  const [durationMonths, setDurationMonths] = useState<number>(6);
  const [hoursPerWeek, setHoursPerWeek] = useState<number>(10);
  const [currentLevel, setCurrentLevel] = useState<string>('beginner');
  const [learningGoal, setLearningGoal] = useState<string>('career');

  const fetchPaths = async () => {
    try {
      setLoading(true);
      const data = await progressService.getLearningPaths();
      setPaths(data);
    } catch (err: any) {
      console.warn('Failed to load learning paths:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPaths();
  }, []);

  const handleGenerateRoadmap = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    setIsGenerating(true);
    setError(null);

    const durationLabel = durationMonths >= 12
      ? '1 Year'
      : `${durationMonths} Months`;

    try {
      const newPath = await progressService.generateRoadmap({
        topic: topic.trim(),
        duration_months: durationMonths,
        duration_label: durationLabel,
        hours_per_week: hoursPerWeek,
        current_level: currentLevel,
        learning_goal: learningGoal,
      });

      setPaths((prev) => [newPath, ...prev]);
      setSelectedPathIndex(0);
    } catch (err: any) {
      setError(err.message || 'Failed to architect custom curriculum roadmap.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleToggleNodeComplete = async (pathId: string, node: LearningPathNode) => {
    const newStatus = node.status === 'completed' ? 'in_progress' : 'completed';
    try {
      const updated = await progressService.updateNodeStatus(pathId, node.id, newStatus);
      setPaths((prev) => prev.map((p) => (p.id === pathId ? updated : p)));
    } catch (err) {
      console.error('Failed to update stage status:', err);
    }
  };

  const handleDeletePath = async (pathId: string) => {
    if (!window.confirm('Are you sure you want to delete this roadmap?')) return;
    try {
      await progressService.deleteLearningPath(pathId);
      setPaths((prev) => prev.filter((p) => p.id !== pathId));
      setSelectedPathIndex(0);
    } catch (err) {
      console.error('Failed to delete roadmap:', err);
    }
  };

  const samplePresets = [
    { title: '6 Months Data Science', topic: 'Data Science & Machine Learning', dur: 6, hrs: 10, lvl: 'beginner', goal: 'career' },
    { title: '3 Months Full-Stack Web Dev', topic: 'Full-Stack Web Development (React & Node)', dur: 3, hrs: 15, lvl: 'intermediate', goal: 'projects' },
    { title: '6 Months AI / Deep Learning', topic: 'AI & Deep Learning Engineering', dur: 6, hrs: 12, lvl: 'intermediate', goal: 'career' },
    { title: '4 Months DevOps & Cloud', topic: 'DevOps & AWS Cloud Architecture', dur: 4, hrs: 10, lvl: 'beginner', goal: 'career' },
    { title: '2 Months Calculus & Math', topic: 'Calculus & Linear Algebra for Machine Learning', dur: 2, hrs: 8, lvl: 'beginner', goal: 'mastery' },
  ];

  const currentPath: LearningPath | undefined = paths[selectedPathIndex];

  return (
    <div className="learning-paths-container pb-16">
      {/* Page Header */}
      <div className="page-header mb-8">
        <div>
          <div className="flex items-center gap-2 text-cyan-400 font-semibold text-xs uppercase mb-1">
            <Compass size={16} /> Dynamic Curriculum Architect
          </div>
          <h2 className="text-3xl font-bold text-white tracking-tight">Personalized Learning Roadmaps</h2>
          <p className="text-slate-400 text-sm mt-1">
            Generate custom month-by-month and week-by-week curriculum trees specifying exact time commitments, concepts, and portfolio projects.
          </p>
        </div>
      </div>

      {/* Grid: Generator Form & Saved Selector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 mb-10">
        {/* Left Column: Roadmap Generator Form */}
        <div className="lg:col-span-8 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl backdrop-blur-sm">
          <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-blue-600/20 text-blue-400">
                <Sparkles size={20} />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-white">Generate Custom Curriculum Roadmap</h3>
                <p className="text-xs text-slate-400">Tell the AI what you want to master and how much time you have.</p>
              </div>
            </div>
          </div>

          {/* Quick Presets Strip */}
          <div className="mb-5">
            <span className="text-xs font-semibold text-slate-400 block mb-2">⚡ Popular Curriculum Presets:</span>
            <div className="flex flex-wrap gap-2">
              {samplePresets.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setTopic(p.topic);
                    setDurationMonths(p.dur);
                    setHoursPerWeek(p.hrs);
                    setCurrentLevel(p.lvl);
                    setLearningGoal(p.goal);
                  }}
                  className="px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-blue-600/30 hover:border-blue-500/50 border border-slate-700 text-slate-300 text-xs font-medium transition-all"
                >
                  {p.title}
                </button>
              ))}
            </div>
          </div>

          {error && <div className="auth-error-alert mb-4">{error}</div>}

          <form onSubmit={handleGenerateRoadmap} className="space-y-4">
            {/* Topic Input */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center gap-1.5">
                <BookOpen size={14} className="text-blue-400" /> Target Subject / Field
              </label>
              <input
                type="text"
                required
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g. Data Science, Machine Learning, Full-Stack React, Cybersecurity, Calculus"
                className="w-full px-4 py-2.5 bg-slate-950 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm"
              />
            </div>

            {/* Duration & Weekly Hours Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center gap-1.5">
                  <Calendar size={14} className="text-cyan-400" /> Roadmap Timeline
                </label>
                <div className="grid grid-cols-4 gap-1.5">
                  {[
                    { val: 1, label: '1 Mo' },
                    { val: 3, label: '3 Mos' },
                    { val: 6, label: '6 Mos' },
                    { val: 12, label: '1 Year' },
                  ].map((d) => (
                    <button
                      key={d.val}
                      type="button"
                      onClick={() => setDurationMonths(d.val)}
                      className={`py-2 rounded-lg text-xs font-semibold border transition-all ${
                        durationMonths === d.val
                          ? 'bg-blue-600 text-white border-blue-500 shadow-md shadow-blue-600/30'
                          : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      {d.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center gap-1.5">
                  <Clock size={14} className="text-emerald-400" /> Weekly Time Commitment
                </label>
                <div className="grid grid-cols-4 gap-1.5">
                  {[
                    { val: 5, label: '5 hrs/wk' },
                    { val: 10, label: '10 hrs/wk' },
                    { val: 15, label: '15 hrs/wk' },
                    { val: 20, label: '20 hrs/wk' },
                  ].map((h) => (
                    <button
                      key={h.val}
                      type="button"
                      onClick={() => setHoursPerWeek(h.val)}
                      className={`py-2 rounded-lg text-xs font-semibold border transition-all ${
                        hoursPerWeek === h.val
                          ? 'bg-emerald-600 text-white border-emerald-500 shadow-md shadow-emerald-600/30'
                          : 'bg-slate-950 text-slate-400 border-slate-800 hover:border-slate-700'
                      }`}
                    >
                      {h.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Level & Goal Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center gap-1.5">
                  <Award size={14} className="text-purple-400" /> Starting Experience Level
                </label>
                <select
                  value={currentLevel}
                  onChange={(e) => setCurrentLevel(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white text-xs focus:outline-none focus:border-blue-500"
                >
                  <option value="beginner">Beginner (Zero / Fundamental knowledge)</option>
                  <option value="intermediate">Intermediate (Foundational proficiency)</option>
                  <option value="advanced">Advanced (Deep specialization & frontiers)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5 flex items-center gap-1.5">
                  <Target size={14} className="text-rose-400" /> Primary Learning Goal
                </label>
                <select
                  value={learningGoal}
                  onChange={(e) => setLearningGoal(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-700 rounded-xl text-white text-xs focus:outline-none focus:border-blue-500"
                >
                  <option value="career">Job Ready / Career Switch</option>
                  <option value="projects">Build Real-World Portfolio Projects</option>
                  <option value="exam">School / University / Certification Exam</option>
                  <option value="mastery">Deep Theoretical & Practical Mastery</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={isGenerating}
              className="w-full mt-2 py-3 bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white rounded-xl font-semibold text-sm shadow-lg shadow-blue-600/20 flex items-center justify-center gap-2 transition-all disabled:opacity-50"
            >
              {isGenerating ? (
                <>
                  <span className="spinner" />
                  <span>Synthesizing Personalized {durationMonths}-Month Curriculum...</span>
                </>
              ) : (
                <>
                  <Sparkles size={16} />
                  <span>Generate Custom {durationMonths}-Month Curriculum</span>
                  <ArrowRight size={16} />
                </>
              )}
            </button>
          </form>
        </div>

        {/* Right Column: Saved Roadmaps Navigation */}
        <div className="lg:col-span-4 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl flex flex-col">
          <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Layers size={16} className="text-blue-400" /> Your Active Roadmaps
            </h3>
            <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 text-xs font-mono">
              {paths.length}
            </span>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12 text-slate-500">
              <span className="spinner" />
            </div>
          ) : paths.length === 0 ? (
            <div className="text-center py-8 text-slate-500 text-xs">
              No custom roadmaps generated yet. Fill out the form to create your first curriculum!
            </div>
          ) : (
            <div className="space-y-2.5 overflow-y-auto max-h-[340px] pr-1">
              {paths.map((p, idx) => {
                const isSelected = idx === selectedPathIndex;
                return (
                  <div
                    key={p.id || idx}
                    onClick={() => setSelectedPathIndex(idx)}
                    className={`p-3.5 rounded-xl border transition-all cursor-pointer flex items-center justify-between ${
                      isSelected
                        ? 'bg-blue-600/15 border-blue-500/60 shadow-inner'
                        : 'bg-slate-950 border-slate-800/80 hover:border-slate-700'
                    }`}
                  >
                    <div className="truncate pr-2">
                      <div className="font-medium text-xs text-white truncate">{p.topic}</div>
                      <div className="text-[11px] text-slate-400 flex items-center gap-2 mt-1">
                        <span>{p.nodes?.length || 0} Stages</span>
                        <span>•</span>
                        <span className="text-cyan-400 font-semibold">{p.progress_percentage}% Done</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-1.5 flex-shrink-0">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeletePath(p.id);
                        }}
                        className="p-1 rounded text-slate-500 hover:text-rose-400 transition-colors"
                        title="Delete Roadmap"
                      >
                        <Trash2 size={14} />
                      </button>
                      <ChevronRight size={16} className={isSelected ? 'text-blue-400' : 'text-slate-600'} />
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Main Roadmap Tree / Stages View */}
      {currentPath ? (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 lg:p-8 shadow-2xl">
          {/* Roadmap Header Banner */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-800 mb-8">
            <div>
              <div className="flex items-center gap-2 text-blue-400 font-semibold text-xs uppercase mb-1">
                <Compass size={16} /> Structured Learning Roadmap
              </div>
              <h3 className="text-2xl font-bold text-white">{currentPath.topic}</h3>
              <p className="text-slate-300 text-sm mt-1 max-w-3xl">{currentPath.description}</p>
            </div>

            <div className="flex items-center gap-4 bg-slate-950 px-5 py-3 rounded-xl border border-slate-800 self-start md:self-auto">
              <div className="text-right">
                <span className="text-xs text-slate-400 block">Overall Mastery</span>
                <span className="text-2xl font-bold text-cyan-400 font-mono">{currentPath.progress_percentage}%</span>
              </div>
              <div className="w-12 h-12 rounded-full border-4 border-slate-800 flex items-center justify-center relative">
                <div
                  className="absolute inset-0 rounded-full border-4 border-cyan-400"
                  style={{
                    clipPath: `polygon(50% 50%, -50% -50%, ${currentPath.progress_percentage * 2}% -50%)`,
                  }}
                />
                <GraduationCap size={18} className="text-slate-400" />
              </div>
            </div>
          </div>

          {/* Month-by-Month & Stage-by-Stage Timeline */}
          <div className="space-y-6">
            {(currentPath.nodes || []).map((node, idx) => {
              const isCompleted = node.status === 'completed';
              const isInProgress = node.status === 'in_progress';
              const isLocked = node.status === 'locked';

              return (
                <div
                  key={node.id || idx}
                  className={`rounded-2xl border transition-all overflow-hidden ${
                    isCompleted
                      ? 'bg-slate-950/70 border-emerald-500/30'
                      : isInProgress
                      ? 'bg-slate-950 border-blue-500 shadow-lg shadow-blue-500/10'
                      : 'bg-slate-950/40 border-slate-800/80 opacity-75'
                  }`}
                >
                  {/* Stage Top Bar */}
                  <div className={`px-6 py-3.5 border-b flex flex-wrap items-center justify-between gap-3 ${
                    isCompleted
                      ? 'bg-emerald-950/20 border-emerald-900/40'
                      : isInProgress
                      ? 'bg-blue-950/30 border-blue-900/40'
                      : 'bg-slate-900/40 border-slate-800'
                  }`}>
                    <div className="flex items-center gap-3">
                      <div className="node-status-indicator">
                        {isCompleted && <CheckCircle2 size={22} className="text-emerald-400" />}
                        {isInProgress && <Circle size={22} className="text-blue-400 fill-blue-400/20" />}
                        {isLocked && <Lock size={20} className="text-slate-500" />}
                      </div>
                      <span className="font-semibold text-sm text-white">
                        {node.phase_name || `Stage ${idx + 1}`}
                      </span>
                    </div>

                    <div className="flex items-center gap-2.5">
                      {node.time_commitment && (
                        <span className="px-2.5 py-1 rounded-md bg-slate-800 text-cyan-300 text-xs font-mono border border-slate-700">
                          ⏱ {node.time_commitment}
                        </span>
                      )}
                      <span className={`px-2.5 py-0.5 rounded-md text-xs font-semibold uppercase ${
                        node.difficulty === 'beginner'
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : node.difficulty === 'advanced'
                          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                          : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                      }`}>
                        {node.difficulty}
                      </span>
                    </div>
                  </div>

                  {/* Stage Main Body */}
                  <div className="p-6">
                    <h4 className="text-lg font-bold text-white mb-2">{node.title}</h4>
                    <p className="text-slate-300 text-sm mb-4 leading-relaxed">{node.description}</p>

                    {/* Core Concepts to Learn */}
                    {node.concepts && node.concepts.length > 0 && (
                      <div className="mb-4">
                        <span className="text-xs font-semibold text-slate-400 block mb-2 flex items-center gap-1.5">
                          <BookOpen size={13} className="text-blue-400" /> Key Concepts to Master:
                        </span>
                        <div className="flex flex-wrap gap-2">
                          {node.concepts.map((concept, cIdx) => (
                            <span
                              key={cIdx}
                              className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-slate-200 text-xs font-medium"
                            >
                              • {concept}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Practical Project Asset */}
                    {node.practical_project && (
                      <div className="mb-4 p-3.5 rounded-xl bg-blue-950/20 border border-blue-800/30 flex items-start gap-3">
                        <Code size={18} className="text-blue-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <span className="text-xs font-bold text-blue-300 uppercase tracking-wider block">
                            🛠 Practical Milestone Project:
                          </span>
                          <span className="text-xs text-slate-300 mt-0.5 block leading-relaxed">
                            {node.practical_project}
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Tools & Resources */}
                    {node.tools_and_resources && node.tools_and_resources.length > 0 && (
                      <div className="mb-5 flex items-center gap-2 text-xs text-slate-400">
                        <Wrench size={14} className="text-slate-500" />
                        <span className="font-semibold text-slate-400">Tools:</span>
                        <span className="text-slate-300">{node.tools_and_resources.join(', ')}</span>
                      </div>
                    )}

                    {/* Actions Row */}
                    <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-800/80">
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={() => handleToggleNodeComplete(currentPath.id, node)}
                          className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors flex items-center gap-1.5 ${
                            isCompleted
                              ? 'bg-emerald-600/20 border-emerald-500/40 text-emerald-300 hover:bg-emerald-600/30'
                              : 'bg-slate-900 border-slate-700 text-slate-300 hover:bg-slate-800'
                          }`}
                        >
                          <CheckCircle2 size={14} className={isCompleted ? 'text-emerald-400' : 'text-slate-500'} />
                          <span>{isCompleted ? 'Completed ✓' : 'Mark Complete'}</span>
                        </button>
                      </div>

                      <button
                        type="button"
                        onClick={() => {
                          navigate('/create-lesson', {
                            state: {
                              topic: `${node.title} (${currentPath.topic.split('—')[0].trim()})`,
                              difficulty: node.difficulty,
                              duration_minutes: 20,
                            },
                          });
                        }}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold flex items-center gap-2 shadow-md shadow-blue-600/20 transition-all"
                      >
                        <Sparkles size={14} />
                        <span>Launch AI Teacher Lesson</span>
                        <ArrowRight size={14} />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : null}
    </div>
  );
};
