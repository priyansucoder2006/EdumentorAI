import React from 'react';
import { GitCommit, ArrowRight, Layers } from 'lucide-react';

interface DiagramRendererProps {
  title?: string;
  mermaid?: string;
  data?: Record<string, any>;
  caption?: string;
}

export const DiagramRenderer: React.FC<DiagramRendererProps> = ({
  title = 'System Architecture & Flow',
  data = {},
  caption,
}) => {
  const steps = data.steps || [
    { title: 'Action Force', desc: 'Rocket expels high-speed gas downward (F_action)' },
    { title: 'Interaction Boundary', desc: 'Newtonian Contact Interface' },
    { title: 'Reaction Force', desc: 'Gas pushes rocket upward with equal force (F_reaction)' },
  ];

  return (
    <div className="diagram-renderer-card">
      <div className="visual-header">
        <span className="visual-badge diagram">Process Diagram</span>
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

      {caption && <div className="visual-caption">{caption}</div>}
    </div>
  );
};
