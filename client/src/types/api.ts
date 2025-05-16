export interface TaskResponse {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message?: string;
}

export interface ProcessResult {
  task_id: string;
  status: 'completed';
  filename: string;
  result: {
    original_filename: string;
    annotated_image: string;
    recognized_braille: string;
    recognized_text: string;
  };
}
