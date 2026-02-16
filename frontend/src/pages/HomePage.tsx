import React, { useState } from 'react';
import { ImageUploader } from '../components/ImageUploader';
import { ResultViewer } from '../components/ResultViewer';
import { useJobPolling } from '../hooks/useJobPolling';

export const HomePage: React.FC = () => {
  const [jobId, setJobId] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [, setUploadedFile] = useState<File | null>(null);

  const { data: jobStatus, error: pollingError } = useJobPolling(jobId);

  const handleUploadStart = (file: File) => {
    setUploadedFile(file);
    setUploadError(null);
    setJobId(null);
  };

  const handleUploadComplete = (newJobId: string) => {
    setJobId(newJobId);
  };

  const handleUploadError = (error: string) => {
    setUploadError(error);
  };

  const handleReset = () => {
    setJobId(null);
    setUploadedFile(null);
    setUploadError(null);
  };

  return (
    <div className="home-page">
      <header>
        <h1>ML OCR Application</h1>
        <p>Upload an image to extract and classify text</p>
      </header>

      <main>
        {!jobId && !uploadError && (
          <ImageUploader
            onUploadStart={handleUploadStart}
            onUploadComplete={handleUploadComplete}
            onUploadError={handleUploadError}
          />
        )}

        {uploadError && (
          <div className="error-message">
            <p>{uploadError}</p>
            <button onClick={handleReset}>Try Again</button>
          </div>
        )}

        {pollingError && (
          <div className="error-message">
            <p>Error checking job status: {pollingError}</p>
            <button onClick={handleReset}>Try Again</button>
          </div>
        )}

        {jobStatus && <ResultViewer jobStatus={jobStatus} />}

        {jobStatus?.status === 'success' && (
          <div className="actions">
            <button onClick={handleReset} className="button-primary">
              Process Another Image
            </button>
          </div>
        )}
      </main>

      <footer>
        <p>Powered by PyTorch, FastAPI, and React</p>
      </footer>
    </div>
  );
};
