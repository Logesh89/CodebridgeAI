import { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { authApi } from '../services/api';

interface User {
  id: string;
  email: string;
  full_name?: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, rememberMe: boolean) => Promise<any>;
  googleLogin: (email: string) => Promise<void>;
  verifyOtp: (email: string, otp: string) => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);

  // Load user profile on startup if token exists
  useState(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      authApi.getMe().then((r) => setUser(r.data)).catch(() => localStorage.clear());
    }
  });

  const login = useCallback(async (email: string, rememberMe: boolean) => {
    setLoading(true);
    try {
      const { data } = await authApi.login(email, rememberMe);
      return data;
    } finally {
      setLoading(false);
    }
  }, []);

  const googleLogin = useCallback(async (email: string) => {
    setLoading(true);
    try {
      const { data } = await authApi.googleLogin(email);
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      const meResponse = await authApi.getMe();
      setUser(meResponse.data);
    } finally {
      setLoading(false);
    }
  }, []);

  const verifyOtp = useCallback(async (email: string, otp: string) => {
    setLoading(true);
    try {
      const { data } = await authApi.verifyOtp(email, otp);
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      const meResponse = await authApi.getMe();
      setUser(meResponse.data);
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } finally {
      localStorage.clear();
      setUser(null);
    }
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!localStorage.getItem('access_token'),
        login,
        googleLogin,
        verifyOtp,
        logout,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}
