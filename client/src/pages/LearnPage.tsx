import { Box, Typography, Paper, Button } from '@mui/material';

const LearnPage = () => {
  return (
    <Box sx={{ p: 2 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Learn Braille
        </Typography>
        <Typography>
          It's like Duolingo, but for Braille! This is a fun and interactive way to learn Braille.
        </Typography>
        <Button variant="contained" sx={{ mt: 2 }}>
          Start Lesson | 開始學習
        </Button>
      </Paper>
    </Box>
  );
};

export default LearnPage;

