import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';

interface GraphRendererProps {
  title?: string;
  dataPoints?: Array<{ x: number | string; y: number; label?: string }>;
  xLabel?: string;
  yLabel?: string;
  caption?: string;
}

export const GraphRenderer: React.FC<GraphRendererProps> = ({
  title = 'Force vs Acceleration (F = ma)',
  dataPoints,
  xLabel = 'Acceleration (m/s²)',
  yLabel = 'Force (N)',
  caption,
}) => {
  // Default sample curve if dataPoints not supplied
  const defaultData = [
    { x: '0', y: 0, force: 0 },
    { x: '1', y: 10, force: 10 },
    { x: '2', y: 20, force: 20 },
    { x: '3', y: 30, force: 30 },
    { x: '4', y: 40, force: 40 },
    { x: '5', y: 50, force: 50 },
  ];

  const chartData = dataPoints && dataPoints.length > 0 ? dataPoints : defaultData;

  return (
    <div className="graph-renderer-card">
      <div className="visual-header">
        <span className="visual-badge graph">Analytics Graph</span>
        <h4>{title}</h4>
      </div>

      <div style={{ width: '100%', height: 220 }}>
        <ResponsiveContainer>
          <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorY" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis dataKey="x" stroke="#94a3b8" label={{ value: xLabel, position: 'insideBottomRight', offset: -5 }} />
            <YAxis stroke="#94a3b8" label={{ value: yLabel, angle: -90, position: 'insideLeft' }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px', color: '#f8fafc' }}
            />
            <Area type="monotone" dataKey="y" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorY)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {caption && <div className="visual-caption">{caption}</div>}
    </div>
  );
};
