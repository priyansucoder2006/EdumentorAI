import React, { useState } from 'react';
import { Question } from '../../types';
import { HelpCircle, Send, Mic, MicOff, Check, X, AlertCircle } from 'lucide-react';
import { voiceManager } from '../../services/voiceService';

interface QuestionEngineProps {
  question: Question;
  isSubmitting: boolean;
  onSubmitAnswer: (answerText: string, mode: string) => void;
  lastEvaluation?: any;
  language?: string;
}

export const QuestionEngine: React.FC<QuestionEngineProps> = ({
  question,
  isSubmitting,
  onSubmitAnswer,
  lastEvaluation,
  language = 'en',
}) => {
  const [selectedOption, setSelectedOption] = useState<string>('');
  const [textAnswer, setTextAnswer] = useState<string>('');
  const [isListening, setIsListening] = useState<boolean>(false);

  const isMCQ = question?.options && question.options.length > 0;

  const handleOptionSelect = (opt: string) => {
    setSelectedOption(opt);
  };

  const handleVoiceToggle = () => {
    if (isListening) {
      voiceManager.stopListening();
      setIsListening(false);
    } else {
      setIsListening(true);
      voiceManager.startListening(
        language,
        (transcript) => {
          setIsListening(false);
          setTextAnswer(transcript);
          onSubmitAnswer(transcript, 'voice');
        },
        () => setIsListening(false)
      );
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const answer = isMCQ ? selectedOption : textAnswer;
    if (!answer || answer.trim() === '') return;
    onSubmitAnswer(answer, isMCQ ? 'option_select' : 'text');
  };

  return (
    <div className="question-engine-card">
      <div className="question-header">
        <div className="flex items-center gap-2">
          <HelpCircle size={18} className="text-blue-400" />
          <span className="question-tag">Check Your Understanding</span>
        </div>
        <span className="difficulty-badge">{question?.difficulty || 'beginner'}</span>
      </div>

      <div className="question-prompt">
        {question?.prompt || 'How would you apply this concept?'}
      </div>

      <form onSubmit={handleSubmit}>
        {isMCQ ? (
          <div className="mcq-options-grid">
            {question.options!.map((opt, idx) => {
              const isSelected = selectedOption === opt;
              return (
                <button
                  type="button"
                  key={idx}
                  className={`mcq-option-btn ${isSelected ? 'selected' : ''}`}
                  onClick={() => handleOptionSelect(opt)}
                >
                  <span className="option-marker">{String.fromCharCode(65 + idx)}</span>
                  <span className="option-text">{opt}</span>
                </button>
              );
            })}
          </div>
        ) : (
          <div className="text-answer-box">
            <textarea
              className="answer-textarea"
              rows={3}
              placeholder="Type your explanation or click the microphone to speak your answer..."
              value={textAnswer}
              onChange={(e) => setTextAnswer(e.target.value)}
            />
          </div>
        )}

        <div className="question-action-bar">
          {!isMCQ && (
            <button
              type="button"
              className={`btn-voice-record ${isListening ? 'listening' : ''}`}
              onClick={handleVoiceToggle}
              title="Speak your answer"
            >
              {isListening ? <MicOff size={18} /> : <Mic size={18} />}
              <span>{isListening ? 'Listening...' : 'Voice Answer'}</span>
            </button>
          )}

          <button
            type="submit"
            className="btn-submit-answer"
            disabled={isSubmitting || (isMCQ ? !selectedOption : !textAnswer.trim())}
          >
            <Send size={16} />
            <span>{isSubmitting ? 'Evaluating...' : 'Submit Answer'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};
