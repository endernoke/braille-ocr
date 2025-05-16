import { useEffect, useRef, useState } from 'react';
import { Box, IconButton, Typography } from '@mui/material';
import { CameraAlt, Cameraswitch } from '@mui/icons-material';

interface CameraViewProps {
  onCapture: (file: File) => void;
  onClose: () => void;
}

const CameraView = ({ onCapture, onClose }: CameraViewProps) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [error, setError] = useState<string>('');
  const [facingMode, setFacingMode] = useState<'environment' | 'user'>('environment');

  useEffect(() => {
    let stream: MediaStream | null = null;

    const startCamera = async () => {
      try {
        if (stream) {
          stream.getTracks().forEach(track => track.stop());
        }

        stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode,
            width: { ideal: 1920 },
            height: { ideal: 1080 }
          },
          audio: false
        });

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        setError('Could not access camera. Please make sure you have granted camera permissions.');
        console.error('Camera error:', err);
      }
    };

    startCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [facingMode]);

  const handleCapture = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;

    // Set canvas dimensions to match video dimensions
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw the current video frame on the canvas
    const context = canvas.getContext('2d');
    if (!context) return;

    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert the canvas content to a file
    canvas.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });
        onCapture(file);
      }
    }, 'image/jpeg', 0.95);
  };

  const toggleCamera = () => {
    setFacingMode(prev => prev === 'environment' ? 'user' : 'environment');
  };

  if (error) {
    return (
      <Box sx={{
        width: '100%',
        aspectRatio: '4/3',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2,
        textAlign: 'center'
      }}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{
      width: '100%',
      aspectRatio: '4/3',
      position: 'relative',
      bgcolor: 'black',
      borderRadius: 2,
      overflow: 'hidden'
    }}>
      <video
        ref={videoRef}
        autoPlay
        playsInline
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover'
        }}
      />
      <canvas
        ref={canvasRef}
        style={{ display: 'none' }}
      />
      
      <Box sx={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        p: 2,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        gap: 2,
        backgroundColor: 'rgba(0, 0, 0, 0.5)'
      }}>
        <IconButton
          onClick={toggleCamera}
          sx={{ color: 'white' }}
        >
          <Cameraswitch />
        </IconButton>
        <IconButton
          onClick={handleCapture}
          sx={{
            width: 64,
            height: 64,
            border: '2px solid white',
            color: 'white',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.1)'
            }
          }}
        >
          <CameraAlt sx={{ fontSize: 32 }} />
        </IconButton>
      </Box>
    </Box>
  );
};

export default CameraView;
