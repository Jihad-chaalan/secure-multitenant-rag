// src/App.tsx

import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { useAppStore } from "./store/useAppStore";
import UserPage from "./pages/UserPage";
import AdminPage from "./pages/AdminPage";
import DarkModeToggle from "./components/DarkModeToggle"; 
import SystemStatus from "./components/SystemStatus";

function App() {
  const { isAdmin } = useAppStore();

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
        {/* Navbar */}
        <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-3 flex items-center justify-between shadow-sm sticky top-0 z-10 transition-colors">
          {/* Left: Logo */}
          <div className="flex items-center gap-2">
            <span className="text-2xl">🔒</span>
            <h1 className="text-xl font-bold text-gray-800 dark:text-white">Secure RAG</h1>
          </div>

          {/* Right */}
          <div className="flex items-center gap-4">
            <SystemStatus />
            <div className="h-6 w-px bg-gray-300 dark:bg-gray-600" />
            <DarkModeToggle />
            <div className="h-6 w-px bg-gray-300 dark:bg-gray-600" />

            {/* 🔥 FIX: Explicit blue colors */}
            <Link
              to="/"
              className={`
                px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
                ${
                  !isAdmin
                    ? "bg-blue-600 text-white shadow-sm hover:bg-blue-700" // <-- Changed
                    : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                }
              `}
            >
              Chat
            </Link>

            <Link
              to="/admin"
              className={`
                px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
                ${
                  isAdmin
                    ? "bg-blue-600 text-white shadow-sm hover:bg-blue-700" // <-- Changed
                    : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                }
              `}
            >
              Dashboard
            </Link>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<UserPage />} />
          <Route path="/admin" element={<AdminPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;