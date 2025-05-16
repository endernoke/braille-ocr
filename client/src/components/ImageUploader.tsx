import { useState } from 'react';
import { Box, Button, CircularProgress, IconButton, useMediaQuery, useTheme } from '@mui/material';
import { CameraAlt, Upload, Close } from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import CameraView from './CameraView.js';

const Input = styled('input')({
  display: 'none',
});

interface ImageUploaderProps {
  onImageSelected: (file: File) => void;
  isLoading?: boolean;
}

const ImageUploader = ({ onImageSelected, isLoading }: ImageUploaderProps) => {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [showCamera, setShowCamera] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      onImageSelected(file);
    }
  };

  const handleCameraCapture = (file: File) => {
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    onImageSelected(file);
    setShowCamera(false);
  };

  const handleRetake = () => {
    setPreviewUrl(null);
  };

  return (
    <Box sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: 2,
      p: 2,
      width: '100%',
      maxWidth: 600,
      margin: '0 auto'
    }}>
      {showCamera ? (
        <CameraView
          onCapture={handleCameraCapture}
          onClose={() => setShowCamera(false)}
        />
      ) : previewUrl ? (
        <Box sx={{
          width: '100%',
          aspectRatio: '4/3',
          overflow: 'hidden',
          borderRadius: 2,
          position: 'relative'
        }}>
          <img
            src={previewUrl}
            alt="Preview"
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover'
            }}
          />
          {isLoading && (
            <Box sx={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: 'rgba(0, 0, 0, 0.5)'
            }}>
              <CircularProgress color="primary" />
            </Box>
          )}
          {!isLoading && (
            <IconButton
              onClick={handleRetake}
              sx={{
                position: 'absolute',
                top: 8,
                right: 8,
                backgroundColor: 'rgba(0, 0, 0, 0.5)',
                color: 'white',
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.7)'
                }
              }}
            >
              <Close />
            </IconButton>
          )}
        </Box>
      ) : (
        <Box sx={{
          width: '100%',
          aspectRatio: '4/3',
          border: '2px dashed',
          borderColor: 'grey.300',
          borderRadius: 2,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 2,
          backgroundColor: 'grey.50'
        }}>
          <CameraAlt sx={{ fontSize: 48, color: 'grey.500' }} />
        </Box>
      )}

      {!showCamera && !isLoading && (
        <Box sx={{ display: 'flex', gap: 2, width: '100%', justifyContent: 'center' }}>
          <Button
            variant={"contained"}
            startIcon={<Upload />}
            component="label"
            disabled={isLoading}
            // fullWidth={!isDesktop}
          >
            Choose Image
            <Input
              accept="image/*"
              type="file"
              // capture={isDesktop ? undefined : "environment"}
              onChange={handleFileChange}
            />
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default ImageUploader;
