import React from 'react';
import { GitCommit, ArrowRight, Layers, Sparkles } from 'lucide-react';

interface DiagramRendererProps {
  title?: string;
  mermaid?: string;
  data?: Record<string, any>;
  caption?: string;
}

export const DiagramRenderer: React.FC<DiagramRendererProps> = ({
  title = 'System Architecture & Flow Diagram',
  data = {},
  caption,
}) => {
  // Extract steps dynamically or construct from analogy/concept
  const rawSteps = data.steps || [];
  const steps = rawSteps.length > 0
    ? rawSteps
    : [
        { title: '1. Initial State / Input', desc: data.analogy ? `Intuition Context: ${data.analogy}` : 'Baseline conditions and input parameters' },
        { title: '2. Core Interaction / Principle', desc: data.focus || data.concept || 'Governing physical, chemical, or logical rule transformation' },
        { title: '3. Observable Output / Result', desc: data.example ? `Demonstrated Result: ${data.example}` : 'Final equilibrium state and systemic response' },
      ];

  return (
    <div className="diagram-renderer-card">
      <div className="visual-header">
        <span className="visual-badge diagram">Process Flow</span>
        <h4>{title}</h4>
      </div>

      <div className="diagram-flow-container">
        {steps.map((step: any, index: number) => (
          <React.Fragment key={index}>
            <div className="flow-step-node">
              <div className="node-icon">
                <GitCommit size={18} />
              </div>
              <div className="node-content">
                <div className="node-title">{step.title}</div>
                <div className="node-desc">{step.desc || step.description}</div>
              </div>
            </div>
            {index < steps.length - 1 && (
              <div className="flow-arrow">
                <ArrowRight size={20} />
              </div>
            )}
          </React.Fragment>
        ))}
      </div>

      {data.key_rule && (
        <div className="diagram-callout">
          <Layers size={16} /> <strong>Rule:</strong> {data.key_rule}
        </div>
      )}

      {data.analogy && !data.key_rule && (
        <div className="diagram-callout">
          <Sparkles size={16} /> <strong>Intuition:</strong> {data.analogy}
        </div>
      )}

      {caption && <div className="visual-caption">{caption}</div>}
    </div>
  );
};
