import { apiRequest } from './api';
import { MasteryOverview, LearningPath, RecommendationItem } from '../types';

export const progressService = {
  getMasteryOverview: async (): Promise<MasteryOverview> => {
    return apiRequest<MasteryOverview>('/progress');
  },

  getLearningPaths: async (): Promise<LearningPath[]> => {
    return apiRequest<LearningPath[]>('/progress/paths');
  },

  getRecommendations: async (): Promise<RecommendationItem[]> => {
    return apiRequest<RecommendationItem[]>('/recommendations');
  },
};
