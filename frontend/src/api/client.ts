import axios, { type AxiosInstance } from 'axios';

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
  text: string;
  confidence: number;
}

export interface JobResult {
  extracted_text: string;
  classification: string;
  confidence: number;
  bounding_boxes: BoundingBox[];
  annotated_image_url: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: 'pending' | 'processing' | 'success' | 'failed';
  result?: JobResult;
  error?: string;
  created_at?: string;
  completed_at?: string;
}

export interface JobSubmitResponse {
  job_id: string;
  status: string;
}

class APIClient {
  private client: AxiosInstance;

  constructor(baseURL: string = '/api') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  async submitJob(file: File): Promise<JobSubmitResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await this.client.post<JobSubmitResponse>(
      '/jobs',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );

    return response.data;
  }

  async getJobStatus(jobId: string): Promise<JobStatusResponse> {
    const response = await this.client.get<JobStatusResponse>(
      `/jobs/${jobId}`
    );
    return response.data;
  }

  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const apiClient = new APIClient();
