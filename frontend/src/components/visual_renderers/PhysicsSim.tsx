import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, Zap } from 'lucide-react';

interface PhysicsSimProps {
  title?: string;
  data?: Record<string, any>;
  caption?: string;
}

export const PhysicsSim: React.FC<PhysicsSimProps> = ({
  title = "Newton's First & Second Law Simulation",
  data = {},
  caption = "Observe that when Net Force = 0 N, the glider glides at constant speed indefinitely.",
}) => {
  const [mass, setMass] = useState<number>(data.mass_kg || 2.0);
  const [force, setForce] = useState<number>(data.net_force_N !== undefined ? data.net_force_N : 0.0);
  const [isPlaying, setIsPlaying] = useState<boolean>(true);
  const [position, setPosition] = useState<number>(50);
  const [velocity, setVelocity] = useState<number>(data.velocity_mps || 3.0);

  const acceleration = mass > 0 ? force / mass : 0;
  const animFrameRef = useRef<number | null>(null);

  useEffect(() => {
    let lastTime = performance.now();

    const updatePhysics = (time: number) => {
      const dt = (time - lastTime) / 1000;
      lastTime = time;

      if (isPlaying) {
        setVelocity((v) => v + acceleration * dt);
        setPosition((p) => {
          let newP = p + velocity * dt * 25;
          // Wrap around track
          if (newP > 480) newP = 20;
          if (newP < 20) newP = 480;
          return newP;
        });
      }

      animFrameRef.current = requestAnimationFrame(updatePhysics);
    };

    animFrameRef.current = requestAnimationFrame(updatePhysics);

    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [isPlaying, acceleration, velocity]);

  const handleReset = () => {
    setPosition(50);
    setVelocity(3.0);
    setForce(0.0);
    setMass(2.0);
  };

  return (
    <div className="physics-sim-card">
      <div className="visual-header">
        <div className="flex items-center gap-2">
          <span className="visual-badge physics">Physics Simulation</span>
          <h4>{title}</h4>
        </div>
        <div className="sim-controls">
          <button
            className="btn-secondary btn-sm"
            onClick={() => setIsPlaying(!isPlaying)}
            title={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? <Pause size={14} /> : <Play size={14} />} {isPlaying ? 'Pause' : 'Play'}
          </button>
          <button className="btn-secondary btn-sm" onClick={handleReset} title="Reset">
            <RotateCcw size={14} /> Reset
          </button>
        </div>
      </div>

      {/* SVG Interactive Track */}
      <div className="sim-canvas-wrapper">
        <svg viewBox="0 0 520 180" className="sim-svg">
          {/* Air Track Bed */}
          <rect x="20" y="110" width="480" height="16" rx="4" fill="#334155" />
          <line x1="20" y1="126" x2="500" y2="126" stroke="#475569" strokeWidth="4" />
          
          {/* Tick marks */}
          {[50, 100, 150, 200, 250, 300, 350, 400, 450].map((x) => (
            <line key={x} x1={x} y1="110" x2={x} y2="118" stroke="#64748b" strokeWidth="2" />
          ))}

          {/* Glider Object */}
          <g transform={`translate(${position}, 70)`}>
            <rect x="0" y="0" width="60" height="38" rx="6" fill="#3b82f6" stroke="#60a5fa" strokeWidth="2" />
            <text x="30" y="24" fill="#ffffff" fontSize="11" fontWeight="bold" textAnchor="middle">
              {mass} kg
            </text>

            {/* Velocity Vector Arrow */}
            {velocity !== 0 && (
              <g transform="translate(60, 19)">
                <line
                  x1="0"
                  y1="0"
                  x2={Math.min(60, velocity * 10)}
                  y2="0"
                  stroke="#10b981"
                  strokeWidth="3"
                  markerEnd="url(#arrow-vel)"
                />
                <text x={Math.min(60, velocity * 10) + 6} y="4" fill="#10b981" fontSize="10" fontWeight="bold">
                  v={velocity.toFixed(1)} m/s
                </text>
              </g>
            )}

            {/* Force Vector Arrow */}
            {force !== 0 && (
              <g transform="translate(30, -10)">
                <line
                  x1="0"
                  y1="0"
                  x2={force * 8}
                  y2="0"
                  stroke="#ef4444"
                  strokeWidth="3"
                />
                <text x={force > 0 ? force * 8 + 6 : force * 8 - 30} y="-4" fill="#ef4444" fontSize="10" fontWeight="bold">
                  F={force} N
                </text>
              </g>
            )}
          </g>
        </svg>
      </div>

      {/* Interactive Controls & Telemetry */}
      <div className="sim-sliders-grid">
        <div className="slider-control">
          <label>
            Net Applied Force (F): <strong>{force} N</strong>
          </label>
          <input
            type="range"
            min="-10"
            max="10"
            step="1"
            value={force}
            onChange={(e) => setForce(parseFloat(e.target.value))}
          />
        </div>

        <div className="slider-control">
          <label>
            Glider Mass (m): <strong>{mass} kg</strong>
          </label>
          <input
            type="range"
            min="0.5"
            max="10"
            step="0.5"
            value={mass}
            onChange={(e) => setMass(parseFloat(e.target.value))}
          />
        </div>
      </div>

      {/* Calculated Physical Gauges */}
      <div className="sim-telemetry-strip">
        <div className="telemetry-item">
          <span className="telemetry-label">Acceleration (a = F/m):</span>
          <span className="telemetry-val">{acceleration.toFixed(2)} m/s²</span>
        </div>
        <div className="telemetry-item">
          <span className="telemetry-label">Velocity (v):</span>
          <span className="telemetry-val text-emerald">{velocity.toFixed(2)} m/s</span>
        </div>
        <div className="telemetry-item">
          <span className="telemetry-label">Inertial State:</span>
          <span className="telemetry-val text-cyan">
            {force === 0 ? 'Uniform Motion (1st Law)' : 'Accelerated Motion (2nd Law)'}
          </span>
        </div>
      </div>

      {caption && <div className="visual-caption">{caption}</div>}
    </div>
  );
};
