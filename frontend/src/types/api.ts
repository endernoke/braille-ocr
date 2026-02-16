export type JobStatus = "pending" | "processing" | "success" | "failed";

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

export interface JobSubmitResponse {
  job_id: string;
  status: JobStatus;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  result?: JobResult | null;
  error?: string | null;
  created_at?: string | null;
  completed_at?: string | null;
}
