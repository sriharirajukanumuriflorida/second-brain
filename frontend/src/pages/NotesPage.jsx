import { useState, useEffect } from 'react';
import { getNotes, getFolders } from '../api/client';
import NoteCard from '../components/notes/NoteCard';

function NotesPage() {
  const [notes, setNotes] = useState([]);
  const [folders, setFolders] = useState([]);
  const [selectedFolder, setSelectedFolder] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadNotes();
    loadFolders();
  }, [selectedFolder]);

  const loadNotes = async () => {
    try {
      const data = await getNotes(selectedFolder);
      setNotes(data);
    } catch (error) {
      console.error('Failed to load notes:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadFolders = async () => {
    try {
      const data = await getFolders();
      setFolders(data);
    } catch (error) {
      console.error('Failed to load folders:', error);
    }
  };

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Notes</h1>
        
        <div className="flex flex-wrap gap-2 mb-4">
          <button
            onClick={() => setSelectedFolder(null)}
            className={`px-4 py-2 rounded-md ${
              selectedFolder === null
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            All Folders
          </button>
          {folders.map((folder) => (
            <button
              key={folder.name}
              onClick={() => setSelectedFolder(folder.name)}
              className={`px-4 py-2 rounded-md ${
                selectedFolder === folder.name
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {folder.name} ({folder.note_count})
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <p className="text-gray-500">Loading notes...</p>
        </div>
      ) : notes.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">No notes found</p>
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {notes.map((note) => (
            <NoteCard key={note.id} note={note} />
          ))}
        </div>
      )}
    </div>
  );
}

export default NotesPage;
