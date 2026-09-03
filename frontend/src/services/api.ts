import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, null, {
            params: { refresh_token: refreshToken },
          });
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('refresh_token', data.refresh_token);
          error.config.headers.Authorization = `Bearer ${data.access_token}`;
          return api.request(error.config);
        } catch {
          localStorage.clear();
          window.location.href = '/login';
        }
      } else {
        localStorage.clear();
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;

export const authApi = {
  login: (email: string, rememberMe: boolean) =>
    api.post('/auth/login', { email, remember_me: rememberMe }),
  googleLogin: (email: string) =>
    api.post('/auth/google', { email }),
  verifyOtp: (email: string, otp: string) =>
    api.post('/auth/verify-otp', { email, otp }),
  logout: () => api.post('/auth/logout'),
  forgotPassword: (email: string) =>
    api.post('/auth/forgot-password', { email }),
  resetPassword: (token: string, newPassword: string) =>
    api.post('/auth/reset-password', { token, new_password: newPassword }),
  getMe: () => api.get('/auth/me'),
};

export const userApi = {
  list: () => api.get('/users'),
  updateRole: (userId: string, role: string, isActive?: boolean) =>
    api.put(`/users/${userId}/role`, { role, is_active: isActive }),
  delete: (userId: string) => api.delete(`/users/${userId}`),
};

export const dashboardApi = {
  getDashboard: () => api.get('/dashboard'),
};

export const excelApi = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/excel/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export const pipelineApi = {
  list: (params?: { skip?: number; limit?: number; status?: string }) =>
    api.get('/pipelines', { params }),
  get: (id: string) => api.get(`/pipelines/${id}`),
  convert: (id: string) => api.post(`/pipelines/${id}/convert`),
  execute: (id: string) => api.post(`/pipelines/${id}/execute`),
  status: (id: string) => api.get(`/pipelines/${id}/status`),
  uploadSnaplogic: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/pipelines/upload-snaplogic', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  scanLocalFolder: (folderPath: string) =>
    api.post('/pipelines/scan-local-folder', { folder_path: folderPath }),
};

export const reportsApi = {
  list: () => api.get('/reports'),
};

export const logsApi = {
  list: (pipelineId?: string) =>
    api.get('/logs', { params: { pipeline_id: pipelineId } }),
};

export const notificationsApi = {
  list: (unreadOnly?: boolean) =>
    api.get('/notifications', { params: { unread_only: unreadOnly } }),
  markRead: (id: string) => api.post(`/notifications/${id}/read`),
};

export const downloadApi = {
  getUrl: (fileId: string) => `${API_BASE_URL}/download/${fileId}`,
};

export const interpreterApi = {
  convertCode: (data: { source_code: string; from_lang: string; to_lang: string; file_name?: string }) =>
    api.post('/interpreter/convert', data),
  executeCode: (data: { code: string; language: string }) =>
    api.post('/interpreter/execute', data),
  autoFixCode: (data: { code: string; language: string; error_message?: string }) =>
    api.post('/interpreter/auto-fix', data),
};
