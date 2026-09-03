import { Typography, Card, CardContent, Switch, FormControlLabel, Divider } from '@mui/material';
import { useAppTheme } from '../contexts/ThemeContext';

export default function SettingsPage() {
  const { darkMode, toggleTheme } = useAppTheme();

  return (
    <div>
      <Typography variant="h4" fontWeight={700} mb={3}>Settings</Typography>
      <Card>
        <CardContent>
          <Typography variant="h6" mb={2}>Appearance</Typography>
          <FormControlLabel control={<Switch checked={darkMode} onChange={toggleTheme} />} label="Dark Mode" />
          <Divider sx={{ my: 2 }} />
          <Typography variant="h6" mb={2}>Notifications</Typography>
          <FormControlLabel control={<Switch defaultChecked />} label="Email notifications" />
          <FormControlLabel control={<Switch defaultChecked />} label="Conversion alerts" />
        </CardContent>
      </Card>
    </div>
  );
}
