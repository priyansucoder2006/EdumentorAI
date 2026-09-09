import { apiRequest } from './api';
import { LearningVideoResponse } from '../types';

export const learningVideoService = {
  async findLearningVideo(
    topic: string,
    targetDurationMinutes?: number,
    durationPreference: string = 'around',
    learnerLevel: string = 'beginner'
  ): Promise<LearningVideoResponse> {
    return apiRequest<LearningVideoResponse>('/learning/video', {
      method: 'POST',
      body: JSON.stringify({
        topic,
        targetDurationMinutes,
        durationPreference,
        learnerLevel,
      }),
    });
  },
};
