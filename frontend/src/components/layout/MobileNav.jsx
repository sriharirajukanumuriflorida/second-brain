import { Link } from 'react-router-dom';

function MobileNav({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="md:hidden fixed inset-0 z-50">
      <div className="absolute inset-0 bg-black bg-opacity-50" onClick={onClose} />
      <div className="absolute left-0 top-0 bottom-0 w-64 bg-white shadow-lg">
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold">Menu</h2>
        </div>
        <nav className="p-4 space-y-2">
          <Link
            to="/notes"
            onClick={onClose}
            className="block px-4 py-2 rounded-md hover:bg-gray-100 text-gray-700"
          >
            📝 Notes
          </Link>
          <Link
            to="/search"
            onClick={onClose}
            className="block px-4 py-2 rounded-md hover:bg-gray-100 text-gray-700"
          >
            🔍 Search
          </Link>
          <Link
            to="/dashboard"
            onClick={onClose}
            className="block px-4 py-2 rounded-md hover:bg-gray-100 text-gray-700"
          >
            📊 Dashboard
          </Link>
        </nav>
      </div>
    </div>
  );
}

export default MobileNav;
