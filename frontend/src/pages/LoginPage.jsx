import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import * as auth from '../api/auth';

function LoginPage() {
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Only auto-handle the OAuth return (when GitHub sends ?code=...).
    // Otherwise show the sign-in button and wait for a click — don't auto-bounce
    // to GitHub on every page load.
    const code = searchParams.get('code');
    const state = searchParams.get('state');

    if (code) {
      handleCallback(code, state);
    }
  }, [searchParams]);

  const initiateLogin = async () => {
    try {
      setLoading(true);
      const data = await auth.getGitHubLoginUrl();
      window.location.href = data.auth_url;
    } catch (err) {
      setError('Failed to initiate login');
      setLoading(false);
    }
  };

  const handleCallback = async (code, state) => {
    try {
      setLoading(true);
      const data = await auth.handleGitHubCallback(code, state);
      
      // Store token
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      // Redirect to dashboard
      navigate('/dashboard');
    } catch (err) {
      setError('Failed to complete login');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-red-500">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Second Brain</h1>
        <p className="text-gray-500 mb-4">Sign in with GitHub to continue</p>
        <button
          onClick={initiateLogin}
          className="px-6 py-2 bg-gray-900 text-white rounded-md hover:bg-gray-800"
        >
          Sign in with GitHub
        </button>
      </div>
    </div>
  );
}

export default LoginPage;
