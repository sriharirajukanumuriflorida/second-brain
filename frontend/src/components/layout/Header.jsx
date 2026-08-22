import { Link } from 'react-router-dom';

function Header({ onMobileMenuToggle, user, onLogout }) {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200 fixed top-0 left-0 right-0 z-50">
      <div className="px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={onMobileMenuToggle}
            className="md:hidden p-2 rounded-md hover:bg-gray-100"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <Link to="/" className="text-xl font-bold text-gray-900">
            FDE Vault
          </Link>
        </div>
        
        <div className="flex items-center space-x-4">
          <nav className="hidden md:flex space-x-6">
            <Link to="/notes" className="text-gray-600 hover:text-gray-900">
              Notes
            </Link>
            <Link to="/search" className="text-gray-600 hover:text-gray-900">
              Search
            </Link>
            <Link to="/dashboard" className="text-gray-600 hover:text-gray-900">
              Dashboard
            </Link>
          </nav>
          
          {user && (
            <div className="flex items-center space-x-3">
              <img 
                src={user.avatar_url} 
                alt={user.username}
                className="w-8 h-8 rounded-full"
              />
              <span className="text-sm text-gray-600 hidden md:inline">{user.username}</span>
              <button
                onClick={onLogout}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header;
