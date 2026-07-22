// src/pages/AdminPage.tsx

import { useAppStore } from '../store/useAppStore';
import MetricsGrid from '../components/admin/MetricsGrid';
import RequestTable from '../components/admin/RequestTable';

export default function AdminPage() {
  const { requestHistory, clearHistory } = useAppStore();

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">📊 Admin Dashboard</h2>
          <p className="text-sm text-gray-500 mt-1">
            Session history — {requestHistory.length} requests tracked
          </p>
        </div>
        {requestHistory.length > 0 && (
          <button
            onClick={clearHistory}
            className="text-sm text-red-500 hover:text-red-700 hover:underline transition"
          >
            Clear History
          </button>
        )}
      </div>

      <MetricsGrid history={requestHistory} />
      <RequestTable logs={requestHistory} />
    </div>
  );
}