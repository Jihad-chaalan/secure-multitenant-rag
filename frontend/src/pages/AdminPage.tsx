// src/pages/AdminPage.tsx

import { useAppStore } from '../store/useAppStore';
import MetricsGrid from '../components/admin/MetricsGrid';
import RequestTable from '../components/admin/RequestTable';
import SecurityTable from '../components/admin/SecurityTable';
export default function AdminPage() {
  const { requestHistory, securityHistory, clearHistory } = useAppStore();

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">📊 Admin Dashboard</h2>
          <p className="text-sm text-gray-500 mt-1">
            {requestHistory.length} requests · {securityHistory.length} security events
          </p>
        </div>
        <button
          onClick={clearHistory}
          className="text-sm text-red-500 hover:text-red-700 hover:underline transition"
        >
          Clear History
        </button>
      </div>

      {/* Metrics */}
      <MetricsGrid history={requestHistory} />

      {/* Request History Table */}
      <RequestTable logs={requestHistory} />

      {/* 🔥 Security Events Table (AI Firewall Logs) */}
      <div className="mt-8">
        <SecurityTable events={securityHistory} />
      </div>
    </div>
  );
}