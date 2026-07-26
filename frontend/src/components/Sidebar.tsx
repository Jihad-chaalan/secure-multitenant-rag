// src/components/Sidebar.tsx

import { useAppStore } from '../store/useAppStore';
import { DEPARTMENTS, ROLES_MAP } from '../utils/constants';

export default function Sidebar() {
  const { department, role, setDepartment, setRole } = useAppStore();

  // Google Drive folder link (replace with your actual folder link)
  const driveFolderLink =
    'https://drive.google.com/drive/folders/1nKe_ZsnnfX92fV0ue6IhCeqLW75-AzNt?usp=drive_link';

  return (
    <aside className="w-80 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 flex flex-col h-full shadow-sm">
      {/* Header */}
      <div className="px-6 pt-6 pb-4 border-b border-gray-100 dark:border-gray-800">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-sm shadow-sm">
            R
          </div>
          <div>
            <h1 className="text-sm font-semibold text-gray-800 dark:text-gray-100 tracking-tight">
              Secure RAG
            </h1>
            <p className="text-[10px] text-gray-400 dark:text-gray-500 font-medium uppercase tracking-wider">
              Multi-Tenant · Enterprise
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 px-6 py-5 space-y-6 overflow-y-auto">
        {/* Context Section */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
              Context
            </span>
            <span className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
          </div>

          <div className="space-y-3.5">
            {/* Department */}
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1.5">
                Department
              </label>
              <select
                value={department}
                onChange={(e) => {
                  const newDept = e.target.value;
                  setDepartment(newDept);
                  setRole(ROLES_MAP[newDept][0]);
                }}
                className="w-full text-sm border border-gray-200 dark:border-gray-700 rounded-lg px-3.5 py-2.5 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition appearance-none cursor-pointer"
              >
                {DEPARTMENTS.map((dept) => (
                  <option key={dept} value={dept}>
                    {dept.replace('_', ' ')}
                  </option>
                ))}
              </select>
            </div>

            {/* Role */}
            <div>
              <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1.5">
                Role
              </label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full text-sm border border-gray-200 dark:border-gray-700 rounded-lg px-3.5 py-2.5 bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition appearance-none cursor-pointer"
              >
                {ROLES_MAP[department].map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Active Context Badge */}
        <div className="bg-blue-50 dark:bg-blue-950/30 rounded-xl border border-blue-100 dark:border-blue-800/50 p-3.5">
          <p className="text-[10px] font-medium text-blue-600 dark:text-blue-400 uppercase tracking-wider flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
            Active Context
          </p>
          <p className="text-sm font-semibold text-gray-800 dark:text-gray-100 mt-0.5">
            {department} / {role}
          </p>
        </div>

        {/* Data Source Section */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <span className="text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
              Data Source
            </span>
            <span className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
          </div>

          <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-gray-200 dark:border-gray-700 p-3.5 space-y-2">
            <a
              href={driveFolderLink}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-sm font-medium text-blue-600 dark:text-blue-400 hover:underline"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M7 14c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm5-1c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm5-1c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z" />
              </svg>
              📁 View Documents
            </a>
            <p className="text-[11px] text-gray-400 dark:text-gray-500 leading-relaxed">
              This folder contains all documents ingested by the RAG system. Files are automatically chunked, embedded, and indexed for retrieval.
            </p>
          </div>
        </div>
      </div>

      {/* Footer: System Status */}
      <div className="px-6 py-4 border-t border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/30">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-xs text-gray-500 dark:text-gray-400 font-medium">System Online</span>
          </div>
          <span className="text-[10px] text-gray-400 dark:text-gray-500 font-mono">v2.0</span>
        </div>
      </div>
    </aside>
  );
}