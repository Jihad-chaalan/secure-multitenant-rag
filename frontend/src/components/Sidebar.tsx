// src/components/Sidebar.tsx

import { useAppStore } from '../store/useAppStore';
import { DEPARTMENTS, ROLES_MAP } from '../utils/constants';

export default function Sidebar() {
  const { department, role, setDepartment, setRole } = useAppStore();

  return (
    <aside className="w-72 bg-white border-r border-gray-200 p-6 flex flex-col h-full">
      <h2 className="text-lg font-bold text-gray-800 mb-6">🔒 Context</h2>

      <div className="space-y-4 flex-1">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Department
          </label>
          <select
            value={department}
            onChange={(e) => {
              const newDept = e.target.value;
              setDepartment(newDept);
              setRole(ROLES_MAP[newDept][0]);
            }}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          >
            {DEPARTMENTS.map((dept) => (
              <option key={dept} value={dept}>{dept}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Role
          </label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          >
            {ROLES_MAP[department].map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>

        <div className="mt-4 p-3 bg-primary-50 rounded-lg border border-primary-100">
          <p className="text-xs text-gray-600">🔒 Active Context</p>
          <p className="text-sm font-medium text-gray-800">{department} / {role}</p>
        </div>
      </div>

      <div className="pt-4 border-t border-gray-200">
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
          API Online
        </div>
      </div>
    </aside>
  );
}