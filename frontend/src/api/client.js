/**
 * API client for backend integration.
 */
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  // Send the read-only access cookie (HTTP-only) with every request so
  // shared-link visitors are authorized. Requires backend CORS
  // allow_credentials=true + explicit origins (already configured).
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach the stored bearer token to every request so protected endpoints work.
// The token is set at login (LoginPage) and cleared on logout (App).
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

// Sync
export const triggerSync = async (force = false) => {
  const response = await api.post('/api/v1/sync', { force });
  return response.data;
};

// Status
export const getStatus = async () => {
  const response = await api.get('/api/v1/status');
  return response.data;
};

// Notes
export const getNotes = async (folder = null, limit = 100) => {
  const params = {};
  if (folder) params.folder = folder;
  params.limit = limit;
  const response = await api.get('/api/v1/notes', { params });
  return response.data;
};

export const getNote = async (noteId) => {
  const response = await api.get(`/api/v1/notes/${noteId}`);
  return response.data;
};

// Folders
export const getFolders = async () => {
  const response = await api.get('/api/v1/folders');
  return response.data;
};

// Read-only shared access: claim a share link (?token=...) to bind read-only
// access to this browser for 24h. The cookie is set by the backend response.
export const claimAccess = async (token) => {
  const response = await api.post('/api/v1/access/claim', { token });
  return response.data;
};

// Search — hybrid (keyword + semantic) by default; pass semantic=false to
// force keyword-only. Matches GET /api/v1/search on the backend.
export const searchNotes = async (query, folder = null, limit = 20, semantic = true) => {
  const params = { query, limit, semantic };
  if (folder) params.folder = folder;
  const response = await api.get('/api/v1/search', { params });
  return response.data;
};

// Admin: read-only share links. All require an admin bearer token (attached
// automatically by the request interceptor above).
export const generateAccessLink = async (hours = 24, label = null) => {
  const response = await api.post('/api/v1/access/generate', { hours, label });
  return response.data;
};

export const listAccessLinks = async () => {
  const response = await api.get('/api/v1/access/list');
  return response.data;
};

export const revokeAccessLink = async (id) => {
  const response = await api.post(`/api/v1/access/${id}/revoke`);
  return response.data;
};

export default api;
