import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { GraduationCap, Lock, Mail, User, Globe, BookOpen, ArrowRight } from 'lucide-react';

export const RegisterPage: React.FC = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [language, setLanguage] = useState('hinglish');
  const [educationLevel, setEducationLevel] = useState('beginner');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await register({
        name,
        email,
        password,
        preferred_language: language,
        education_level: educationLevel,
      });
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-wrapper">
      <div className="auth-card">
        <div className="auth-header">
          <div className="auth-icon-badge">
            <GraduationCap size={28} className="text-blue-400" />
          </div>
          <h2>Join EduMentor AI</h2>
          <p>Set up your profile to start personalized adaptive learning</p>
        </div>

        {error && <div className="auth-error-alert">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>Full Name</label>
            <div className="input-icon-wrapper">
              <User size={18} className="input-icon" />
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Aarav Patel"
              />
            </div>
          </div>

          <div className="form-group">
            <label>Email Address</label>
            <div className="input-icon-wrapper">
              <Mail size={18} className="input-icon" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="aarav@example.com"
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

          <div className="form-row-2">
            <div className="form-group">
              <label><Globe size={14} /> Preferred Language</label>
              <select value={language} onChange={(e) => setLanguage(e.target.value)}>
                <option value="en">English</option>
                <option value="hinglish">Hinglish</option>
                <option value="hi">हिन्दी (Hindi)</option>
                <option value="bn">বাংলা (Bengali)</option>
              </select>
            </div>

            <div className="form-group">
              <label><BookOpen size={14} /> Knowledge Level</label>
              <select value={educationLevel} onChange={(e) => setEducationLevel(e.target.value)}>
                <option value="beginner">Beginner (Class 6–10)</option>
                <option value="intermediate">Intermediate (High School / UG)</option>
                <option value="advanced">Advanced (Degree / Professional)</option>
              </select>
            </div>
          </div>

          <button type="submit" className="btn-auth-submit" disabled={loading}>
            <span>{loading ? 'Creating Account...' : 'Get Started'}</span>
            <ArrowRight size={18} />
          </button>
        </form>

        <div className="auth-footer">
          Already have an account? <Link to="/login">Sign In</Link>
        </div>
      </div>
    </div>
  );
};
