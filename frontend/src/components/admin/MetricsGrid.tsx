// src/components/admin/MetricsGrid.tsx

import type { RequestLog } from '../../store/useAppStore';

interface MetricsGridProps {
  history: RequestLog[];
}

export default function MetricsGrid({ history }: MetricsGridProps) {
  const totalRequests = history.length;
  const successfulRequests = history.filter((log) => log.status === 'success');
  const avgLatency = successfulRequests.length > 0
    ? Math.round(successfulRequests.reduce((acc, log) => acc + log.latency_ms, 0) / successfulRequests.length)
    : 0;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition">
        <p className="text-sm text-gray-500 font-medium">Total Requests</p>
        <p className="text-3xl font-bold text-gray-900 mt-1">{totalRequests}</p>
        <p className="text-xs text-gray-400 mt-1">
          {successfulRequests.length} successful
        </p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition">
        <p className="text-sm text-gray-500 font-medium">Avg Latency</p>
        <p className="text-3xl font-bold text-gray-900 mt-1">
          {avgLatency > 0 ? `${avgLatency}ms` : '—'}
        </p>
        <p className="text-xs text-gray-400 mt-1">
          Based on {successfulRequests.length} requests
        </p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition">
        <p className="text-sm text-gray-500 font-medium">System Status</p>
        <div className="flex items-center gap-2 mt-1">
          <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
          <span className="text-3xl font-bold text-green-600">Online</span>
        </div>
        <p className="text-xs text-gray-400 mt-1">
          Last request: {history.length > 0 ? new Date(history[0].timestamp).toLocaleTimeString() : 'Never'}
        </p>
      </div>
    </div>
  );
}