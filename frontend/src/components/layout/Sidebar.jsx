import { Link } from 'react-router-dom';

function Sidebar() {
  return (
    <aside className="hidden md:block fixed left-0 top-16 bottom-0 w-64 bg-white border-r border-gray-200 overflow-y-auto">
      <nav className="p-4 space-y-2">
        <Link
          to="/notes"
          className="block px-4 py-2 rounded-md hover:bg-gray-100 text-gray-700"
        >
          📝 Notes
        </Link>
        <Link
          to="/search"
          className="block px-4 py-2 rounded-md hover:bg-gray-100 text-gray-700"
        >
          🔍 Search
        </Link>
        <Link
          to="/dashboard"
          className="block px-4 py-2 rounded-md hover:bg-gray-100 text-gray-700"
        >
          📊 Dashboard
        </Link>
      </nav>
      
      <div className="p-4 border-t border-gray-200 mt-4">
        <p className="text-sm text-gray-500">Phase 2: Responsive Web UI</p>
      </div>
    </aside>
  );
}

export default Sidebar;
