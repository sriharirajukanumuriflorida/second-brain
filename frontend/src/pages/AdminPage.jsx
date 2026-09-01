import { useState, useEffect } from 'react';
import {
  generateAccessLink,
  listAccessLinks,
  revokeAccessLink,
  getEmbeddingStatus,
  generateAllEmbeddings,
  runCompaction,
} from '../api/client';

function AdminPage() {
  const [links, setLinks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [hours, setHours] = useState(24);
  const [label, setLabel] = useState('');
  const [generating, setGenerating] = useState(false);
  const [newLink, setNewLink] = useState(null);
  const [error, setError] = useState(null);
  const [forbidden, setForbidden] = useState(false);

  // Semantic-search index (embeddings) state.
  const [embStatus, setEmbStatus] = useState(null);
  const [embRunning, setEmbRunning] = useState(false);
  const [embResult, setEmbResult] = useState(null);
  const [embError, setEmbError] = useState(null);

  // Compaction / LLM-wiki state.
  const [compTopic, setCompTopic] = useState('');
  const [compRunning, setCompRunning] = useState(false);
  const [compPreview, setCompPreview] = useState(null);
  const [compPr, setCompPr] = useState(null);
  const [compError, setCompError] = useState(null);

  useEffect(() => {
    loadLinks();
    loadEmbStatus();
  }, []);

  const loadEmbStatus = async () => {
    try {
      const data = await getEmbeddingStatus();
      setEmbStatus(data);
    } catch (err) {
      // Non-fatal: status panel just shows unavailable.
      setEmbStatus(null);
    }
  };

  const handleBackfill = async () => {
    setEmbRunning(true);
    setEmbError(null);
    setEmbResult(null);
    try {
      const data = await generateAllEmbeddings(true);
      setEmbResult(data);
      await loadEmbStatus();
    } catch (err) {
      setEmbError(
        err.response?.data?.detail || 'Failed to generate embeddings'
      );
    } finally {
      setEmbRunning(false);
    }
  };

  const handleCompaction = async (dryRun) => {
    if (!compTopic.trim()) return;
    setCompRunning(true);
    setCompError(null);
    if (dryRun) setCompPr(null);
    try {
      const data = await runCompaction(compTopic.trim(), { dryRun });
      setCompPreview(data);
      if (!dryRun && data.pr_url) setCompPr(data);
    } catch (err) {
      setCompError(err.response?.data?.detail || 'Compaction failed');
    } finally {
      setCompRunning(false);
    }
  };

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

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Semantic Search Index</h2>
        {embStatus ? (
          <div className="flex flex-wrap gap-6 text-sm text-gray-700 mb-4">
            <div>
              <div className="text-gray-500">Total chunks</div>
              <div className="text-xl font-semibold text-gray-900">{embStatus.total_chunks}</div>
            </div>
            <div>
              <div className="text-gray-500">Stale chunks</div>
              <div className="text-xl font-semibold text-gray-900">{embStatus.stale_chunks}</div>
            </div>
            <div>
              <div className="text-gray-500">Semantic search</div>
              <div className={`text-xl font-semibold ${embStatus.semantic_search_available ? 'text-green-600' : 'text-gray-500'}`}>
                {embStatus.semantic_search_available ? 'Available' : 'Not available'}
              </div>
            </div>
          </div>
        ) : (
          <p className="text-gray-500 mb-4">Embedding status unavailable.</p>
        )}

        <p className="text-sm text-gray-500 mb-3">
          Embeddings are generated automatically on sync for changed notes. Use
          backfill once to embed notes that predate this feature (safe to re-run —
          it only embeds notes with no chunks yet).
        </p>

        <button
          onClick={handleBackfill}
          disabled={embRunning}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
        >
          {embRunning ? 'Generating…' : 'Backfill missing embeddings'}
        </button>

        {embResult && (
          <p className="text-sm text-green-700 mt-3">
            Done: {embResult.notes_embedded} embedded, {embResult.notes_skipped} already indexed,
            {' '}{embResult.notes_failed} failed.
          </p>
        )}
        {embError && <p className="text-sm text-red-500 mt-3">{embError}</p>}
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Compile Wiki Page (Compaction)</h2>
        <p className="text-sm text-gray-500 mb-3">
          Compile the notes matching a topic into one derived, cross-linked wiki
          page. Source notes are never changed. Preview first, then open a pull
          request that adds the page under <code>14 Agent Outputs/</code> for review.
        </p>

        <div className="flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[240px]">
            <label className="block text-sm text-gray-600 mb-1">Topic</label>
            <input
              type="text"
              value={compTopic}
              onChange={(e) => setCompTopic(e.target.value)}
              placeholder="e.g. Retrieval-Augmented Generation"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            onClick={() => handleCompaction(true)}
            disabled={compRunning || !compTopic.trim()}
            className="px-5 py-2 bg-white border border-blue-300 text-blue-700 rounded-md hover:bg-blue-50 disabled:opacity-50"
          >
            {compRunning ? 'Working…' : 'Preview'}
          </button>
          <button
            onClick={() => handleCompaction(false)}
            disabled={compRunning || !compTopic.trim()}
            className="px-5 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          >
            Create PR
          </button>
        </div>

        {compPr && (
          <p className="text-sm text-green-700 mt-3">
            PR #{compPr.pr_number} opened:{' '}
            <a href={compPr.pr_url} target="_blank" rel="noreferrer" className="underline">
              {compPr.pr_url}
            </a>
          </p>
        )}

        {compPreview && (
          <div className="mt-4">
            <div className="text-xs text-gray-500 mb-2">
              {compPreview.source_notes.length} source note(s) · model {compPreview.model} ·
              {' '}est. ${compPreview.estimated_cost_usd?.toFixed?.(4) ?? compPreview.estimated_cost_usd}
            </div>
            <pre className="max-h-96 overflow-auto p-3 bg-gray-50 border border-gray-200 rounded-md text-xs whitespace-pre-wrap">
              {compPreview.content}
            </pre>
          </div>
        )}

        {compError && <p className="text-sm text-red-500 mt-3">{compError}</p>}
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
