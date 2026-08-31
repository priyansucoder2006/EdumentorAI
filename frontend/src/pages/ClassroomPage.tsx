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
  const [teacherMood, setTeacherMood] = useState<'explaining' | 'questioning' | 'praising' | 'remedial'>('explaining');
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
      const speechText = `${currentStep.concept}. ${currentStep.explanation} ${currentStep.analogy ? `Think of it like this: ${currentStep.analogy}` : ''}`;
      voiceManager.speak(speechText, lesson?.language || 'en', () => {
        setTeacherMood('questioning');
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

    try {
      const interaction: Interaction = await lessonService.submitAnswer({
        step_id: currentStep.id,
        student_answer: answerText,
        response_mode: mode,
      });

      setCurrentMastery(interaction.current_mastery);

      if (interaction.evaluation.is_correct) {
        // Praise student
        setTeacherMood('praising');
        setActiveMisconception(null);
        setAdaptiveDecision(interaction.adaptive_decision);
        if (isVoiceEnabled) {
          voiceManager.speak('Shabash! Excellent explanation. You captured the core physical principle perfectly.', lesson.language);
        }
      } else {
        // Misconception Detected!
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
        voiceManager.speak(`Language switched to ${targetLang}. Continuing our lesson seamlessly!`, targetLang);
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
            <h2 className="current-concept-headline">{currentStep.concept}</h2>
          </div>

          <div className="classroom-top-actions">
            <button
              className={`btn-voice-toggle ${isSpeaking ? 'active' : ''}`}
              onClick={handleToggleVoice}
              title={isVoiceEnabled ? 'Mute AI Teacher Voice' : 'Enable AI Teacher Voice'}
            >
              {isVoiceEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
              <span>{isSpeaking ? 'Teacher Speaking' : isVoiceEnabled ? 'Voice On' : 'Voice Muted'}</span>
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
                <span>Teacher Explanation</span>
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
    </div>
  );
};
