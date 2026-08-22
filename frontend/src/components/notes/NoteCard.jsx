import { Link } from 'react-router-dom';

function NoteCard({ note }) {
  return (
    <Link
      to={`/notes/${note.id}`}
      className="block bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow"
    >
      <h3 className="font-semibold text-gray-900 mb-2">{note.title}</h3>
      <p className="text-sm text-gray-500 mb-2">{note.path}</p>
      <div className="flex flex-wrap gap-1">
        {note.tags.slice(0, 3).map((tag) => (
          <span
            key={tag}
            className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
          >
            #{tag}
          </span>
        ))}
        {note.tags.length > 3 && (
          <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
            +{note.tags.length - 3}
          </span>
        )}
      </div>
    </Link>
  );
}

export default NoteCard;
