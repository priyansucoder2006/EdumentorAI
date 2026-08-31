import React from 'react';
import { Lesson, LessonStep } from '../../types';
import { CheckCircle2, Circle, RotateCcw, Clock, Award, Globe, BookOpen } from 'lucide-react';

interface LessonSidebarProps {
  lesson: Lesson;
  currentStepIndex: number;
  overallMastery: number;
  onSwitchLanguage: (lang: string) => void;
  onSelectStep?: (index: number) => void;
}

export const LessonSidebar: React.FC<LessonSidebarProps> = ({
  lesson,
  currentStepIndex,
  overallMastery,
  onSwitchLanguage,
  onSelectStep,
}) => {
  const steps = lesson.steps || [];
  const currentLang = lesson.language || 'en';

  const languages = [
    { code: 'en', label: 'English' },
    { code: 'hinglish', label: 'Hinglish' },
    { code: 'hi', label: 'हिन्दी (Hindi)' },
    { code: 'bn', label: 'বাংলা (Bengali)' },
  ];

  return (
    <div className="lesson-sidebar-panel">
      {/* Lesson Header */}
      <div className="sidebar-section lesson-meta-box">
        <div className="flex items-center gap-2 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-1">
          <BookOpen size={14} /> Lesson Roadmap
        </div>
        <h3 className="sidebar-lesson-title">{lesson.topic}</h3>
        <div className="sidebar-meta-badges">
          <span className="meta-badge"><Clock size={12} /> {lesson.duration_minutes}m</span>
          <span className="meta-badge diff">{lesson.difficulty}</span>
        </div>
      </div>

      {/* Real-time Mastery Gauge */}
      <div className="sidebar-section mastery-gauge-card">
        <div className="flex justify-between items-center mb-1">
          <span className="text-xs font-medium text-slate-300 flex items-center gap-1">
            <Award size={14} className="text-emerald-400" /> Concept Mastery
          </span>
          <span className="text-sm font-bold text-emerald-400">{Math.round(overallMastery)}%</span>
        </div>
        <div className="mastery-progress-bar">
          <div
            className="mastery-progress-fill"
            style={{ width: `${Math.min(100, Math.max(5, overallMastery))}%` }}
          />
        </div>
      </div>

      {/* Step Roadmap */}
      <div className="sidebar-section step-roadmap-list">
        <div className="section-subtitle">Lesson Modules</div>
        {steps.map((step, idx) => {
          const isActive = idx === currentStepIndex;
          const isCompleted = idx < currentStepIndex || step.state === 'completed';
          const isReteach = step.state === 'reteach';

          return (
            <div
              key={step.id || idx}
              className={`roadmap-step-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''} ${isReteach ? 'reteach' : ''}`}
              onClick={() => onSelectStep && onSelectStep(idx)}
            >
              <div className="step-icon-col">
                {isCompleted ? (
                  <CheckCircle2 size={16} className="text-emerald-400" />
                ) : isReteach ? (
                  <RotateCcw size={16} className="text-amber-400" />
                ) : (
                  <Circle size={16} className={isActive ? 'text-blue-400 fill-blue-400/20' : 'text-slate-500'} />
                )}
              </div>
              <div className="step-content-col">
                <div className="step-num">Step {step.step_number}</div>
                <div className="step-concept">{step.concept}</div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Multilingual Switcher */}
      <div className="sidebar-section language-switcher-card">
        <div className="section-subtitle flex items-center gap-1.5">
          <Globe size={14} /> Teaching Language
        </div>
        <div className="language-btn-grid">
          {languages.map((l) => (
            <button
              key={l.code}
              className={`lang-btn ${currentLang === l.code ? 'active' : ''}`}
              onClick={() => onSwitchLanguage(l.code)}
            >
              {l.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
