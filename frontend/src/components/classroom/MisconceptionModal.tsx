import React from 'react';
import { MisconceptionResult, AdaptiveDecision } from '../../types';
import { AlertTriangle, Lightbulb, ArrowRight, Compass } from 'lucide-react';

interface MisconceptionModalProps {
  misconception: MisconceptionResult;
  adaptiveDecision: AdaptiveDecision;
  onContinue: () => void;
}

export const MisconceptionModal: React.FC<MisconceptionModalProps> = ({
  misconception,
  adaptiveDecision,
  onContinue,
}) => {
  return (
    <div className="misconception-card animate-fade-in">
      <div className="misc-header">
        <div className="flex items-center gap-2">
          <div className="misc-icon-box">
            <AlertTriangle size={20} className="text-amber-400" />
          </div>
          <div>
            <h4 className="misc-title">
              {misconception.misconception_title || 'Conceptual Gap Detected'}
            </h4>
            <span className="misc-badge">Pedagogical Remediation Active</span>
          </div>
        </div>
      </div>

      <div className="misc-body">
        {misconception.root_cause && (
          <div className="misc-root-cause">
            <strong>Underlying Mental Model:</strong> {misconception.root_cause}
          </div>
        )}

        {adaptiveDecision.remedial_explanation && (
          <div className="remedial-box">
            <div className="flex items-start gap-2">
              <Lightbulb size={20} className="text-yellow-400 mt-1 flex-shrink-0" />
              <div className="remedial-text">
                {adaptiveDecision.remedial_explanation}
              </div>
            </div>
          </div>
        )}

        {adaptiveDecision.next_question && (
          <div className="followup-challenge-notice">
            <Compass size={16} className="text-blue-400" />
            <span>A formative intuition check has been generated for you below.</span>
          </div>
        )}
      </div>

      <div className="misc-footer">
        <button className="btn-primary" onClick={onContinue}>
          <span>Try Follow-up Challenge</span>
          <ArrowRight size={16} />
        </button>
      </div>
    </div>
  );
};
