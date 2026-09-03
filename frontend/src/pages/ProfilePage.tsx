import { Typography, Card, CardContent, Avatar, Box } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

export default function ProfilePage() {
  const { user } = useAuth();

  return (
    <div>
      <Typography variant="h4" fontWeight={700} mb={3}>User Profile</Typography>
      <Card>
        <CardContent>
          <Box display="flex" alignItems="center" gap={3} mb={3}>
            <Avatar sx={{ width: 80, height: 80, fontSize: 32 }}>{user?.email?.[0]?.toUpperCase() || 'U'}</Avatar>
            <Box>
              <Typography variant="h5">{user?.full_name || 'User'}</Typography>
              <Typography color="text.secondary">{user?.email || 'Not logged in'}</Typography>
              <Typography variant="body2" color="primary" mt={0.5}>Role: {user?.role || 'developer'}</Typography>
            </Box>
          </Box>
        </CardContent>
      </Card>
    </div>
  );
}
