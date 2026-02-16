import React from 'react';
import { type JobStatusResponse } from '../api/client';

interface ResultViewerProps {
  jobStatus: JobStatusResponse;
}

export const ResultViewer: React.FC<ResultViewerProps> = ({ jobStatus }) => {
  const { status, result, error } = jobStatus;

  if (status === 'pending' || status === 'processing') {
    return (
      <div className="result-viewer loading">
        <div className="spinner" />
        <p>
          Processing your image...
          <br />
          <small>Status: {status}</small>
        </p>
      </div>
    );
  }

  if (status === 'failed') {
    return (
      <div className="result-viewer error">
        <h3>Processing Failed</h3>
        <p>{error || 'An unknown error occurred'}</p>
      </div>
    );
  }

  if (status === 'success' && result) {
    return (
      <div className="result-viewer success">
        <h2>Results</h2>

        <div className="result-section">
          <h3>Annotated Image</h3>
          <img
            src={result.annotated_image_url}
            alt="Annotated result"
            className="result-image"
          />
        </div>

        <div className="result-section">
          <h3>
            Classification: <span className="classification">{result.classification}</span>
          </h3>
          <p>Confidence: {(result.confidence * 100).toFixed(1)}%</p>
        </div>

        <div className="result-section">
          <h3>Extracted Text</h3>
          <div className="text-output">{result.extracted_text}</div>
        </div>

        <div className="result-section">
          <h3>Bounding Boxes ({result.bounding_boxes.length})</h3>
          <div className="boxes-list">
            {result.bounding_boxes.map((box, idx) => (
              <div key={idx} className="box-item">
                <div className="box-text">{box.text}</div>
                <div className="box-confidence">
                  {(box.confidence * 100).toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return null;
};
