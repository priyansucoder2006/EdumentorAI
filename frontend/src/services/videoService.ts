import { apiRequest } from './api';

export interface VideoJob {
  id: string;
  lesson_id: string;
  status: 'queued' | 'processing' | 'rendering' | 'completed' | 'failed';
  progress: number;
  scenes_data: Array<any>;
  video_url?: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export const videoService = {
  generateVideo: async (lessonId: string): Promise<VideoJob> => {
    return apiRequest<VideoJob>('/videos/generate', {
      method: 'POST',
      body: JSON.stringify({ lesson_id: lessonId }),
    });
  },

  getJobStatus: async (jobId: string): Promise<VideoJob> => {
    return apiRequest<VideoJob>(`/videos/${jobId}`);
  },
};
