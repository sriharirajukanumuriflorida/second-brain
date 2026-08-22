/**
 * Authentication API client.
 */
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const getGitHubLoginUrl = async () => {
  const response = await axios.get(`${API_URL}/api/v1/auth/github/login`);
  return response.data;
};

export const handleGitHubCallback = async (code, state) => {
  // Backend reads code/state as QUERY params (FastAPI signature), not a body.
  // Sending them in the body causes a 422. See app/api/auth.py:github_callback.
  const response = await axios.post(
    `${API_URL}/api/v1/auth/github/callback`,
    null,
    { params: { code, state } }
  );
  return response.data;
};

export const logout = async (token) => {
  const response = await axios.post(
    `${API_URL}/api/v1/auth/logout`,
    {},
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );
  return response.data;
};

export const getCurrentUser = async (token) => {
  const response = await axios.get(`${API_URL}/api/v1/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
  return response.data;
};

export default {
  getGitHubLoginUrl,
  handleGitHubCallback,
  logout,
  getCurrentUser
};
