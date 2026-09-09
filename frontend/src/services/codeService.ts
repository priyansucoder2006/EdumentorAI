import { apiRequest } from './api';
import { CodeExecutionResponse, LanguageItem } from '../types';

export const codeService = {
  async executeCode(
    language: string,
    sourceCode: string,
    stdin: string = ''
  ): Promise<CodeExecutionResponse> {
    return apiRequest<CodeExecutionResponse>('/code/execute', {
      method: 'POST',
      body: JSON.stringify({
        language,
        sourceCode,
        stdin,
      }),
    });
  },

  async getLanguages(): Promise<LanguageItem[]> {
    return apiRequest<LanguageItem[]>('/code/languages');
  },

  async checkHealth(): Promise<{ status: string; message: string; languages_count: number }> {
    return apiRequest('/code/health');
  },
};
