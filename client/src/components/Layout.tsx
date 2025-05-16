import { Box, Paper, BottomNavigation, BottomNavigationAction } from '@mui/material';
import { CameraAlt, School } from '@mui/icons-material';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';

const Layout = () => {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <Box sx={{ pb: 7, height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <Outlet />
      </Box>
      <Paper sx={{ position: 'fixed', bottom: 0, left: 0, right: 0 }} elevation={3}>
        <BottomNavigation
          value={location.pathname}
          onChange={(_, newValue) => navigate(newValue)}
        >
          <BottomNavigationAction
            label="OCR"
            value="/"
            icon={<CameraAlt />}
          />
          <BottomNavigationAction
            label="Learn"
            value="/learn"
            icon={<School />}
          />
        </BottomNavigation>
      </Paper>
    </Box>
  );
};

export default Layout;
