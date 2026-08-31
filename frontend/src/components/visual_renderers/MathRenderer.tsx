import React, { useEffect, useRef } from 'react';
import katex from 'katex';
import 'katex/dist/katex.min.css';

interface MathRendererProps {
  equation?: string;
  steps?: string[];
  title?: string;
  caption?: string;
}

export const MathRenderer: React.FC<MathRendererProps> = ({
  equation,
  steps,
  title,
  caption,
}) => {
  const eqRef = useRef<HTMLDivElement>(null);
  const stepsRefs = useRef<(HTMLDivElement | null)[]>([]);

  useEffect(() => {
    if (equation && eqRef.current) {
      try {
        katex.render(equation, eqRef.current, {
          displayMode: true,
          throwOnError: false,
        });
      } catch (e) {
        console.warn('KaTeX render error:', e);
      }
    }

    if (steps && steps.length > 0) {
      steps.forEach((step, idx) => {
        const el = stepsRefs.current[idx];
        if (el) {
          try {
            // Render inline LaTeX inside text if present
            const rendered = step.replace(/\$([^\$]+)\$/g, (_, latex) => {
              return katex.renderToString(latex, { throwOnError: false });
            });
            el.innerHTML = rendered;
          } catch {
            el.textContent = step;
          }
        }
      });
    }
  }, [equation, steps]);

  return (
    <div className="math-renderer-card">
      {title && <div className="visual-header"><span className="visual-badge">Mathematics</span><h4>{title}</h4></div>}
      
      {equation && (
        <div className="katex-main-equation" ref={eqRef} />
      )}

      {steps && steps.length > 0 && (
        <div className="math-steps-list">
          <div className="steps-label">Step-by-Step Derivation:</div>
          {steps.map((_, i) => (
            <div
              key={i}
              className="math-step-item"
              ref={(el) => (stepsRefs.current[i] = el)}
            />
          ))}
        </div>
      )}

      {caption && <div className="visual-caption">{caption}</div>}
    </div>
  );
};
