import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import * as auth from '../api/auth';

function AuthCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState(null);

  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state');

    if (!code) {
      setError('No authorization code received from GitHub');
      return;
    }

    handleCallback(code, state);
  }, [searchParams, navigate]);

  const handleCallback = async (code, state) => {
    try {
      const data = await auth.handleGitHubCallback(code, state);
      
      // Store token and user info
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      // Redirect to dashboard
      navigate('/dashboard', { replace: true });
    } catch (err) {
      console.error('OAuth callback failed:', err);
      setError('Failed to complete login. Please try again.');
    }
  };

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-4 text-red-600">Login Failed</h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <a href="/" className="px-6 py-2 bg-gray-900 text-white rounded-md hover:bg-gray-800">
            Back to Login
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <p className="text-gray-500">Completing login...</p>
      </div>
    </div>
  );
}

export default AuthCallbackPage;
