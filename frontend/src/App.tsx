import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/common/Navbar';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { LessonCreatorPage } from './pages/LessonCreatorPage';
import { ClassroomPage } from './pages/ClassroomPage';
import { AssessmentPage } from './pages/AssessmentPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { LearningPathsPage } from './pages/LearningPathsPage';
import { RevisionPage } from './pages/RevisionPage';
import { DiagnosticsPage } from './pages/DiagnosticsPage';
import './App.css';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="global-loading-screen">
        <span className="spinner-lg" />
        <p>Loading EduMentor AI...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

export const AppContent: React.FC = () => {
  return (
    <div className="app-root-layout">
      <Navbar />
      <div className="app-main-content">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/create-lesson"
            element={
              <ProtectedRoute>
                <LessonCreatorPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/classroom/:id"
            element={
              <ProtectedRoute>
                <ClassroomPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/assessment/:lessonId"
            element={
              <ProtectedRoute>
                <AssessmentPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/documents"
            element={
              <ProtectedRoute>
                <DocumentsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/analytics"
            element={
              <ProtectedRoute>
                <AnalyticsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/learning-paths"
            element={
              <ProtectedRoute>
                <LearningPathsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/revision"
            element={
              <ProtectedRoute>
                <RevisionPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/diagnostics"
            element={
              <ProtectedRoute>
                <DiagnosticsPage />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
};

export default App;
