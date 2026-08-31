import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { progressService } from '../services/progressService';
import { MasteryOverview, RecommendationItem } from '../types';
import { RotateCcw, AlertTriangle, Sparkles, ArrowRight, Lightbulb, CheckCircle } from 'lucide-react';

export const RevisionPage: React.FC = () => {
  const navigate = useNavigate();
  const [mastery, setMastery] = useState<MasteryOverview | null>(null);
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    Promise.all([
      progressService.getMasteryOverview(),
      progressService.getRecommendations(),
    ])
      .then(([m, r]) => {
        setMastery(m);
        setRecommendations(r);
      })
      .catch(console.warn)
      .finally(() => setLoading(false));
  }, []);

  const weakConcepts = mastery?.weak_topics || ['Action-Reaction Pairs', 'Inertia in Vacuum'];

  return (
    <div className="revision-page-container">
      <div className="page-header">
        <div>
          <h2>Targeted Revision & Remediation Hub</h2>
          <p>Reinforce conceptual gaps and misconceptions diagnosed during previous lessons.</p>
        </div>
      </div>

      {/* Weak Concepts Grid */}
      <div className="revision-sections-grid">
        <div className="revision-card-column">
          <h3 className="section-title flex items-center gap-2 mb-3">
            <AlertTriangle size={18} className="text-amber-400" /> Diagnosed Weak Concepts
          </h3>
          <div className="weak-concepts-cards-stack">
            {weakConcepts.map((concept, i) => (
              <div key={i} className="weak-concept-remedial-card">
                <div className="flex justify-between items-start mb-2">
                  <span className="remedial-badge">Priority Revision</span>
                  <span className="text-xs text-amber-400">Mastery: 45%</span>
                </div>
                <h4>{concept}</h4>
                <p className="remedial-hint">
                  <Lightbulb size={14} className="text-amber-400 inline mr-1" />
                  Review the core frictionless thought experiment to avoid confusing momentum with continuous force.
                </p>
                <button
                  className="btn-primary btn-sm mt-3"
                  onClick={() =>
                    navigate('/create-lesson', {
                      state: { topic: concept, duration_minutes: 5 },
                    })
                  }
                >
                  <RotateCcw size={14} /> Launch 5-min Targeted Drill
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Practice Recommendations Column */}
        <div className="revision-card-column">
          <h3 className="section-title flex items-center gap-2 mb-3">
            <Sparkles size={18} className="text-blue-400" /> AI Practice Recommendations
          </h3>
          <div className="recommendation-cards-stack">
            {recommendations.map((rec, idx) => (
              <div key={idx} className="rec-revision-card">
                <div className="flex justify-between items-center mb-1">
                  <span className="rec-type-badge">{rec.type}</span>
                  <span className="text-xs text-slate-400">{rec.estimated_minutes} mins</span>
                </div>
                <h4>{rec.topic}</h4>
                <p>{rec.reason}</p>
                <button
                  className="btn-secondary btn-sm mt-3"
                  onClick={() =>
                    navigate('/create-lesson', {
                      state: { topic: rec.topic, duration_minutes: rec.estimated_minutes },
                    })
                  }
                >
                  <span>Start Lesson</span>
                  <ArrowRight size={14} />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
