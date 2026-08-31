import React from 'react';
import { MathRenderer } from '../visual_renderers/MathRenderer';
import { CodeRunner } from '../visual_renderers/CodeRunner';
import { GraphRenderer } from '../visual_renderers/GraphRenderer';
import { DiagramRenderer } from '../visual_renderers/DiagramRenderer';
import { PhysicsSim } from '../visual_renderers/PhysicsSim';
import { VisualData } from '../../types';
import { BookOpen, Lightbulb } from 'lucide-react';

interface VisualBoardProps {
  visualType: string;
  visualData: Record<string, any>;
  concept: string;
  analogy?: string;
}

export const VisualBoard: React.FC<VisualBoardProps> = ({
  visualType,
  visualData,
  concept,
  analogy,
}) => {
  const vType = (visualType || 'none').toLowerCase();
  const vData = visualData?.data || visualData || {};
  const title = visualData?.title || concept;
  const caption = visualData?.caption;

  switch (vType) {
    case 'math':
      return (
        <MathRenderer
          title={title}
          equation={vData.equation || vData.formula}
          steps={vData.steps || []}
          caption={caption}
        />
      );

    case 'code':
      return (
        <CodeRunner
          title={title}
          initialCode={vData.code}
          language={vData.language || 'typescript'}
          expectedOutput={vData.output}
        />
      );

    case 'graph':
      return (
        <GraphRenderer
          title={title}
          dataPoints={vData.points || vData.dataPoints}
          xLabel={vData.xLabel}
          yLabel={vData.yLabel}
          caption={caption}
        />
      );

    case 'physics_sim':
      return (
        <PhysicsSim
          title={title}
          data={vData}
          caption={caption}
        />
      );

    case 'diagram':
      return (
        <DiagramRenderer
          title={title}
          data={vData}
          caption={caption}
        />
      );

    default:
      return (
        <div className="default-visual-card">
          <div className="visual-header">
            <span className="visual-badge concept">Key Concept</span>
            <h4>{concept}</h4>
          </div>
          <div className="concept-highlight-box">
            <div className="concept-icon"><BookOpen size={24} /></div>
            <div className="concept-content">
              <h5>Foundational Principle</h5>
              <p>Explore this concept through progressive interactive inquiry and demonstration.</p>
            </div>
          </div>
          {analogy && (
            <div className="analogy-box">
              <Lightbulb size={18} className="text-amber-400" />
              <div>
                <strong>Intuition Analogy:</strong> {analogy}
              </div>
            </div>
          )}
        </div>
      );
  }
};
