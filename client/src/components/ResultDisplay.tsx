import { Box, Typography, Paper } from '@mui/material';
import type { ProcessResult } from '../types/api';

interface ResultDisplayProps {
  result: ProcessResult;
}

const ResultDisplay = ({ result }: ResultDisplayProps) => {
  return (
    <Box sx={{ p: 2, maxWidth: 600, margin: '0 auto' }}>
      <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
        <img
          src={result.result.annotated_image}
          alt="Processed"
          style={{
            width: '100%',
            borderRadius: 8,
            marginBottom: 16
          }}
        />
        
        <Typography variant="h6" gutterBottom>
          Recognized Text
        </Typography>
        <Typography paragraph>
          {result.result.recognized_text}
        </Typography>

        <Typography variant="h6" gutterBottom>
          Braille Text
        </Typography>
        <Typography paragraph sx={{ fontFamily: 'monospace' }}>
          {result.result.recognized_braille}
        </Typography>
      </Paper>
    </Box>
  );
};

export default ResultDisplay;
