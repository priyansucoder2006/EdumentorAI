import { apiRequest } from './api';
import { MasteryOverview, LearningPath, RecommendationItem } from '../types';

export const progressService = {
  getMasteryOverview: async (): Promise<MasteryOverview> => {
    return apiRequest<MasteryOverview>('/progress');
  },

  getLearningPaths: async (): Promise<LearningPath[]> => {
    return apiRequest<LearningPath[]>('/progress/paths');
  },

  generateRoadmap: async (data: {
    topic: string;
    duration_months?: number;
    duration_label?: string;
    hours_per_week?: number;
    current_level?: string;
    learning_goal?: string;
    target_role?: string;
  }): Promise<LearningPath> => {
    return apiRequest<LearningPath>('/progress/paths/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  updateNodeStatus: async (
    pathId: string,
    nodeId: string,
    status: 'completed' | 'in_progress' | 'locked',
    progress?: number
  ): Promise<LearningPath> => {
    return apiRequest<LearningPath>(`/progress/paths/${pathId}/node/${nodeId}`, {
      method: 'PUT',
      body: JSON.stringify({ status, progress }),
    });
  },

  deleteLearningPath: async (pathId: string): Promise<void> => {
    return apiRequest<void>(`/progress/paths/${pathId}`, {
      method: 'DELETE',
    });
  },

  getRecommendations: async (): Promise<RecommendationItem[]> => {
    return apiRequest<RecommendationItem[]>('/recommendations');
  },
};
