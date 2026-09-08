import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import {
  Box, Card, CardContent, TextField, Button, Typography,
  Alert, CircularProgress
} from '@mui/material';
import { Pin, Key } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

interface OtpForm {
  otp: string;
}

export default function OtpVerificationPage() {
  const { verifyOtp, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const stateData = location.state as { email?: string; otpCode?: string } | undefined;
  const email = stateData?.email || '';
  const otpCode = stateData?.otpCode;

  const [error, setError] = useState('');
  const { register, handleSubmit, setValue, formState: { errors } } = useForm<OtpForm>({
    defaultValues: { otp: otpCode || '' },
  });

  const onSubmit = async (data: OtpForm) => {
    setError('');
    try {
      await verifyOtp(email, data.otp);
      navigate('/dashboard');
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Invalid or expired OTP code. Please try again.';
      setError(msg);
    }
  };

  if (!email) {
    navigate('/login');
    return null;
  }

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 2 }}>
      <Card sx={{ maxWidth: 460, width: '100%', borderRadius: 3, boxShadow: 6 }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h5" fontWeight={700} gutterBottom>Verify Email OTP</Typography>
          <Typography variant="body2" color="text.secondary" mb={3}>
            We have generated a 6-digit verification code for <strong>{email}</strong>.
          </Typography>

          {otpCode && (
            <Alert severity="info" icon={<Key />} sx={{ mb: 3, bgcolor: '#e3f2fd', color: '#0d47a1' }}>
              <Typography variant="subtitle2" fontWeight={700}>Verification OTP Code:</Typography>
              <Typography variant="h4" fontWeight={800} sx={{ letterSpacing: '6px', my: 1, color: '#1565c0' }}>
                {otpCode}
              </Typography>
              <Button
                size="small"
                variant="contained"
                color="primary"
                onClick={() => setValue('otp', otpCode)}
                sx={{ mt: 1, textTransform: 'none' }}
              >
                Auto-Fill OTP Code
              </Button>
            </Alert>
          )}

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          <form onSubmit={handleSubmit(onSubmit)}>
            <TextField
              fullWidth label="6-Digit OTP Code" margin="normal"
              placeholder="──────"
              inputProps={{ maxLength: 6, style: { letterSpacing: '8px', fontSize: '24px', textAlign: 'center' } }}
              InputProps={{ startAdornment: <Pin sx={{ mr: 1, color: 'text.secondary' }} /> }}
              {...register('otp', { required: 'OTP is required', minLength: { value: 4, message: 'OTP must be 6 digits' } })}
              error={!!errors.otp}
              helperText={errors.otp?.message}
            />

            <Button type="submit" fullWidth variant="contained" size="large" disabled={loading} sx={{ mt: 3, py: 1.5, fontWeight: 600 }}>
              {loading ? <CircularProgress size={24} /> : 'Verify & Sign In'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </Box>
  );
}
