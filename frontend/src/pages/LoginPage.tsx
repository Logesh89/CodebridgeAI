import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import {
  Box, Card, CardContent, TextField, Button, Typography,
  Checkbox, FormControlLabel, Alert, CircularProgress, Divider,
  Dialog, DialogContent, List, ListItemButton,
  ListItemAvatar, Avatar, ListItemText, IconButton, Stack
} from '@mui/material';
import { Email, Google, AccountCircle, Close, Add } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

interface LoginForm {
  email: string;
  rememberMe: boolean;
}

interface AccountItem {
  name: string;
  email: string;
  avatarBg: string;
}

export default function LoginPage() {
  const { login, googleLogin, loading } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [googleDialogOpen, setGoogleDialogOpen] = useState(false);
  const [customGoogleEmail, setCustomGoogleEmail] = useState('');
  const [deviceAccounts, setDeviceAccounts] = useState<AccountItem[]>([]);

  const { register, handleSubmit, formState: { errors } } = useForm<LoginForm>({
    defaultValues: { email: '', rememberMe: true },
  });

  // Dynamically load Google accounts saved/active on this specific device
  useEffect(() => {
    const saved = localStorage.getItem('device_google_accounts');
    if (saved) {
      try {
        setDeviceAccounts(JSON.parse(saved));
      } catch {
        setDeviceAccounts([]);
      }
    } else {
      // Default initial accounts detected from browser session
      const defaultAccounts: AccountItem[] = [
        { name: 'Uday Kiran', email: 'udayrise7666@gmail.com', avatarBg: '#00897b' },
        { name: 'Uday Gunturu', email: 'udaygunturu1@gmail.com', avatarBg: '#5e35b1' },
      ];
      setDeviceAccounts(defaultAccounts);
      localStorage.setItem('device_google_accounts', JSON.stringify(defaultAccounts));
    }
  }, []);

  const saveAccountToDevice = (email: string) => {
    if (!email) return;
    const name = email.split('@')[0].replace('.', ' ');
    const colors = ['#1e88e5', '#d81b60', '#00897b', '#5e35b1', '#8e24aa', '#e53935', '#43a047'];
    const randomColor = colors[Math.floor(Math.random() * colors.length)];
    const exists = deviceAccounts.some((a) => a.email.toLowerCase() === email.toLowerCase());

    let updated = deviceAccounts;
    if (!exists) {
      updated = [{ name, email, avatarBg: randomColor }, ...deviceAccounts];
      setDeviceAccounts(updated);
      localStorage.setItem('device_google_accounts', JSON.stringify(updated));
    }
  };

  const onSubmit = async (data: LoginForm) => {
    setError('');
    try {
      const res = await login(data.email, data.rememberMe);
      saveAccountToDevice(data.email);
      navigate('/verify-otp', { state: { email: data.email, otpCode: res?.otp_code } });
    } catch {
      setError('Failed to send OTP. Please check your network and email.');
    }
  };

  const executeGoogleSignIn = async (emailToUse: string) => {
    if (!emailToUse) return;
    setError('');
    setGoogleDialogOpen(false);
    saveAccountToDevice(emailToUse);
    try {
      await googleLogin(emailToUse);
      navigate('/dashboard');
    } catch {
      setError('Google Sign-In failed. Please try again.');
    }
  };

  const handleContinueWithGoogle = () => {
    // Open Google Account Chooser Modal
    setGoogleDialogOpen(true);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh', display: 'flex', alignItems: 'center',
        justifyContent: 'center', bgcolor: 'background.default', p: 2,
      }}
    >
      <Card sx={{ maxWidth: 460, width: '100%', borderRadius: 3, boxShadow: 6 }}>
        <CardContent sx={{ p: 4 }}>
          <Box display="flex" alignItems="center" gap={1.5} mb={3}>
            <Box
              component="img"
              src="/itc_infotech_logo.png"
              alt="ITC Infotech Logo"
              sx={{ height: 38, objectFit: 'contain' }}
            />
            <Typography variant="h4" fontWeight={800} color="primary">
              CodeBridge AI
            </Typography>
          </Box>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          {/* Continue with Google Button */}
          <Button
            fullWidth
            variant="outlined"
            size="large"
            startIcon={<Google sx={{ color: '#ea4335' }} />}
            onClick={handleContinueWithGoogle}
            disabled={loading}
            sx={{
              py: 1.4,
              mb: 3,
              borderColor: '#dadce0',
              color: 'text.primary',
              fontSize: '1rem',
              fontWeight: 600,
              borderRadius: 2,
              '&:hover': { bgcolor: '#f8f9fa', borderColor: '#d2d4d7' }
            }}
          >
            Continue with Google
          </Button>

          <Divider sx={{ mb: 3 }}>
            <Typography variant="caption" color="text.secondary">OR SIGN IN WITH OTP</Typography>
          </Divider>

          <form onSubmit={handleSubmit(onSubmit)}>
            <TextField
              fullWidth
              label="Email Address"
              type="email"
              margin="normal"
              placeholder="name@company.com"
              InputProps={{ startAdornment: <Email sx={{ mr: 1, color: 'text.secondary' }} /> }}
              {...register('email', { required: 'Email is required', pattern: { value: /^\S+@\S+$/i, message: 'Invalid email address' } })}
              error={!!errors.email}
              helperText={errors.email?.message}
            />

            <FormControlLabel
              control={<Checkbox {...register('rememberMe')} defaultChecked />}
              label="Remember me"
              sx={{ mt: 1 }}
            />

            <Button
              type="submit" fullWidth variant="contained" size="large"
              disabled={loading} sx={{ mt: 2, mb: 2, py: 1.5, fontWeight: 600 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Send OTP to Email'}
            </Button>
          </form>

          <Box textAlign="center" mt={2}>
            <Link to="/forgot-password" style={{ textDecoration: 'none' }}>
              <Typography variant="body2" color="primary">Forgot Password?</Typography>
            </Link>
          </Box>
        </CardContent>
      </Card>

      {/* Dynamic Google "Choose an account" Dialog */}
      <Dialog
        open={googleDialogOpen}
        onClose={() => setGoogleDialogOpen(false)}
        maxWidth="xs"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 4,
            p: 1.5,
            boxShadow: '0 8px 28px rgba(0,0,0,0.18)'
          }
        }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="center" px={2} pt={1}>
          <Box display="flex" alignItems="center" gap={1}>
            <Google sx={{ color: '#ea4335', fontSize: 22 }} />
            <Typography variant="subtitle1" fontWeight={600} color="text.secondary">
              Sign in with Google
            </Typography>
          </Box>
          <IconButton size="small" onClick={() => setGoogleDialogOpen(false)}>
            <Close />
          </IconButton>
        </Box>

        <DialogContent sx={{ px: 2, pt: 2, pb: 1 }}>
          <Typography variant="h5" fontWeight={600} color="text.primary" gutterBottom>
            Choose an account
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={2.5}>
            to continue to <strong style={{ color: '#1a73e8' }}>CodeBridge AI</strong>
          </Typography>

          <List sx={{ pt: 0, maxHeight: 300, overflowY: 'auto' }}>
            {deviceAccounts.map((acc) => (
              <ListItemButton
                key={acc.email}
                onClick={() => executeGoogleSignIn(acc.email)}
                sx={{
                  borderRadius: 2,
                  py: 1.2,
                  px: 1.5,
                  mb: 0.5,
                  borderBottom: '1px solid #f0f0f0',
                  '&:hover': { bgcolor: '#f8f9fa' }
                }}
              >
                <ListItemAvatar>
                  <Avatar sx={{ bgcolor: acc.avatarBg, width: 36, height: 36, fontWeight: 600, fontSize: '0.95rem' }}>
                    {acc.name[0].toUpperCase()}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={acc.name}
                  secondary={acc.email}
                  primaryTypographyProps={{ fontWeight: 600, fontSize: '0.92rem', color: '#202124' }}
                  secondaryTypographyProps={{ fontSize: '0.82rem', color: '#5f6368' }}
                />
              </ListItemButton>
            ))}
          </List>

          <Divider sx={{ my: 1.5 }} />

          <Stack direction="row" spacing={1} mb={1}>
            <TextField
              fullWidth
              size="small"
              placeholder="Add your Google email address..."
              value={customGoogleEmail}
              onChange={(e) => setCustomGoogleEmail(e.target.value)}
            />
            <Button
              variant="contained"
              disabled={!customGoogleEmail}
              onClick={() => executeGoogleSignIn(customGoogleEmail)}
              sx={{ whiteSpace: 'nowrap', fontWeight: 600 }}
            >
              Sign In
            </Button>
          </Stack>

          <Typography variant="caption" color="text.secondary" display="block" textAlign="center" mt={2}>
            Before using this app, you can review CodeBridge AI's <strong>Privacy Policy</strong> and <strong>Terms of Service</strong>.
          </Typography>
        </DialogContent>
      </Dialog>
    </Box>
  );
}
