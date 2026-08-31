import React, { useState, useEffect } from 'react';
import { apiRequest } from '../services/api';
import { Activity, Server, Cpu, Database, Terminal, ShieldCheck } from 'lucide-react';

export const DiagnosticsPage: React.FC = () => {
  const [sysInfo, setSysInfo] = useState<any>(null);
  const [traces, setTraces] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    Promise.all([
      apiRequest<any>('/diagnostics/system'),
      apiRequest<any>('/diagnostics/ai-trace'),
    ])
      .then(([sys, tr]) => {
        setSysInfo(sys);
        setTraces(tr.traces || []);
      })
      .catch(console.warn)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="diagnostics-page-container">
      <div className="page-header">
        <div>
          <h2>System Diagnostics & AI Trace Observability</h2>
          <p>Developer and Judge inspection dashboard for RAG retrieval, LLM latency, and deterministic state transitions.</p>
        </div>
      </div>

      {/* System Status Grid */}
      <div className="diagnostics-sys-grid">
        <div className="diag-stat-card">
          <div className="flex items-center gap-2 text-blue-400 font-bold mb-2">
            <Server size={18} /> Application Core
          </div>
          <div className="diag-detail-row">
            <span>Status:</span>
            <span className="status-badge indexed">Online (Healthy)</span>
          </div>
          <div className="diag-detail-row">
            <span>Version:</span>
            <code>{sysInfo?.version || '1.0.0'}</code>
          </div>
          <div className="diag-detail-row">
            <span>LLM Provider:</span>
            <code className="text-blue-400">{sysInfo?.llm_provider?.toUpperCase() || 'MOCK/DEV'}</code>
          </div>
        </div>

        <div className="diag-stat-card">
          <div className="flex items-center gap-2 text-purple-400 font-bold mb-2">
            <Cpu size={18} /> Embeddings & Vector DB
          </div>
          <div className="diag-detail-row">
            <span>Embedding Model:</span>
            <code>{sysInfo?.embedding_provider || 'local (384-dim)'}</code>
          </div>
          <div className="diag-detail-row">
            <span>Chunks Indexed:</span>
            <strong>{sysInfo?.storage?.chunks_stored || 0}</strong>
          </div>
          <div className="diag-detail-row">
            <span>Documents:</span>
            <strong>{sysInfo?.storage?.documents_indexed || 0}</strong>
          </div>
        </div>

        <div className="diag-stat-card">
          <div className="flex items-center gap-2 text-emerald-400 font-bold mb-2">
            <ShieldCheck size={18} /> Pedagogical State Machine
          </div>
          <div className="diag-detail-row">
            <span>Lessons Conducted:</span>
            <strong>{sysInfo?.storage?.lessons_conducted || 0}</strong>
          </div>
          <div className="diag-detail-row">
            <span>Interactions Logged:</span>
            <strong>{sysInfo?.storage?.interactions_evaluated || 0}</strong>
          </div>
          <div className="diag-detail-row">
            <span>Adaptation Policy:</span>
            <span className="text-emerald-400 font-semibold">Deterministic Wrapper</span>
          </div>
        </div>
      </div>

      {/* AI Traces Table */}
      <div className="traces-section-card">
        <div className="flex items-center gap-2 font-bold mb-3 text-blue-400">
          <Terminal size={18} /> Recent Evaluator & Misconception Traces
        </div>

        {traces.length === 0 ? (
          <p className="text-sm text-slate-400">No interaction traces logged yet. Start a lesson to observe live traces!</p>
        ) : (
          <div className="traces-list">
            {traces.map((trace, idx) => (
              <div key={idx} className="trace-item-box">
                <div className="trace-header">
                  <span className="trace-q">Q: {trace.question}</span>
                  <span className="trace-time">{new Date(trace.created_at).toLocaleTimeString()}</span>
                </div>
                <div className="trace-ans">
                  <strong>Student Response:</strong> "{trace.student_answer}"
                </div>

                <div className="trace-meta-grid">
                  <div className="trace-meta-col">
                    <span className="text-xs text-slate-400">Evaluation:</span>
                    <div className="font-semibold text-emerald-400">
                      {trace.evaluation?.is_correct ? 'Correct (1.0)' : `Score: ${trace.evaluation?.score || 0.25}`}
                    </div>
                  </div>

                  <div className="trace-meta-col">
                    <span className="text-xs text-slate-400">Misconception:</span>
                    <div className="text-amber-400 font-medium">
                      {trace.misconception?.detected
                        ? trace.misconception?.misconception_title || 'Detected'
                        : 'None'}
                    </div>
                  </div>

                  <div className="trace-meta-col">
                    <span className="text-xs text-slate-400">Adaptive Decision:</span>
                    <div className="text-blue-400 font-semibold">
                      {trace.adaptive_decision?.action || trace.adaptive_decision}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
