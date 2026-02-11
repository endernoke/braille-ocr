import { useState, useEffect, useCallback } from 'react';
import { apiClient, type JobStatusResponse } from '../api/client';

interface UseJobPollingResult {
  data: JobStatusResponse | null;
  error: string | null;
  isLoading: boolean;
}

export function useJobPolling(
  jobId: string | null,
  interval: number = 2000
): UseJobPollingResult {
  const [data, setData] = useState<JobStatusResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const pollStatus = useCallback(async () => {
    if (!jobId) return;

    try {
      setIsLoading(true);
      const status = await apiClient.getJobStatus(jobId);
      setData(status);
      setError(null);

      // Stop polling if job is complete
      if (status.status === 'success' || status.status === 'failed') {
        setIsLoading(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setIsLoading(false);
    }
  }, [jobId]);

  useEffect(() => {
    if (!jobId) return;

    // Initial poll
    pollStatus();

    // Set up polling interval
    const intervalId = setInterval(() => {
      if (data?.status !== 'success' && data?.status !== 'failed') {
        pollStatus();
      }
    }, interval);

    return () => clearInterval(intervalId);
  }, [jobId, interval, data?.status, pollStatus]);

  return { data, error, isLoading };
}
