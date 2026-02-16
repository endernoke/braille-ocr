import type { JobSubmitResponse, JobStatusResponse } from "@/types/api";

const API_BASE = "/api";

export async function submitJob(file: File): Promise<JobSubmitResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/jobs`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Upload failed (${res.status}): ${text}`);
  }

  return res.json() as Promise<JobSubmitResponse>;
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`);

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Status check failed (${res.status}): ${text}`);
  }

  return res.json() as Promise<JobStatusResponse>;
}

/**
 * Poll for job completion. Resolves when the job succeeds or rejects on failure.
 */
export function pollJobUntilDone(
  jobId: string,
  intervalMs = 1500,
  maxAttempts = 120
): Promise<JobStatusResponse> {
  return new Promise((resolve, reject) => {
    let attempts = 0;

    const poll = async () => {
      attempts++;
      try {
        const status = await getJobStatus(jobId);

        if (status.status === "success") {
          resolve(status);
          return;
        }

        if (status.status === "failed") {
          reject(new Error(status.error ?? "Job failed"));
          return;
        }

        if (attempts >= maxAttempts) {
          reject(new Error("Timed out waiting for results"));
          return;
        }

        setTimeout(poll, intervalMs);
      } catch (err) {
        reject(err);
      }
    };

    poll();
  });
}
