import React, { useEffect, useRef } from 'react';
import { Sparkles, Volume2, HelpCircle, CheckCircle2, AlertCircle } from 'lucide-react';

interface AvatarTeacherProps {
  isSpeaking: boolean;
  teacherMood?: 'explaining' | 'questioning' | 'praising' | 'remedial' | 'idle';
  language?: string;
  currentConcept?: string;
}

export const AvatarTeacher: React.FC<AvatarTeacherProps> = ({
  isSpeaking,
  teacherMood = 'explaining',
  language = 'en',
  currentConcept,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animFrameRef = useRef<number | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let time = 0;
    let mouthOpen = 0;
    let eyeBlink = 0;

    const render = () => {
      time += 0.05;
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const centerX = canvas.width / 2;
      const centerY = 130;

      // 1. Soft Ambient Halo
      const gradient = ctx.createRadialGradient(centerX, centerY, 40, centerX, centerY, 140);
      gradient.addColorStop(0, 'rgba(59, 130, 246, 0.25)');
      gradient.addColorStop(1, 'rgba(15, 23, 42, 0)');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Subtle Head Bobbing
      const bobY = Math.sin(time * 1.5) * 3;

      // 2. Shoulders / Torso
      ctx.fillStyle = '#1e293b';
      ctx.beginPath();
      ctx.ellipse(centerX, centerY + 120 + bobY, 75, 45, 0, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#3b82f6';
      ctx.beginPath();
      ctx.ellipse(centerX, centerY + 135 + bobY, 40, 25, 0, 0, Math.PI * 2);
      ctx.fill();

      // 3. Neck
      ctx.fillStyle = '#fbcfe8';
      ctx.fillRect(centerX - 14, centerY + 45 + bobY, 28, 25);

      // 4. Head (Face Oval)
      ctx.fillStyle = '#fde047'; // Stylized friendly avatar tone or warm skin tone
      ctx.fillStyle = '#fcd34d';
      ctx.beginPath();
      ctx.ellipse(centerX, centerY + bobY, 52, 60, 0, 0, Math.PI * 2);
      ctx.fill();

      // 5. Hair
      ctx.fillStyle = '#334155';
      ctx.beginPath();
      ctx.arc(centerX, centerY - 15 + bobY, 56, Math.PI * 0.8, Math.PI * 2.2);
      ctx.fill();

      // Hair bun / side style
      ctx.beginPath();
      ctx.arc(centerX - 48, centerY - 10 + bobY, 18, 0, Math.PI * 2);
      ctx.arc(centerX + 48, centerY - 10 + bobY, 18, 0, Math.PI * 2);
      ctx.fill();

      // 6. Eyes (With Natural Blinking)
      if (Math.sin(time * 0.4) > 0.96) {
        eyeBlink = 1;
      } else {
        eyeBlink = 0;
      }

      ctx.fillStyle = '#0f172a';
      if (eyeBlink === 1) {
        // Closed eyelid curve
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(centerX - 20, centerY - 5 + bobY, 8, 0, Math.PI);
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(centerX + 20, centerY - 5 + bobY, 8, 0, Math.PI);
        ctx.stroke();
      } else {
        // Open expressive eyes
        ctx.beginPath();
        ctx.arc(centerX - 20, centerY - 5 + bobY, 7, 0, Math.PI * 2);
        ctx.arc(centerX + 20, centerY - 5 + bobY, 7, 0, Math.PI * 2);
        ctx.fill();

        // Eye glint
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(centerX - 18, centerY - 7 + bobY, 2.5, 0, Math.PI * 2);
        ctx.arc(centerX + 22, centerY - 7 + bobY, 2.5, 0, Math.PI * 2);
        ctx.fill();
      }

      // 7. Eyebrows (Mood aware)
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      if (teacherMood === 'questioning') {
        // One raised eyebrow
        ctx.arc(centerX - 20, centerY - 24 + bobY, 10, Math.PI * 1.1, Math.PI * 1.9);
        ctx.arc(centerX + 20, centerY - 18 + bobY, 10, Math.PI * 1.2, Math.PI * 1.8);
      } else if (teacherMood === 'remedial') {
        // Empathetic comforting curve
        ctx.arc(centerX - 20, centerY - 17 + bobY, 10, Math.PI * 1.25, Math.PI * 1.75);
        ctx.arc(centerX + 20, centerY - 17 + bobY, 10, Math.PI * 1.25, Math.PI * 1.75);
      } else {
        ctx.arc(centerX - 20, centerY - 19 + bobY, 10, Math.PI * 1.2, Math.PI * 1.8);
        ctx.arc(centerX + 20, centerY - 19 + bobY, 10, Math.PI * 1.2, Math.PI * 1.8);
      }
      ctx.stroke();

      // 8. Glasses (Intellectual teacher look)
      ctx.strokeStyle = '#0284c7';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(centerX - 20, centerY - 5 + bobY, 14, 0, Math.PI * 2);
      ctx.arc(centerX + 20, centerY - 5 + bobY, 14, 0, Math.PI * 2);
      ctx.moveTo(centerX - 6, centerY - 5 + bobY);
      ctx.lineTo(centerX + 6, centerY - 5 + bobY);
      ctx.stroke();

      // 9. Mouth (Animated Lip-Sync when Speaking)
      if (isSpeaking) {
        mouthOpen = (Math.sin(time * 12) + 1) * 5 + 3;
      } else {
        mouthOpen = 2;
      }

      ctx.fillStyle = '#e11d48';
      ctx.beginPath();
      if (teacherMood === 'praising') {
        // Big smile
        ctx.ellipse(centerX, centerY + 28 + bobY, 14, Math.max(4, mouthOpen), 0, 0, Math.PI);
      } else {
        ctx.ellipse(centerX, centerY + 28 + bobY, 10, Math.max(3, mouthOpen), 0, 0, Math.PI * 2);
      }
      ctx.fill();

      // 10. Voice Audio Waves (when speaking)
      if (isSpeaking) {
        ctx.strokeStyle = 'rgba(59, 130, 246, 0.7)';
        ctx.lineWidth = 2;
        for (let i = 0; i < 4; i++) {
          const waveRadius = 75 + i * 18 + ((time * 30) % 25);
          const alpha = Math.max(0, 1 - (waveRadius - 75) / 60);
          ctx.strokeStyle = `rgba(59, 130, 246, ${alpha * 0.5})`;
          ctx.beginPath();
          ctx.arc(centerX, centerY + bobY, waveRadius, -Math.PI * 0.3, Math.PI * 0.3);
          ctx.stroke();
        }
      }

      animFrameRef.current = requestAnimationFrame(render);
    };

    animFrameRef.current = requestAnimationFrame(render);

    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
    };
  }, [isSpeaking, teacherMood]);

  const getMoodBadge = () => {
    switch (teacherMood) {
      case 'questioning':
        return <span className="mood-badge questioning"><HelpCircle size={12} /> Checking Understanding</span>;
      case 'praising':
        return <span className="mood-badge praising"><CheckCircle2 size={12} /> Outstanding!</span>;
      case 'remedial':
        return <span className="mood-badge remedial"><AlertCircle size={12} /> Explaining Intuition</span>;
      default:
        return <span className="mood-badge explaining"><Sparkles size={12} /> Teaching</span>;
    }
  };

  return (
    <div className="avatar-teacher-card">
      <div className="avatar-canvas-box">
        <canvas ref={canvasRef} width={280} height={250} className="avatar-canvas" />
        <div className="avatar-overlay-badge">{getMoodBadge()}</div>
      </div>

      <div className="teacher-info-bar">
        <div className="teacher-name-group">
          <span className="teacher-title">Prof. Elena</span>
          <span className="teacher-role">Adaptive AI Master Teacher</span>
        </div>
        {isSpeaking && (
          <div className="speaking-indicator">
            <Volume2 size={16} className="pulse-icon text-blue-400" />
            <span className="text-xs text-blue-400">Speaking...</span>
          </div>
        )}
      </div>
    </div>
  );
};
