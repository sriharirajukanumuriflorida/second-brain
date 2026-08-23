import { useState, useEffect } from 'react';
import { generateAccessLink, listAccessLinks, revokeAccessLink } from '../api/client';

function AdminPage() {
  const [links, setLinks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [hours, setHours] = useState(24);
  const [label, setLabel] = useState('');
  const [generating, setGenerating] = useState(false);
  const [newLink, setNewLink] = useState(null);
  const [error, setError] = useState(null);
  const [forbidden, setForbidden] = useState(false);

  useEffect(() => {
    loadLinks();
  }, []);

  const loadLinks = async () => {
    try {
      const data = await listAccessLinks();
      setLinks(data);
    } catch (err) {
      if (err.response?.status === 403) {
        setForbidden(true);
      } else {
        setError('Failed to load access links');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    setGenerating(true);
    setError(null);
    try {
      const data = await generateAccessLink(Number(hours), label.trim() || null);
      const shareUrl = `${window.location.origin}/access?token=${data.token}`;
      setNewLink(shareUrl);
      setLabel('');
      await loadLinks();
    } catch (err) {
      setError('Failed to generate access link');
    } finally {
      setGenerating(false);
    }
  };

  const handleRevoke = async (id) => {
    try {
      await revokeAccessLink(id);
      await loadLinks();
    } catch (err) {
      setError('Failed to revoke access link');
    }
  };

  const handleCopy = () => {
    if (newLink) navigator.clipboard.writeText(newLink);
  };

  const statusFor = (link) => {
    if (link.revoked) return { text: 'Revoked', className: 'text-red-600' };
    if (!link.is_claimed) return { text: 'Unclaimed', className: 'text-gray-500' };
    if (link.expires_at && new Date(link.expires_at) < new Date()) {
      return { text: 'Expired', className: 'text-gray-500' };
    }
    return { text: 'Active', className: 'text-green-600' };
  };

  if (forbidden) {
    return (
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Admin</h1>
        <p className="text-red-500">You don't have permission to view this page.</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Admin</h1>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Generate Read-Only Access Link</h2>
        <form onSubmit={handleGenerate} className="flex flex-wrap gap-3 items-end">
          <div>
            <label className="block text-sm text-gray-600 mb-1">Valid for (hours)</label>
            <input
              type="number"
              min="1"
              max="720"
              value={hours}
              onChange={(e) => setHours(e.target.value)}
              className="w-28 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm text-gray-600 mb-1">Label (optional)</label>
            <input
              type="text"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              placeholder="e.g. for Alex"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            type="submit"
            disabled={generating}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          >
            {generating ? 'Generating...' : 'Generate Link'}
          </button>
        </form>

        {newLink && (
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md flex items-center justify-between gap-3">
            <code className="text-sm text-blue-900 break-all">{newLink}</code>
            <button
              onClick={handleCopy}
              className="shrink-0 px-3 py-1 text-sm bg-white border border-blue-300 rounded-md hover:bg-blue-100"
            >
              Copy
            </button>
          </div>
        )}

        {error && <p className="text-sm text-red-500 mt-3">{error}</p>}
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Existing Links</h2>
        {loading ? (
          <p className="text-gray-500">Loading...</p>
        ) : links.length === 0 ? (
          <p className="text-gray-500">No access links generated yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead>
                <tr className="text-gray-500 border-b border-gray-200">
                  <th className="py-2 pr-4">Label</th>
                  <th className="py-2 pr-4">Status</th>
                  <th className="py-2 pr-4">TTL</th>
                  <th className="py-2 pr-4">Created</th>
                  <th className="py-2 pr-4">Expires</th>
                  <th className="py-2"></th>
                </tr>
              </thead>
              <tbody>
                {links.map((link) => {
                  const status = statusFor(link);
                  return (
                    <tr key={link.id} className="border-b border-gray-100">
                      <td className="py-2 pr-4">{link.label || '—'}</td>
                      <td className={`py-2 pr-4 font-medium ${status.className}`}>{status.text}</td>
                      <td className="py-2 pr-4">{link.ttl_hours}h</td>
                      <td className="py-2 pr-4">{new Date(link.created_at).toLocaleString()}</td>
                      <td className="py-2 pr-4">
                        {link.expires_at ? new Date(link.expires_at).toLocaleString() : '—'}
                      </td>
                      <td className="py-2">
                        {!link.revoked && (
                          <button
                            onClick={() => handleRevoke(link.id)}
                            className="text-red-600 hover:text-red-700 text-sm"
                          >
                            Revoke
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminPage;
