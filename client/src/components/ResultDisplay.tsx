import { Box, Typography, Paper, Button, IconButton, Snackbar } from '@mui/material';
import { ArrowBack, ContentCopy, Share } from '@mui/icons-material';
import type { ProcessResult } from '../types/api';
import { useState } from 'react';

interface ResultDisplayProps {
  result: ProcessResult;
  onBack: () => void;
}

const ResultDisplay = ({ result, onBack }: ResultDisplayProps) => {
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  const handleCopy = async (text: string) => {
    // See https://stackoverflow.com/questions/51805395/navigator-clipboard-is-undefined
    try {
      // Navigator clipboard api needs a secure context (https)
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        // Use the 'out of viewport hidden text area' trick
        const textArea = document.createElement("textarea");
        textArea.value = text;
          
        // Move textarea out of the viewport so it's not visible
        textArea.style.position = "absolute";
        textArea.style.left = "-999999px";
          
        document.body.prepend(textArea);
        textArea.select();

        try {
          document.execCommand('copy');
        } catch (error) {
          throw new Error('Failed to copy text');
        } finally {
          textArea.remove();
        }
      }
      setSnackbarMessage('Copied to clipboard!');
      setSnackbarOpen(true);
    } catch (err) {
      setSnackbarMessage('Failed to copy text.');
      setSnackbarOpen(true);
    }
  };

  const handleShare = async (text: string) => {
    if (navigator.share) {
      try {
        await navigator.share({
          text: text,
        });
      } catch (err) {
        if ((err as Error).name !== 'AbortError') {
          setSnackbarMessage('Failed to share text.');
          setSnackbarOpen(true);
        }
      }
    } else {
      setSnackbarMessage('Sharing is not supported on this device.');
      setSnackbarOpen(true);
    }
  };

  return (
    <Box sx={{ p: 2, maxWidth: 600, margin: '0 auto' }}>
      <Button
        onClick={onBack}
        startIcon={<ArrowBack />}
        sx={{ mb: 2 }}
        aria-label="Return to image upload"
      >
        Back
      </Button>

      <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
        {result.result.annotated_image && (
          <img
            src={result.result.annotated_image}
            alt="Processed"
            style={{
              width: '100%',
              borderRadius: 8,
              marginBottom: 16
            }}
          />
        )}

        {result.result.recognized_text ? (
          <>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="h6" sx={{ flex: 1 }}>
                Recognized Text
              </Typography>
              <IconButton
                onClick={() => handleCopy(result.result.recognized_text)}
                aria-label="Copy recognized text"
                size="small"
              >
                <ContentCopy />
              </IconButton>
              <IconButton
                onClick={() => handleShare(result.result.recognized_text)}
                aria-label="Share recognized text"
                size="small"
              >
                <Share />
              </IconButton>
            </Box>
            <Box sx={{ 
              backgroundColor: 'grey.50',
              p: 2,
              borderRadius: 1,
              mb: 3,
              overflowX: 'auto'
            }}>
              <Typography
                component="pre"
                sx={{
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  margin: 0,
                  fontFamily: 'inherit',
                }}
              >
                {result.result.recognized_text}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Typography variant="h6" sx={{ flex: 1 }}>
                Braille Text
              </Typography>
              <IconButton
                onClick={() => handleCopy(result.result.recognized_braille || '')}
                aria-label="Copy braille text"
                size="small"
              >
                <ContentCopy />
              </IconButton>
              <IconButton
                onClick={() => handleShare(result.result.recognized_braille || '')}
                aria-label="Share braille text"
                size="small"
              >
                <Share />
              </IconButton>
            </Box>
            <Box sx={{ 
              backgroundColor: 'grey.50',
              p: 2,
              borderRadius: 1,
              overflowX: 'auto'
            }}>
              <Typography
                component="pre"
                sx={{
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  margin: 0,
                  fontFamily: 'monospace'
                }}
              >
                {result.result.recognized_braille || 'Unavailable'}
              </Typography>
            </Box>
          </>
        ) : (
          <Typography variant="h6" gutterBottom>
            No text recognized. Please try again.
          </Typography>
        )}
      </Paper>
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Box>
  );
};

export default ResultDisplay;
