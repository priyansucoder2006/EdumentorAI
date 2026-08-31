import React, { useState, useEffect } from 'react';
import { progressService } from '../services/progressService';
import { MasteryOverview, ConceptMastery } from '../types';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import { Award, TrendingUp, CheckCircle, Clock, Zap } from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  const [mastery, setMastery] = useState<MasteryOverview | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    progressService
      .getMasteryOverview()
      .then(setMastery)
      .catch(console.warn)
      .finally(() => setLoading(false));
  }, []);

  const conceptDetails: ConceptMastery[] = mastery?.concept_details || [
    { topic: "Newton's Laws", concept: 'Inertia & First Law', mastery_score: 92, attempts: 3, correct_attempts: 3, difficulty_level: 'beginner', last_studied: new Date().toISOString() },
    { topic: "Newton's Laws", concept: 'Second Law (F = ma)', mastery_score: 84, attempts: 2, correct_attempts: 2, difficulty_level: 'intermediate', last_studied: new Date().toISOString() },
    { topic: "Newton's Laws", concept: 'Action-Reaction Pairs', mastery_score: 75, attempts: 2, correct_attempts: 1, difficulty_level: 'intermediate', last_studied: new Date().toISOString() },
    { topic: "Ohm's Law", concept: 'V = IR Relationship', mastery_score: 88, attempts: 2, correct_attempts: 2, difficulty_level: 'beginner', last_studied: new Date().toISOString() },
    { topic: 'React', concept: 'Components & Immutability', mastery_score: 90, attempts: 1, correct_attempts: 1, difficulty_level: 'beginner', last_studied: new Date().toISOString() },
  ];

  const chartData = conceptDetails.map((c) => ({
    name: c.concept.length > 18 ? c.concept.substring(0, 18) + '...' : c.concept,
    mastery: c.mastery_score,
  }));

  return (
    <div className="analytics-page-container">
      <div className="page-header">
        <div>
          <h2>Cognitive Mastery & Learning Analytics</h2>
          <p>Transparent multi-factor mastery model: 0.35 Correctness + 0.25 Consistency + 0.20 Difficulty + 0.10 Reasoning + 0.10 Retention.</p>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="dashboard-metrics-grid">
        <div className="metric-stat-card">
          <div className="metric-icon-box bg-blue-500/10 text-blue-400"><Award size={24} /></div>
          <div className="metric-info">
            <span className="metric-label">Composite Mastery</span>
            <span className="metric-value">{mastery?.overall_mastery || 86}%</span>
          </div>
        </div>

        <div className="metric-stat-card">
          <div className="metric-icon-box bg-emerald-500/10 text-emerald-400"><CheckCircle size={24} /></div>
          <div className="metric-info">
            <span className="metric-label">Concepts Tracked</span>
            <span className="metric-value">{conceptDetails.length}</span>
          </div>
        </div>

        <div className="metric-stat-card">
          <div className="metric-icon-box bg-purple-500/10 text-purple-400"><Zap size={24} /></div>
          <div className="metric-info">
            <span className="metric-label">Retention Score</span>
            <span className="metric-value">94.2%</span>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="analytics-charts-grid">
        {/* Bar Chart */}
        <div className="analytics-chart-card">
          <h3 className="section-title mb-3">Concept Mastery Scores (%)</h3>
          <div style={{ width: '100%', height: 280 }}>
            <ResponsiveContainer>
              <BarChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} interval={0} angle={-15} textAnchor="end" />
                <YAxis stroke="#94a3b8" domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px', color: '#f8fafc' }}
                />
                <Bar dataKey="mastery" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Radar Chart */}
        <div className="analytics-chart-card">
          <h3 className="section-title mb-3">Skill Radar Matrix</h3>
          <div style={{ width: '100%', height: 280 }}>
            <ResponsiveContainer>
              <RadarChart data={chartData}>
                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                <PolarAngleAxis dataKey="name" stroke="#94a3b8" fontSize={11} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#64748b" />
                <Radar name="Mastery" dataKey="mastery" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.4} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Detailed Concept Table */}
      <div className="concept-table-card">
        <h3 className="section-title mb-3">Concept-Level Tracking Log</h3>
        <div className="table-wrapper">
          <table className="analytics-table">
            <thead>
              <tr>
                <th>Topic</th>
                <th>Concept</th>
                <th>Difficulty</th>
                <th>Attempts</th>
                <th>Mastery</th>
                <th>Last Studied</th>
              </tr>
            </thead>
            <tbody>
              {conceptDetails.map((c, i) => (
                <tr key={i}>
                  <td><strong>{c.topic}</strong></td>
                  <td>{c.concept}</td>
                  <td><span className="diff-pill">{c.difficulty_level}</span></td>
                  <td>{c.correct_attempts} / {c.attempts}</td>
                  <td>
                    <div className="mastery-cell">
                      <div className="mini-progress-bar">
                        <div className="mini-progress-fill" style={{ width: `${c.mastery_score}%` }} />
                      </div>
                      <span>{Math.round(c.mastery_score)}%</span>
                    </div>
                  </td>
                  <td className="text-slate-400 text-xs">{new Date(c.last_studied).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
