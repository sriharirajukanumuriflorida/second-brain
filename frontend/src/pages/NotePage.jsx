import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getNote, getRelatedNotes } from '../api/client';

function NotePage() {
  const { id } = useParams();
  const [note, setNote] = useState(null);
  const [related, setRelated] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadNote();
    loadRelated();
  }, [id]);

  const loadNote = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getNote(id);
      setNote(data);
    } catch (err) {
      setError('Note not found');
    } finally {
      setLoading(false);
    }
  };

  const loadRelated = async () => {
    try {
      const data = await getRelatedNotes(id);
      setRelated(data);
    } catch (err) {
      // Non-fatal: related notes just don't render.
      setRelated([]);
    }
  };

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto">
        <p className="text-gray-500">Loading note...</p>
      </div>
    );
  }

  if (error || !note) {
    return (
      <div className="max-w-3xl mx-auto">
        <p className="text-red-500 mb-4">{error || 'Note not found'}</p>
        <Link to="/notes" className="text-blue-600 hover:text-blue-700">
          &larr; Back to Notes
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <Link to="/notes" className="text-sm text-blue-600 hover:text-blue-700 mb-4 inline-block">
        &larr; Back to Notes
      </Link>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-1">{note.title}</h1>
        <p className="text-sm text-gray-500 font-mono mb-4">{note.path}</p>

        <div className="flex flex-wrap gap-1 mb-6">
          <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
            {note.folder}
          </span>
          {note.tags.map((tag) => (
            <span
              key={tag}
              className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
            >
              #{tag}
            </span>
          ))}
        </div>

        {note.backlinks.length > 0 && (
          <div className="mb-6">
            <h2 className="text-sm font-semibold text-gray-900 mb-2">Backlinks</h2>
            <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
              {note.backlinks.map((link) => (
                <li key={link}>{link}</li>
              ))}
            </ul>
          </div>
        )}

        {related.length > 0 && (
          <div className="mb-6">
            <h2 className="text-sm font-semibold text-gray-900 mb-2">Related Notes</h2>
            <ul className="space-y-1">
              {related.map((rel) => (
                <li key={rel.id} className="flex items-center justify-between gap-2 text-sm">
                  <Link to={`/notes/${rel.id}`} className="text-blue-600 hover:text-blue-700 truncate">
                    {rel.title}
                  </Link>
                  <span className="shrink-0 text-xs text-gray-400">
                    {Math.round(rel.score * 100)}%
                  </span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="text-xs text-gray-400 border-t border-gray-200 pt-4 space-y-1">
          <p>Created: {new Date(note.created_at).toLocaleString()}</p>
          {note.updated_at && <p>Updated: {new Date(note.updated_at).toLocaleString()}</p>}
          <p>Last indexed: {new Date(note.last_indexed_at).toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
}

export default NotePage;
