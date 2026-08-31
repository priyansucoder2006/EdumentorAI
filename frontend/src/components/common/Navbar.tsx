import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import {
  GraduationCap,
  LayoutDashboard,
  FolderOpen,
  PlusCircle,
  BarChart3,
  GitBranch,
  RotateCcw,
  Activity,
  LogOut,
  User as UserIcon,
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navLinks = [
    { path: '/dashboard', label: 'Dashboard', icon: <LayoutDashboard size={18} /> },
    { path: '/create-lesson', label: 'New Lesson', icon: <PlusCircle size={18} /> },
    { path: '/documents', label: 'Documents & RAG', icon: <FolderOpen size={18} /> },
    { path: '/learning-paths', label: 'Roadmaps', icon: <GitBranch size={18} /> },
    { path: '/analytics', label: 'Mastery Analytics', icon: <BarChart3 size={18} /> },
    { path: '/revision', label: 'Revision Hub', icon: <RotateCcw size={18} /> },
    { path: '/diagnostics', label: 'AI Trace', icon: <Activity size={18} /> },
  ];

  return (
    <header className="app-navbar">
      <div className="navbar-container">
        {/* Brand Logo */}
        <Link to="/dashboard" className="navbar-brand">
          <div className="brand-icon-box">
            <GraduationCap size={24} className="text-blue-400" />
          </div>
          <div className="brand-text-group">
            <span className="brand-title">EduMentor AI</span>
            <span className="brand-tagline">Adaptive AI Teacher</span>
          </div>
        </Link>

        {/* Navigation Links */}
        {isAuthenticated && (
          <nav className="navbar-nav">
            {navLinks.map((link) => {
              const isActive = location.pathname === link.path;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`nav-link-item ${isActive ? 'active' : ''}`}
                >
                  {link.icon}
                  <span>{link.label}</span>
                </Link>
              );
            })}
          </nav>
        )}

        {/* User Profile / Logout */}
        <div className="navbar-user-actions">
          {isAuthenticated ? (
            <div className="user-profile-menu">
              <div className="user-avatar-pill">
                <UserIcon size={16} className="text-blue-400" />
                <span className="user-name">{user?.name || 'Learner'}</span>
                <span className="user-lang-badge">{user?.preferred_language || 'en'}</span>
              </div>
              <button
                className="btn-logout"
                onClick={handleLogout}
                title="Log Out"
              >
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <div className="flex gap-2">
              <Link to="/login" className="btn-secondary btn-sm">Log In</Link>
              <Link to="/register" className="btn-primary btn-sm">Register</Link>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
