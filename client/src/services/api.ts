import axios from 'axios';
import type { TaskResponse, ProcessResult } from '../types/api.js';

const API_BASE_URL = import.meta.env.VITE_API_URL || window.location.origin+'/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const uploadImage = async (file: File): Promise<TaskResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/process-image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const checkTaskStatus = async (taskId: string): Promise<TaskResponse> => {
  const response = await api.get(`/tasks/${taskId}/status`);
  return response.data;
};

export const getTaskResult = async (taskId: string): Promise<ProcessResult> => {
  const response = await api.get(`/tasks/${taskId}/result`);
  return response.data;
};
