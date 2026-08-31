import { apiRequest } from './api';
import { AuthResponse, User, LearnerProfile } from '../types';

export const authService = {
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const res = await apiRequest<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    localStorage.setItem('edumentor_token', res.access_token);
    return res;
  },

  register: async (data: {
    name: string;
    email: string;
    password: string;
    preferred_language?: string;
    education_level?: string;
  }): Promise<AuthResponse> => {
    const res = await apiRequest<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    localStorage.setItem('edumentor_token', res.access_token);
    return res;
  },

  getMe: async (): Promise<User> => {
    return apiRequest<User>('/auth/me');
  },

  getProfile: async (): Promise<LearnerProfile> => {
    return apiRequest<LearnerProfile>('/auth/profile');
  },

  updateProfile: async (data: Partial<LearnerProfile>): Promise<LearnerProfile> => {
    return apiRequest<LearnerProfile>('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  logout: () => {
    localStorage.removeItem('edumentor_token');
  },
};
