import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, LearnerProfile } from '../types';
import { authService } from '../services/authService';

interface AuthContextType {
  user: User | null;
  profile: LearnerProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, pass: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<LearnerProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const initAuth = async () => {
    const token = localStorage.getItem('edumentor_token');
    if (!token) {
      setUser(null);
      setProfile(null);
      setIsLoading(false);
      return;
    }

    try {
      const u = await authService.getMe();
      setUser(u);
      const p = await authService.getProfile();
      setProfile(p);
    } catch {
      localStorage.removeItem('edumentor_token');
      setUser(null);
      setProfile(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    initAuth();
  }, []);

  const login = async (email: string, pass: string) => {
    setIsLoading(true);
    try {
      const res = await authService.login(email, pass);
      setUser(res.user);
      const p = await authService.getProfile();
      setProfile(p);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (data: any) => {
    setIsLoading(true);
    try {
      const res = await authService.register(data);
      setUser(res.user);
      const p = await authService.getProfile();
      setProfile(p);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setProfile(null);
  };

  const refreshProfile = async () => {
    try {
      const p = await authService.getProfile();
      setProfile(p);
    } catch (e) {
      console.warn('Error refreshing profile:', e);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
