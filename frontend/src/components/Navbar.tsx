// src/components/Navbar.tsx

import { useState } from "react";
import { Link } from "react-router-dom";
import { useAppStore } from "../store/useAppStore";
import DarkModeToggle from "./DarkModeToggle";
import SystemStatus from "./SystemStatus";
import InfoTooltip from "./InfoTooltip";
import MobileSidebar from "./MobileSidebar";

// ✅ Custom SVG Hamburger (no external dependency)
const HamburgerIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
  </svg>
);

export default function Navbar() {
  const { isAdmin } = useAppStore();
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  return (
    <>
      <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 sm:px-6 py-3 flex items-center justify-between shadow-sm sticky top-0 z-10 transition-colors">
        {/* Left: Hamburger + Logo + Title + Info */}
        <div className="flex items-center gap-2 min-w-0">
          {/* Hamburger (mobile only) */}
          <button
            onClick={() => setMobileSidebarOpen(true)}
            className="lg:hidden p-2 -ml-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition"
            aria-label="Open sidebar"
          >
            <HamburgerIcon />
          </button>

          {/* Logo / Icon */}
          <div className="flex items-center justify-center w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 text-white text-sm font-bold shadow-sm flex-shrink-0">
            R
          </div>

          {/* Title */}
          <h1 className="text-base sm:text-lg font-bold text-gray-800 dark:text-white tracking-tight truncate">
            Enterprise RAG
          </h1>

          <InfoTooltip />
        </div>

        {/* Right: Navigation + Controls */}
        <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
          <div className="hidden sm:flex items-center gap-1 bg-gray-100 dark:bg-gray-700/50 rounded-lg p-0.5">
            <Link
              to="/"
              className={`
                px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200
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
                px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200
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

          <div className="hidden sm:block h-6 w-px bg-gray-300 dark:bg-gray-600" />
          <DarkModeToggle />
          <div className="hidden sm:block h-6 w-px bg-gray-300 dark:bg-gray-600" />
          <SystemStatus />
        </div>
      </nav>

      <MobileSidebar isOpen={mobileSidebarOpen} onClose={() => setMobileSidebarOpen(false)} />
    </>
  );
}