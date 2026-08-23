import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import { healthCheck, getStatus } from './api/client';
import * as auth from './api/auth';
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import MobileNav from './components/layout/MobileNav';
import NotesPage from './pages/NotesPage';
import NotePage from './pages/NotePage';
import SearchPage from './pages/SearchPage';
import DashboardPage from './pages/DashboardPage';
import AdminPage from './pages/AdminPage';
import ChatPage from './pages/ChatPage';
import LoginPage from './pages/LoginPage';
import AuthCallbackPage from './pages/AuthCallbackPage';
import AccessPage from './pages/AccessPage';

function App() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isReadOnly, setIsReadOnly] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    checkAuth();
    loadStatus();
  }, []);

  const checkAuth = () => {
    const token = localStorage.getItem('access_token');
    const userStr = localStorage.getItem('user');
    if (token && userStr) {
      setIsAuthenticated(true);
      setUser(JSON.parse(userStr));
    } else if (localStorage.getItem('readonly_access_token') || localStorage.getItem('access_mode') === 'readonly') {
      // Shared-link visitor: authorized by a claimed temporary access token.
      setIsReadOnly(true);
    }
  };

  const loadStatus = async () => {
    try {
      const statusData = await getStatus();
      setStatus(statusData);
    } catch (error) {
      console.error('Failed to load status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      await auth.logout(token);
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    localStorage.removeItem('readonly_access_token');
    localStorage.removeItem('access_mode');
    setIsAuthenticated(false);
    setUser(null);
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  // Router wraps the WHOLE app so router hooks always have a provider.
  // The /access route is always reachable (it claims a shared read-only link).
  // A logged-in user OR a read-only visitor sees the app shell; otherwise login.
  const showApp = isAuthenticated || isReadOnly;

  return (
    <Router>
      <Routes>
        <Route path="/access" element={<AccessPage />} />
        <Route path="/auth/callback" element={<AuthCallbackPage />} />
        <Route
          path="/*"
          element={
            !showApp ? (
              <LoginPage />
            ) : (
              <div className="min-h-screen bg-gray-50">
                <Header
                  onMobileMenuToggle={toggleMobileMenu}
                  user={user}
                  onLogout={handleLogout}
                  isReadOnly={isReadOnly}
                />

                <div className="flex">
                  <Sidebar user={user} />

                  <MobileNav isOpen={isMobileMenuOpen} onClose={toggleMobileMenu} user={user} />

                  <main className="flex-1 p-4 md:p-8 lg:ml-64">
                    <Routes>
                      <Route path="/" element={<Navigate to="/notes" />} />
                      <Route path="/notes" element={<NotesPage />} />
                      <Route path="/notes/:id" element={<NotePage />} />
                      <Route path="/search" element={<SearchPage />} />
                      <Route path="/dashboard" element={<DashboardPage />} />
                      <Route path="/admin" element={<AdminPage />} />
                      <Route path="/chat" element={<ChatPage />} />
                    </Routes>
                  </main>
                </div>
              </div>
            )
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
