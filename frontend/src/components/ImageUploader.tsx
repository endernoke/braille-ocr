import React, { useCallback, useState } from 'react';

interface ImageUploaderProps {
  onUploadStart: (file: File) => void;
  onUploadComplete: (jobId: string) => void;
  onUploadError: (error: string) => void;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  onUploadStart,
  onUploadComplete,
  onUploadError,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleFile = useCallback(
    async (file: File) => {
      if (!file.type.startsWith('image/')) {
        onUploadError('Please upload an image file');
        return;
      }

      try {
        setUploading(true);
        onUploadStart(file);

        const { apiClient } = await import('../api/client');
        const response = await apiClient.submitJob(file);

        onUploadComplete(response.job_id);
      } catch (error) {
        onUploadError(
          error instanceof Error ? error.message : 'Upload failed'
        );
      } finally {
        setUploading(false);
      }
    },
    [onUploadStart, onUploadComplete, onUploadError]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      const file = e.dataTransfer.files[0];
      if (file) {
        handleFile(file);
      }
    },
    [handleFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        handleFile(file);
      }
    },
    [handleFile]
  );

  return (
    <div
      className={`upload-zone ${isDragging ? 'dragging' : ''} ${uploading ? 'uploading' : ''}`}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
    >
      <div className="upload-content">
        <svg
          width="64"
          height="64"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
        >
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="17 8 12 3 7 8" />
          <line x1="12" y1="3" x2="12" y2="15" />
        </svg>
        <h3>{uploading ? 'Uploading...' : 'Upload an Image'}</h3>
        <p>Drag and drop or click to browse</p>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileInput}
          disabled={uploading}
          style={{ display: 'none' }}
          id="file-input"
        />
        <label htmlFor="file-input" className="button">
          Choose File
        </label>
      </div>
    </div>
  );
};
