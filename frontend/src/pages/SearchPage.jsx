import { useState } from 'react';
import { searchNotes } from '../api/client';
import NoteCard from '../components/notes/NoteCard';

function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setSearched(true);

    try {
      const data = await searchNotes(query);
      setResults(data);
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Search</h1>

      <form onSubmit={handleSearch} className="mb-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search notes..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {!searched ? (
        <div className="text-center py-8">
          <p className="text-gray-500">Enter a search query to find notes</p>
        </div>
      ) : loading ? (
        <div className="text-center py-8">
          <p className="text-gray-500">Searching...</p>
        </div>
      ) : results.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">No results found for "{query}"</p>
        </div>
      ) : (
        <div>
          <p className="text-sm text-gray-500 mb-4">{results.length} results found</p>
          <div className="grid gap-4">
            {results.map((result) => (
              <NoteCard key={result.id} note={result} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default SearchPage;
