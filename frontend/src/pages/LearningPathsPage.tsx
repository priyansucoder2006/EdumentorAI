import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { progressService } from '../services/progressService';
import { LearningPath } from '../types';
import { GitBranch, CheckCircle2, Circle, Lock, ArrowRight, BookOpen, Compass } from 'lucide-react';

export const LearningPathsPage: React.FC = () => {
  const navigate = useNavigate();
  const [paths, setPaths] = useState<LearningPath[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    progressService.getLearningPaths().then(setPaths).catch(console.warn).finally(() => setLoading(false));
  }, []);

  const path = paths[0] || {
    id: 'default_path',
    topic: 'Physics & Classical Mechanics Roadmap',
    description: 'Structured progression from foundational Newtonian kinematics to planetary astrophysics.',
    progress_percentage: 45,
    nodes: [
      { id: 'n1', title: "Newton's Laws of Motion", difficulty: 'beginner', status: 'completed', progress: 100 },
      { id: 'n2', title: 'Work, Kinetic & Potential Energy', difficulty: 'intermediate', status: 'in_progress', progress: 50 },
      { id: 'n3', title: 'Conservation of Linear Momentum', difficulty: 'intermediate', status: 'locked', progress: 0 },
      { id: 'n4', title: 'Rotational Dynamics & Angular Momentum', difficulty: 'advanced', status: 'locked', progress: 0 },
      { id: 'n5', title: 'Universal Gravitation & Orbital Orbits', difficulty: 'advanced', status: 'locked', progress: 0 },
    ],
  };

  return (
    <div className="learning-paths-container">
      <div className="page-header">
        <div>
          <h2>Curriculum Learning Roadmaps</h2>
          <p>Multi-topic developmental trees with prerequisite graph mapping.</p>
        </div>
      </div>

      <div className="path-overview-card">
        <div className="flex justify-between items-start mb-4">
          <div>
            <div className="flex items-center gap-2 text-blue-400 font-semibold text-xs uppercase mb-1">
              <Compass size={16} /> Active Curriculum
            </div>
            <h3>{path.topic}</h3>
            <p className="text-slate-300 text-sm">{path.description}</p>
          </div>
          <div className="path-progress-badge">
            <span className="text-lg font-bold text-blue-400">{path.progress_percentage}%</span>
            <span className="text-xs text-slate-400">Completed</span>
          </div>
        </div>

        {/* Roadmap Nodes Timeline */}
        <div className="roadmap-dag-timeline">
          {path.nodes.map((node, idx) => {
            const isCompleted = node.status === 'completed';
            const isInProgress = node.status === 'in_progress';
            const isLocked = node.status === 'locked';

            return (
              <div
                key={node.id || idx}
                className={`roadmap-node-card ${node.status}`}
                onClick={() => {
                  if (!isLocked) {
                    navigate('/create-lesson', { state: { topic: node.title } });
                  }
                }}
              >
                <div className="node-status-indicator">
                  {isCompleted && <CheckCircle2 size={22} className="text-emerald-400" />}
                  {isInProgress && <Circle size={22} className="text-blue-400 fill-blue-400/20" />}
                  {isLocked && <Lock size={20} className="text-slate-500" />}
                </div>

                <div className="node-body">
                  <div className="flex justify-between items-center mb-1">
                    <span className="node-stage-badge">Module {idx + 1}</span>
                    <span className={`diff-tag ${node.difficulty}`}>{node.difficulty}</span>
                  </div>
                  <h4 className="node-title">{node.title}</h4>
                  <div className="node-progress-bar">
                    <div className="node-progress-fill" style={{ width: `${node.progress}%` }} />
                  </div>
                </div>

                <div className="node-action">
                  {!isLocked ? (
                    <button className="btn-primary btn-sm">
                      <span>{isCompleted ? 'Review' : 'Continue'}</span>
                      <ArrowRight size={14} />
                    </button>
                  ) : (
                    <span className="text-xs text-slate-500 flex items-center gap-1">Prerequisite required</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
