import { Box, Typography, Paper } from '@mui/material';

const LearnPage = () => {
  return (
    <Box sx={{ p: 2 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Learn Braille
        </Typography>
        <Typography>
          This section will contain learning resources for Braille.
          Coming soon!
        </Typography>
      </Paper>
    </Box>
  );
};

export default LearnPage;
