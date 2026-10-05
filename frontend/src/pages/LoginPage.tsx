import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { GraduationCap, Lock, Mail, ArrowRight, Sparkles } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('student@edumentor.ai');
  const [password, setPassword] = useState('password123');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login, demoLogin } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Login failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoAccess = async () => {
    setError(null);
    setLoading(true);
    try {
      await demoLogin();
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Demo login failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-wrapper">
      <div className="auth-card">
        <div className="auth-header">
          <div className="flex justify-center mb-4">
            <img 
              src="/icon-transparent.png" 
              alt="EduMentor AI" 
              className="w-20 h-20 object-contain drop-shadow-md hover:scale-105 transition-transform duration-300" 
            />
          </div>
          <h2>Welcome to EduMentor AI</h2>
          <p>Your personalized, adaptive AI teacher and mentor</p>
        </div>

        {error && <div className="auth-error-alert">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>Email Address</label>
            <div className="input-icon-wrapper">
              <Mail size={18} className="input-icon" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Password</label>
            <div className="input-icon-wrapper">
              <Lock size={18} className="input-icon" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
            </div>
          </div>

          <button type="submit" className="btn-auth-submit" disabled={loading}>
            <span>{loading ? 'Authenticating...' : 'Sign In'}</span>
            <ArrowRight size={18} />
          </button>
        </form>

        {loading && (
          <div className="text-xs text-center text-[#CC5500] animate-pulse my-2 bg-orange-brand/10 py-2 px-3 rounded-lg border border-orange-brand/20">
            ⏳ Connecting to EduMentor AI backend... Please wait (Render free tier may take 15–30s if waking up from idle).
          </div>
        )}

        <button
          type="button"
          onClick={handleDemoAccess}
          disabled={loading}
          className="demo-credentials-banner w-full text-left cursor-pointer hover:bg-orange-brand/15 transition-all border border-orange-brand/40"
        >
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-1.5 font-semibold text-[#CC5500]">
              <Sparkles size={14} /> Quick Demo Account (Click for Instant Access)
            </div>
            <ArrowRight size={14} className="text-[#CC5500]" />
          </div>
          <div className="text-xs text-chocolate-400">Student: <code>student@edumentor.ai</code> | Pass: <code>password123</code></div>
        </button>

        <div className="auth-footer">
          Don't have an account? <Link to="/register">Create one now</Link>
        </div>
      </div>
    </div>
  );
};
