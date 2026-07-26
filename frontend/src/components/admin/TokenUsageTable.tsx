// src/components/admin/TokenUsageTable.tsx

import { useAppStore } from '../../store/useAppStore';

export default function TokenUsageTable() {
  const { requestHistory } = useAppStore();

  const tokenizedRequests = requestHistory.filter(
    (log) => log.total_tokens !== undefined && log.total_tokens > 0
  );

  if (tokenizedRequests.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="font-semibold text-gray-800">🧮 Token Usage</h3>
        </div>
        <div className="p-12 text-center text-gray-400">
          <p className="text-4xl mb-2">📭</p>
          <p>No token data available yet.</p>
          <p className="text-sm mt-1">Make a request to start tracking usage.</p>
        </div>
      </div>
    );
  }

  const totalTokens = tokenizedRequests.reduce((sum, log) => sum + (log.total_tokens || 0), 0);
  const totalPrompt = tokenizedRequests.reduce((sum, log) => sum + (log.prompt_tokens || 0), 0);
  const totalCompletion = tokenizedRequests.reduce((sum, log) => sum + (log.completion_tokens || 0), 0);

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 className="font-semibold text-gray-800">🧮 Token Usage</h3>
        <div className="flex gap-4 text-xs text-gray-500">
          <span>Prompt: {totalPrompt.toLocaleString()}</span>
          <span>Completion: {totalCompletion.toLocaleString()}</span>
          <span className="font-semibold text-gray-700">Total: {totalTokens.toLocaleString()}</span>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            <tr>
              <th className="px-6 py-3">Request ID</th>
              <th className="px-6 py-3">Query</th>
              <th className="px-6 py-3 text-right">Prompt</th>
              <th className="px-6 py-3 text-right">Completion</th>
              <th className="px-6 py-3 text-right font-bold">Total</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {tokenizedRequests.map((log) => (
              <tr key={log.id} className="hover:bg-gray-50 transition">
                <td className="px-6 py-3 font-mono text-xs text-gray-400">
                  {log.id.slice(0, 8)}...{log.id.slice(-4)}
                </td>
                <td className="px-6 py-3 text-gray-700 max-w-xs truncate">
                  {log.query}
                </td>
                <td className="px-6 py-3 text-right text-gray-600">
                  {log.prompt_tokens?.toLocaleString() || '—'}
                </td>
                <td className="px-6 py-3 text-right text-gray-600">
                  {log.completion_tokens?.toLocaleString() || '—'}
                </td>
                <td className="px-6 py-3 text-right font-medium text-gray-900">
                  {log.total_tokens?.toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}