// src/App.tsx

import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { useAppStore } from './store/useAppStore';
import UserPage from './pages/UserPage';
import AdminPage from './pages/AdminPage';

function App() {
  const { isAdmin, toggleAdmin } = useAppStore();

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        {/* Navbar */}
        <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between shadow-sm sticky top-0 z-10">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🔒</span>
            <h1 className="text-xl font-bold text-gray-800">Secure RAG</h1>
          </div>
          <div className="flex items-center gap-4">
            <Link
              to="/"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                !isAdmin ? 'bg-primary-600 text-white' : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Chat
            </Link>
            <Link
              to="/admin"
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
                isAdmin ? 'bg-primary-600 text-white' : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Dashboard
            </Link>
          </div>
        </nav>

        {/* Routes */}
        <Routes>
          <Route path="/" element={<UserPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;