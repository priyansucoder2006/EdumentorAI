import { apiRequest } from './api';
import { Lesson, Interaction, Assessment } from '../types';

export const lessonService = {
  createLesson: async (data: {
    topic: string;
    document_id?: string;
    language?: string;
    difficulty?: string;
    duration_minutes?: number;
    target_audience?: string;
    learning_goal?: string;
  }): Promise<Lesson> => {
    return apiRequest<Lesson>('/lessons', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  getLessons: async (): Promise<Lesson[]> => {
    return apiRequest<Lesson[]>('/lessons');
  },

  getLesson: async (id: string): Promise<Lesson> => {
    return apiRequest<Lesson>(`/lessons/${id}`);
  },

  advanceStep: async (lessonId: string): Promise<Lesson> => {
    return apiRequest<Lesson>(`/lessons/${lessonId}/state`, {
      method: 'POST',
      body: JSON.stringify({ action: 'next_step' }),
    });
  },

  switchLanguage: async (lessonId: string, targetLanguage: string): Promise<Lesson> => {
    return apiRequest<Lesson>(`/lessons/${lessonId}/language`, {
      method: 'POST',
      body: JSON.stringify({ target_language: targetLanguage }),
    });
  },

  submitAnswer: async (data: {
    step_id: string;
    student_answer: string;
    response_mode?: string;
  }): Promise<Interaction> => {
    return apiRequest<Interaction>('/interactions/answer', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  getInteractions: async (lessonId: string): Promise<Interaction[]> => {
    return apiRequest<Interaction[]>(`/interactions/${lessonId}`);
  },

  generateAssessment: async (lessonId: string): Promise<Assessment> => {
    return apiRequest<Assessment>('/assessments/generate', {
      method: 'POST',
      body: JSON.stringify({ lesson_id: lessonId }),
    });
  },

  submitAssessment: async (
    assessmentId: string,
    answers: Array<{ question_id: string; answer: string }>
  ): Promise<Assessment> => {
    return apiRequest<Assessment>(`/assessments/${assessmentId}/submit`, {
      method: 'POST',
      body: JSON.stringify({ answers }),
    });
  },

  getAssessment: async (assessmentId: string): Promise<Assessment> => {
    return apiRequest<Assessment>(`/assessments/${assessmentId}`);
  },
};
