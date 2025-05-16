import { useState, useEffect } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import ImageUploader from '../components/ImageUploader.js';
import ResultDisplay from '../components/ResultDisplay.js';
import { uploadImage, checkTaskStatus, getTaskResult } from '../services/api.js';
import type { ProcessResult, TaskResponse } from '../types/api.js';

const OCRPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [currentTask, setCurrentTask] = useState<TaskResponse | null>(null);
  const [result, setResult] = useState<ProcessResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let intervalId: number;

    const pollTaskStatus = async (taskId: string) => {
      try {
        const status = await checkTaskStatus(taskId);
        
        if (status.status === 'completed') {
          const result = await getTaskResult(taskId);
          setResult(result);
          setIsLoading(false);
          setCurrentTask(null);
          clearInterval(intervalId);
        } else if (status.status === 'failed') {
          setError('Processing failed. Please try again.');
          setIsLoading(false);
          setCurrentTask(null);
          clearInterval(intervalId);
        }
      } catch (error) {
        setError('Error checking task status');
        setIsLoading(false);
        setCurrentTask(null);
        clearInterval(intervalId);
      }
    };

    if (currentTask?.task_id) {
      intervalId = setInterval(() => pollTaskStatus(currentTask.task_id), 2000);
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [currentTask]);

  const handleImageSelected = async (file: File) => {
    try {
      setIsLoading(true);
      setError(null);
      setResult(null);

      const response = await uploadImage(file);
      setCurrentTask(response);
    } catch (error) {
      setError('Error uploading image');
      setIsLoading(false);
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      {error && (
        <Typography color="error" align="center" gutterBottom>
          {error}
        </Typography>
      )}

      {!result && (
        <ImageUploader
          onImageSelected={handleImageSelected}
          isLoading={isLoading}
        />
      )}

      {isLoading && !result && (
        <Box sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 2,
          mt: 4
        }}>
          <CircularProgress />
          <Typography>
            Processing image...
          </Typography>
        </Box>
      )}

      {result && (
        <ResultDisplay 
          result={result} 
          onBack={() => {
            setResult(null);
            setError(null);
          }} 
        />
      )}
    </Box>
  );
};

export default OCRPage;
