// src/components/admin/MetricsGrid.tsx

import type { RequestLog } from '../../store/useAppStore';

interface MetricsGridProps {
  history: RequestLog[];
}

// Cost per 1M tokens (Groq's pricing for llama-3.3-70b)
const COST_PER_1M_TOKENS = 0.05; // $0.05 per 1M tokens

export default function MetricsGrid({ history }: MetricsGridProps) {
  const totalRequests = history.length;
  const successfulRequests = history.filter((log) => log.status === 'success');
  const avgLatency = successfulRequests.length > 0
    ? Math.round(successfulRequests.reduce((acc, log) => acc + log.latency_ms, 0) / successfulRequests.length)
    : 0;

  // 🔥 Cost & Token Calculations
  const totalTokens = history.reduce((acc, log) => acc + (log.total_tokens || 0), 0);
  const totalCost = (totalTokens / 1_000_000) * COST_PER_1M_TOKENS;

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      {/* Total Requests */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition">
        <p className="text-sm text-gray-500 font-medium">Total Requests</p>
        <p className="text-3xl font-bold text-gray-900 mt-1">{totalRequests}</p>
        <p className="text-xs text-gray-400 mt-1">
          {successfulRequests.length} successful
        </p>
      </div>

      {/* Avg Latency */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition">
        <p className="text-sm text-gray-500 font-medium">Avg Latency</p>
        <p className="text-3xl font-bold text-gray-900 mt-1">
          {avgLatency > 0 ? `${avgLatency}ms` : '—'}
        </p>
        <p className="text-xs text-gray-400 mt-1">
          Based on {successfulRequests.length} requests
        </p>
      </div>

      {/* 🔥 Total Tokens (NEW) */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition">
        <p className="text-sm text-gray-500 font-medium">Total Tokens</p>
        <p className="text-3xl font-bold text-gray-900 mt-1">
          {totalTokens.toLocaleString()}
        </p>
        <p className="text-xs text-gray-400 mt-1">
          {history.length > 0 ? `${Math.round(totalTokens / history.length)} avg per request` : 'No data'}
        </p>
      </div>

      {/* 🔥 Estimated Cost (NEW) */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm hover:shadow-md transition">
        <p className="text-sm text-gray-500 font-medium">Estimated Cost</p>
        <p className="text-3xl font-bold text-gray-900 mt-1">
          ${totalCost.toFixed(6)}
        </p>
        <p className="text-xs text-gray-400 mt-1">
          @ ${COST_PER_1M_TOKENS} / 1M tokens (Groq)
        </p>
      </div>
    </div>
  );
}