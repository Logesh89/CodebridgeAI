import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { Box, Card, CardContent, TextField, Button, Typography, Alert } from '@mui/material';
import { authApi } from '../services/api';

export default function ForgotPasswordPage() {
  const [sent, setSent] = useState(false);
  const [error, setError] = useState('');
  const { register, handleSubmit } = useForm<{ email: string }>();

  const onSubmit = async (data: { email: string }) => {
    try {
      await authApi.forgotPassword(data.email);
      setSent(true);
    } catch {
      setError('Failed to send reset link.');
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 2 }}>
      <Card sx={{ maxWidth: 440, width: '100%' }}>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h5" fontWeight={700} mb={2}>Forgot Password</Typography>
          {sent ? (
            <Alert severity="success">Reset link sent to your email.</Alert>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)}>
              {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
              <TextField fullWidth label="Email" type="email" margin="normal" {...register('email', { required: true })} />
              <Button type="submit" fullWidth variant="contained" sx={{ mt: 2 }}>Send Reset Link</Button>
            </form>
          )}
          <Box textAlign="center" mt={2}>
            <Link to="/login"><Typography variant="body2" color="primary">Back to Login</Typography></Link>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}
