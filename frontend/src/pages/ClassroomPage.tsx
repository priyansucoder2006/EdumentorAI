import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { lessonService } from '../services/lessonService';
import { voiceManager } from '../services/voiceService';
import { Lesson, LessonStep, Interaction } from '../types';
import { AvatarTeacher } from '../components/classroom/AvatarTeacher';
import { VisualBoard } from '../components/classroom/VisualBoard';
import { QuestionEngine } from '../components/classroom/QuestionEngine';
import { MisconceptionModal } from '../components/classroom/MisconceptionModal';
import { LessonSidebar } from '../components/classroom/LessonSidebar';
import { VideoPlayerModal } from '../components/classroom/VideoPlayerModal';
import {
  Volume2,
  VolumeX,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  Sparkles,
  BookOpen,
  HelpCircle,
  Lightbulb,
  Video,
  Clock,
  Target,
  Award,
} from 'lucide-react';

export const ClassroomPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [currentStepIndex, setCurrentStepIndex] = useState<number>(0);
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [isVoiceEnabled, setIsVoiceEnabled] = useState<boolean>(true);
  const [isSubmittingAnswer, setIsSubmittingAnswer] = useState<boolean>(false);
  const [activeMisconception, setActiveMisconception] = useState<any>(null);
  const [adaptiveDecision, setAdaptiveDecision] = useState<any>(null);
  const [currentMastery, setCurrentMastery] = useState<number>(65);
  const [pedagogicalState, setPedagogicalState] = useState<string>('EXPLAINING');
  const [teacherMood, setTeacherMood] = useState<'explaining' | 'questioning' | 'praising' | 'remedial'>('explaining');
  const [showVideoModal, setShowVideoModal] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  // Load lesson
  useEffect(() => {
    if (!id) return;
    const fetchLesson = async () => {
      try {
        const l = await lessonService.getLesson(id);
        setLesson(l);
        setCurrentStepIndex(l.current_step_index || 0);
      } catch (err) {
        console.error('Error fetching lesson:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchLesson();

    // Voice speaking listener
    voiceManager.setSpeakingListener(setIsSpeaking);

    return () => {
      voiceManager.stopSpeaking();
    };
  }, [id]);

  const currentStep: LessonStep | undefined = lesson?.steps?.[currentStepIndex];

  // Auto-speak on step change if voice enabled
  useEffect(() => {
    if (currentStep && isVoiceEnabled) {
      setTeacherMood('explaining');
      setPedagogicalState('EXPLAINING');
      const speechText = `${currentStep.concept}. ${currentStep.explanation} ${currentStep.analogy ? `Think of it like this: ${currentStep.analogy}` : ''}`;
      voiceManager.speak(speechText, lesson?.language || 'en', () => {
        setTeacherMood('questioning');
        setPedagogicalState('CHECKING_UNDERSTANDING');
      });
    }
  }, [currentStepIndex, lesson?.language]);

  const handleToggleVoice = () => {
    if (isSpeaking) {
      voiceManager.stopSpeaking();
      setIsVoiceEnabled(false);
    } else {
      setIsVoiceEnabled(true);
      if (currentStep) {
        voiceManager.speak(currentStep.explanation, lesson?.language || 'en');
      }
    }
  };

  const handleAnswerSubmit = async (answerText: string, mode: string) => {
    if (!currentStep || !lesson) return;
    setIsSubmittingAnswer(true);
    setPedagogicalState('EVALUATING');

    try {
      const interaction: Interaction = await lessonService.submitAnswer({
        step_id: currentStep.id,
        student_answer: answerText,
        response_mode: mode,
      });

      setCurrentMastery(interaction.current_mastery);

      if (interaction.evaluation.is_correct) {
        // Praise student & check for higher difficulty
        if (interaction.evaluation.score >= 0.85) {
          setPedagogicalState('MASTERY_ACHIEVED');
          setTeacherMood('praising');
        } else {
          setPedagogicalState('CONTINUE');
          setTeacherMood('praising');
        }
        setActiveMisconception(null);
        setAdaptiveDecision(interaction.adaptive_decision);
        if (isVoiceEnabled) {
          voiceManager.speak(
            interaction.adaptive_decision?.remedial_explanation || 'Excellent explanation! You captured the core foundational principle.',
            lesson.language
          );
        }
      } else {
        // Misconception Diagnosed & Adaptive Reteach
        setPedagogicalState('DIAGNOSING');
        setTimeout(() => setPedagogicalState('RE_TEACHING'), 800);
        setTeacherMood('remedial');
        setActiveMisconception(interaction.misconception);
        setAdaptiveDecision(interaction.adaptive_decision);
        if (isVoiceEnabled && interaction.adaptive_decision.remedial_explanation) {
          voiceManager.speak(interaction.adaptive_decision.remedial_explanation, lesson.language);
        }
      }
    } catch (err) {
      console.error('Answer evaluation error:', err);
    } finally {
      setIsSubmittingAnswer(false);
    }
  };

  const handleNextStep = async () => {
    if (!lesson) return;
    voiceManager.stopSpeaking();
    setActiveMisconception(null);
    setAdaptiveDecision(null);

    const steps = lesson.steps || [];
    if (currentStepIndex + 1 < steps.length) {
      try {
        const updated = await lessonService.advanceStep(lesson.id);
        setLesson(updated);
        setCurrentStepIndex((prev) => prev + 1);
      } catch {
        setCurrentStepIndex((prev) => prev + 1);
      }
    } else {
      // Proceed to Assessment
      navigate(`/assessment/${lesson.id}`);
    }
  };

  const handleSwitchLanguage = async (targetLang: string) => {
    if (!lesson) return;
    try {
      const updated = await lessonService.switchLanguage(lesson.id, targetLang);
      setLesson(updated);
      if (isVoiceEnabled && currentStep) {
        voiceManager.speak(`Language updated to ${targetLang}. Continuing our adaptive lesson!`, targetLang);
      }
    } catch (err) {
      console.warn('Language switch error:', err);
    }
  };

  if (loading || !lesson || !currentStep) {
    return (
      <div className="classroom-loading-screen">
        <span className="spinner-lg" />
        <h3>Connecting to AI Master Teacher...</h3>
      </div>
    );
  }

  const isLastStep = currentStepIndex === (lesson.steps?.length || 1) - 1;
  const currentObjective = lesson.objectives?.[currentStepIndex] || lesson.objectives?.[0] || 'Understand foundational principles';
  const minutesRemaining = Math.max(1, Math.round(((lesson.steps.length - currentStepIndex) / lesson.steps.length) * (lesson.duration_minutes || 20)));

  return (
    <div className="classroom-layout-container">
      {/* Sidebar Controls */}
      <aside className="classroom-sidebar-pane">
        <LessonSidebar
          lesson={lesson}
          currentStepIndex={currentStepIndex}
          overallMastery={currentMastery}
          onSwitchLanguage={handleSwitchLanguage}
          onSelectStep={(idx) => setCurrentStepIndex(idx)}
        />
      </aside>

      {/* Main Classroom Stage */}
      <main className="classroom-main-stage">
        {/* Top Floating Control Strip */}
        <div className="classroom-top-strip">
          <div className="flex items-center gap-3">
            <span className="step-pill-indicator">
              Step {currentStepIndex + 1} of {lesson.steps.length}
            </span>
            <div className="flex items-center gap-2">
              <span className={`px-2.5 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${
                pedagogicalState === 'RE_TEACHING' || pedagogicalState === 'DIAGNOSING'
                  ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                  : pedagogicalState === 'MASTERY_ACHIEVED'
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
              }`}>
                State: {pedagogicalState.replace('_', ' ')}
              </span>
            </div>
            <h2 className="current-concept-headline">{currentStep.concept}</h2>
          </div>

          <div className="classroom-top-actions flex items-center gap-3">
            {/* Generate Video Lesson Button */}
            <button
              className="flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-lg text-xs font-medium shadow-md transition-all"
              onClick={() => setShowVideoModal(true)}
              title="Generate MP4 Teaching Video"
            >
              <Video size={14} />
              <span>Generate Video</span>
            </button>

            {/* Time remaining badge */}
            <div className="flex items-center gap-1 text-xs text-slate-400 bg-slate-800/80 px-2.5 py-1.5 rounded-lg border border-slate-700">
              <Clock size={13} className="text-cyan-400" />
              <span>~{minutesRemaining} min remaining</span>
            </div>

            {/* Voice toggle */}
            <button
              className={`btn-voice-toggle ${isSpeaking ? 'active' : ''}`}
              onClick={handleToggleVoice}
              title={isVoiceEnabled ? 'Mute AI Teacher Voice' : 'Enable AI Teacher Voice'}
            >
              {isVoiceEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
              <span>{isSpeaking ? 'Speaking...' : isVoiceEnabled ? 'Voice On' : 'Muted'}</span>
            </button>
          </div>
        </div>

        {/* Dynamic Split Screen: Avatar & Narration + Subject Visual Board */}
        <div className="classroom-split-grid">
          {/* Left Column: Avatar & Teacher Dialogue */}
          <div className="teacher-interaction-column">
            {/* Animated Teacher Avatar */}
            <AvatarTeacher
              isSpeaking={isSpeaking}
              teacherMood={teacherMood}
              language={lesson.language}
              currentConcept={currentStep.concept}
            />

            {/* Explanation Dialogue Box */}
            <div className="teacher-speech-bubble">
              <div className="bubble-header">
                <Sparkles size={14} className="text-blue-400" />
                <span>AI Teacher Explanation</span>
              </div>
              <p className="bubble-text">{currentStep.explanation}</p>
              {currentStep.analogy && (
                <div className="bubble-analogy">
                  <Lightbulb size={16} className="text-amber-400 flex-shrink-0" />
                  <span><strong>Intuition:</strong> {currentStep.analogy}</span>
                </div>
              )}
            </div>

            {/* Misconception Diagnostic Breakdown (if detected) */}
            {activeMisconception && adaptiveDecision && (
              <MisconceptionModal
                misconception={activeMisconception}
                adaptiveDecision={adaptiveDecision}
                onContinue={() => setActiveMisconception(null)}
              />
            )}

            {/* Formative Question Engine */}
            <QuestionEngine
              question={
                adaptiveDecision?.next_question || currentStep.question
              }
              isSubmitting={isSubmittingAnswer}
              onSubmitAnswer={handleAnswerSubmit}
              language={lesson.language}
            />
          </div>

          {/* Right Column: Subject-Aware Visual Board & Next Step Bar */}
          <div className="visual-board-column">
            <VisualBoard
              visualType={adaptiveDecision?.visual_override?.type || currentStep.visual_type}
              visualData={adaptiveDecision?.visual_override || currentStep.visual_data}
              concept={currentStep.concept}
              analogy={currentStep.analogy}
            />

            {/* Bottom Progression Bar */}
            <div className="step-navigation-bar">
              <button
                className="btn-secondary"
                disabled={currentStepIndex === 0}
                onClick={() => setCurrentStepIndex((p) => Math.max(0, p - 1))}
              >
                <ArrowLeft size={16} /> Previous
              </button>

              <button className="btn-primary-large" onClick={handleNextStep}>
                <span>{isLastStep ? 'Take Final Assessment' : 'Next Concept'}</span>
                <ArrowRight size={18} />
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* Video Generation & Playback Modal */}
      {showVideoModal && (
        <VideoPlayerModal
          lessonId={lesson.id}
          lessonTopic={lesson.topic}
          onClose={() => setShowVideoModal(false)}
        />
      )}
    </div>
  );
};
