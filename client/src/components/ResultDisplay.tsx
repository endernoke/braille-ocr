import { Box, Typography, Paper, Button } from '@mui/material';
import { ArrowBack } from '@mui/icons-material';
import type { ProcessResult } from '../types/api';

interface ResultDisplayProps {
  result: ProcessResult;
  onBack: () => void;
}

const ResultDisplay = ({ result, onBack }: ResultDisplayProps) => {
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
          <Typography variant="h6" gutterBottom>
            Recognized Text
          </Typography>
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

          <Typography variant="h6" gutterBottom>
            Braille Text
          </Typography>
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
    </Box>
  );
};

export default ResultDisplay;
