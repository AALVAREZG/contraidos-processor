/**
 * API client for backend communication
 */

import axios from 'axios';
import type {
  UploadResponse,
  AnalysisResult,
  ExportRequest,
  ExportResponse,
} from '../types';

const API_BASE = '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Upload a file for analysis
 */
export const uploadFile = async (file: File): Promise<UploadResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post<UploadResponse>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Analyze an uploaded file
 */
export const analyzeFile = async (
  uploadId: string,
  analysisType?: string
): Promise<AnalysisResult> => {
  const response = await api.post<AnalysisResult>(`/analysis/${uploadId}`, {
    analysis_type: analysisType,
  });

  return response.data;
};

/**
 * Get analysis results by ID
 */
export const getAnalysis = async (analysisId: string): Promise<AnalysisResult> => {
  const response = await api.get<AnalysisResult>(`/analysis/${analysisId}`);
  return response.data;
};

/**
 * Export analysis results
 */
export const exportAnalysis = async (
  analysisId: string,
  request: ExportRequest
): Promise<ExportResponse> => {
  const response = await api.post<ExportResponse>(
    `/export/${analysisId}`,
    request
  );
  return response.data;
};

/**
 * Download exported file
 */
export const downloadExport = (exportId: string): string => {
  return `${API_BASE}/export/download/${exportId}`;
};

export default api;
