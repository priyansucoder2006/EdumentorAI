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
import { YouTubeRecommendationModal } from '../components/classroom/YouTubeRecommendationModal';
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
  Youtube,
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
  const [showYtModal, setShowYtModal] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  // Dynamic Teacher Dialogue and Doubt states
  const [teacherDialogueTitle, setTeacherDialogueTitle] = useState<string>('AI Teacher Explanation');
  const [teacherDialogueText, setTeacherDialogueText] = useState<string>('');
  const [teacherDialogueAnalogy, setTeacherDialogueAnalogy] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'concept' | 'feedback' | 'ask'>('concept');
  const [doubtInput, setDoubtInput] = useState<string>('');
  const [isAskingDoubt, setIsAskingDoubt] = useState<boolean>(false);

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
    if (currentStep) {
      setTeacherDialogueTitle('AI Teacher Explanation');
      setTeacherDialogueText(currentStep.explanation);
      setTeacherDialogueAnalogy(currentStep.analogy || null);
      setActiveTab('concept');
      setActiveMisconception(null);
      setAdaptiveDecision(null);

      if (isVoiceEnabled) {
        setTeacherMood('explaining');
        setPedagogicalState('EXPLAINING');
        const speechText = `${currentStep.concept}. ${currentStep.explanation} ${currentStep.analogy ? `Think of it like this: ${currentStep.analogy}` : ''}`;
        voiceManager.speak(speechText, lesson?.language || 'en', () => {
          setTeacherMood('questioning');
          setPedagogicalState('CHECKING_UNDERSTANDING');
        });
      }
    }
  }, [currentStepIndex, lesson?.language]);

  const handleToggleVoice = () => {
    if (isSpeaking) {
      voiceManager.stopSpeaking();
      setIsVoiceEnabled(false);
    } else {
      setIsVoiceEnabled(true);
      const textToSpeak = teacherDialogueText || currentStep?.explanation;
      if (textToSpeak) {
        voiceManager.speak(textToSpeak, lesson?.language || 'en');
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
      setAdaptiveDecision(interaction.adaptive_decision);

      const evalFeedback = interaction.evaluation?.feedback || '';
      const remedialText = interaction.adaptive_decision?.remedial_explanation || '';
      const fullResponse = evalFeedback && remedialText
        ? `${evalFeedback}\n\n${remedialText}`
        : (evalFeedback || remedialText || 'Good effort on this checkpoint!');

      if (interaction.evaluation.is_correct) {
        setTeacherDialogueTitle('Prof. Elena: Great Insight!');
        setTeacherDialogueText(fullResponse);
        setTeacherDialogueAnalogy(null);
        setActiveTab('feedback');

        if (interaction.evaluation.score >= 0.85) {
          setPedagogicalState('MASTERY_ACHIEVED');
          setTeacherMood('praising');
        } else {
          setPedagogicalState('CONTINUE');
          setTeacherMood('praising');
        }
        setActiveMisconception(null);

        if (isVoiceEnabled) {
          voiceManager.speak(fullResponse, lesson.language);
        }
      } else {
        setTeacherDialogueTitle('Prof. Elena: Conceptual Guidance');
        setTeacherDialogueText(fullResponse);
        setTeacherDialogueAnalogy(interaction.misconception?.pedagogical_analogy || null);
        setActiveTab('feedback');

        setPedagogicalState('DIAGNOSING');
        setTimeout(() => setPedagogicalState('RE_TEACHING'), 800);
        setTeacherMood('remedial');
        setActiveMisconception(interaction.misconception);

        if (isVoiceEnabled) {
          voiceManager.speak(fullResponse, lesson.language);
        }
      }
    } catch (err) {
      console.error('Answer evaluation error:', err);
    } finally {
      setIsSubmittingAnswer(false);
    }
  };

  const handleAskDoubt = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!doubtInput.trim() || !lesson || isAskingDoubt) return;

    const questionText = doubtInput.trim();
    setDoubtInput('');
    setIsAskingDoubt(true);
    setTeacherMood('explaining');

    try {
      const res = await lessonService.askTeacher({
        lesson_id: lesson.id,
        step_id: currentStep?.id,
        question: questionText,
        language: lesson.language || 'en',
      });

      setTeacherDialogueTitle(`Prof. Elena: Doubt Cleared`);
      setTeacherDialogueText(`**Q:** "${questionText}"\n\n**Prof. Elena:** ${res.answer}`);
      setTeacherDialogueAnalogy(null);
      setActiveTab('feedback');

      if (isVoiceEnabled) {
        voiceManager.speak(res.answer, lesson.language || 'en');
      }
    } catch (err) {
      console.error('Error asking doubt:', err);
      setTeacherDialogueText('I apologize, I had a momentary connection issue. Please feel free to ask again!');
    } finally {
      setIsAskingDoubt(false);
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

          <div className="classroom-top-actions flex items-center gap-2 sm:gap-3">
            {/* AI YouTube Learning Video Button */}
            <button
              className="flex items-center gap-1.5 px-3 py-1.5 bg-red-600/90 hover:bg-red-500 text-white rounded-lg text-xs font-semibold shadow-md transition-all border border-red-500/40"
              onClick={() => setShowYtModal(true)}
              title="Find Best YouTube Learning Video for this Concept"
            >
              <Youtube size={14} />
              <span>YouTube Video</span>
            </button>

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

            {/* Dynamic Teacher Dialogue Box with Tabs */}
            <div className="teacher-speech-bubble bg-slate-800/90 border border-slate-700/80 rounded-xl p-4 shadow-xl">
              <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-700/60">
                <div className="flex items-center gap-2">
                  <Sparkles size={16} className="text-blue-400" />
                  <span className="font-semibold text-sm text-slate-200">{teacherDialogueTitle}</span>
                </div>
                <div className="flex items-center gap-1.5 bg-slate-900/80 p-1 rounded-lg border border-slate-700/50 text-xs">
                  <button
                    type="button"
                    className={`px-2 py-0.5 rounded transition-colors ${activeTab === 'concept' ? 'bg-blue-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'}`}
                    onClick={() => setActiveTab('concept')}
                  >
                    Concept
                  </button>
                  <button
                    type="button"
                    className={`px-2 py-0.5 rounded transition-colors ${activeTab === 'feedback' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'}`}
                    onClick={() => setActiveTab('feedback')}
                  >
                    Teacher Feedback
                  </button>
                  <button
                    type="button"
                    className={`px-2 py-0.5 rounded transition-colors ${activeTab === 'ask' ? 'bg-cyan-600 text-white font-medium' : 'text-slate-400 hover:text-slate-200'}`}
                    onClick={() => setActiveTab('ask')}
                  >
                    Ask Doubt
                  </button>
                </div>
              </div>

              {/* Tab 1: Concept Explanation */}
              {activeTab === 'concept' && (
                <div>
                  <p className="bubble-text text-sm leading-relaxed text-slate-300">{currentStep.explanation}</p>
                  {currentStep.analogy && (
                    <div className="bubble-analogy mt-3 flex items-start gap-2.5 bg-amber-500/10 border border-amber-500/20 p-2.5 rounded-lg text-amber-200 text-xs">
                      <Lightbulb size={16} className="text-amber-400 flex-shrink-0 mt-0.5" />
                      <span><strong>Intuition:</strong> {currentStep.analogy}</span>
                    </div>
                  )}
                </div>
              )}

              {/* Tab 2: Dynamic Teacher Feedback / Dialogue */}
              {activeTab === 'feedback' && (
                <div>
                  <div className="text-sm leading-relaxed text-slate-200 whitespace-pre-line bg-slate-900/60 p-3 rounded-lg border border-slate-700/50">
                    {teacherDialogueText || "Submit your answer below to receive personalized guidance and feedback from Prof. Elena!"}
                  </div>
                  {teacherDialogueAnalogy && (
                    <div className="mt-2.5 flex items-start gap-2 bg-indigo-500/10 border border-indigo-500/20 p-2.5 rounded-lg text-indigo-200 text-xs">
                      <Lightbulb size={15} className="text-indigo-400 flex-shrink-0 mt-0.5" />
                      <span><strong>Remedial Intuition:</strong> {teacherDialogueAnalogy}</span>
                    </div>
                  )}
                  {teacherDialogueText && (
                    <button
                      type="button"
                      onClick={() => voiceManager.speak(teacherDialogueText, lesson.language || 'en')}
                      className="mt-2 text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 transition-colors"
                    >
                      <Volume2 size={13} /> Listen to Prof. Elena again
                    </button>
                  )}
                </div>
              )}

              {/* Tab 3: Ask Prof. Elena a Doubt */}
              {activeTab === 'ask' && (
                <form onSubmit={handleAskDoubt} className="mt-1">
                  <p className="text-xs text-slate-400 mb-2">Have a question or confusion about <strong>{currentStep.concept}</strong>? Ask Prof. Elena directly:</p>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      className="flex-1 bg-slate-900/90 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
                      placeholder="e.g., Why doesn't the normal force cancel gravity here?"
                      value={doubtInput}
                      onChange={(e) => setDoubtInput(e.target.value)}
                      disabled={isAskingDoubt}
                    />
                    <button
                      type="submit"
                      disabled={!doubtInput.trim() || isAskingDoubt}
                      className="px-3 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white rounded-lg text-xs font-semibold flex items-center gap-1 shadow transition-colors"
                    >
                      <span>{isAskingDoubt ? 'Thinking...' : 'Ask'}</span>
                    </button>
                  </div>
                </form>
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

      {/* YouTube Recommendation Modal */}
      {showYtModal && (
        <YouTubeRecommendationModal
          initialTopic={`${currentStep.concept} (${lesson.topic})`}
          initialDurationMinutes={lesson.duration_minutes || 20}
          onClose={() => setShowYtModal(false)}
        />
      )}
    </div>
  );
};
