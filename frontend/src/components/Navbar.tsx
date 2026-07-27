// src/components/Navbar.tsx

import { Link } from "react-router-dom";
import { useAppStore } from "../store/useAppStore";
import DarkModeToggle from "./DarkModeToggle";
import SystemStatus from "./SystemStatus";
import InfoTooltip from "./InfoTooltip";

export default function Navbar() {
  const { isAdmin } = useAppStore();

  return (
    <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-3 flex items-center justify-between shadow-sm sticky top-0 z-10 transition-colors">
      {/* Left: Logo + Title + Info */}
      <div className="flex items-center gap-1">
        <span className="text-2xl">🔒</span>
        <h1 className="text-lg font-bold text-gray-800 dark:text-white tracking-tight">
          Enterprise RAG
        </h1>
        <InfoTooltip />
      </div>

      {/* Right: Navigation + Controls */}
      <div className="flex items-center gap-3">
        {/* Navigation Links */}
        <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-700/50 rounded-lg p-0.5">
          <Link
            to="/"
            className={`
              px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-200
              ${
                !isAdmin
                  ? "bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm"
                  : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
              }
            `}
          >
            Chat
          </Link>
          <Link
            to="/admin"
            className={`
              px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-200
              ${
                isAdmin
                  ? "bg-white dark:bg-gray-800 text-gray-900 dark:text-white shadow-sm"
                  : "text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
              }
            `}
          >
            Dashboard
          </Link>
        </div>

        {/* Divider */}
        <div className="h-6 w-px bg-gray-300 dark:bg-gray-600" />

        {/* Dark Mode */}
        <DarkModeToggle />

        {/* Divider */}
        <div className="h-6 w-px bg-gray-300 dark:bg-gray-600" />

        {/* System Status */}
        <SystemStatus />
      </div>
    </nav>
  );
}