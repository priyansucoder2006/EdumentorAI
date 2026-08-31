import { apiRequest } from './api';
import { DocumentItem } from '../types';

export const documentService = {
  getDocuments: async (): Promise<DocumentItem[]> => {
    return apiRequest<DocumentItem[]>('/documents');
  },

  uploadDocument: async (file: File, language: string = 'en'): Promise<DocumentItem> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('language', language);

    return apiRequest<DocumentItem>('/documents/upload', {
      method: 'POST',
      body: formData,
    });
  },

  deleteDocument: async (id: string): Promise<{ success: boolean }> => {
    return apiRequest<{ success: boolean }>(`/documents/${id}`, {
      method: 'DELETE',
    });
  },

  queryRAG: async (query: string, documentId?: string): Promise<any> => {
    return apiRequest<any>('/rag/query', {
      method: 'POST',
      body: JSON.stringify({ query, document_id: documentId }),
    });
  },
};
