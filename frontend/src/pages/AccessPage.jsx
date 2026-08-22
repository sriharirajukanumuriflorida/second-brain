import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { claimAccess } from '../api/client';

/**
 * Handles a shared read-only access link: /access?token=XYZ
 * Claims the token (binds read-only access to this browser for 24h), then
 * sends the visitor into the app in read-only mode.
 */
function AccessPage() {
  const [searchParams] = useSearchParams();
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = searchParams.get('token');
    if (!token) {
      setError('This link is missing its access token.');
      setLoading(false);
      return;
    }
    (async () => {
      try {
        await claimAccess(token);
        // Mark this browser as read-only so the app skips GitHub login.
        localStorage.setItem('access_mode', 'readonly');
        navigate('/notes');
      } catch (err) {
        setError('This link is invalid, already used, expired, or revoked.');
        setLoading(false);
      }
    })();
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      {loading ? (
        <p className="text-gray-500">Unlocking read-only access…</p>
      ) : (
        <div className="text-center">
          <h1 className="text-xl font-bold mb-2">Access link</h1>
          <p className="text-red-500">{error}</p>
        </div>
      )}
    </div>
  );
}

export default AccessPage;
