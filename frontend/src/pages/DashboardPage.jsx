import { useState, useEffect } from 'react';
import { getStatus, triggerSync } from '../api/client';

function DashboardPage() {
  const [status, setStatus] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      const data = await getStatus();
      setStatus(data);
    } catch (error) {
      console.error('Failed to load status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      await triggerSync(true);
      setTimeout(loadStatus, 2000);
    } catch (error) {
      console.error('Sync failed:', error);
    } finally {
      setSyncing(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>
        <p className="text-gray-500">Loading status...</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>

      <div className="grid gap-6 md:grid-cols-2 mb-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">Total Notes</h2>
          <p className="text-4xl font-bold text-blue-600">{status?.total_notes || 0}</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">Last Sync Status</h2>
          <p className={`text-2xl font-bold ${
            status?.last_sync_status === 'completed' ? 'text-green-600' :
            status?.last_sync_status === 'failed' ? 'text-red-600' :
            'text-gray-600'
          }`}>
            {status?.last_sync_status || 'Unknown'}
          </p>
          {status?.last_sync_at && (
            <p className="text-sm text-gray-500 mt-1">
              {new Date(status.last_sync_at).toLocaleString()}
            </p>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">Vault Path</h2>
        <p className="text-gray-600 font-mono text-sm">{status?.vault_path || 'Not configured'}</p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Actions</h2>
        <button
          onClick={handleSync}
          disabled={syncing}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
        >
          {syncing ? 'Syncing...' : 'Trigger Sync'}
        </button>
      </div>
    </div>
  );
}

export default DashboardPage;
