// src/components/admin/RequestTable.tsx

import type { RequestLog } from '../../store/useAppStore';

interface RequestTableProps {
  logs: RequestLog[];
}

export default function RequestTable({ logs }: RequestTableProps) {
  if (logs.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="font-semibold text-gray-800">Recent Requests</h3>
        </div>
        <div className="p-12 text-center text-gray-400">
          <p className="text-4xl mb-2">📭</p>
          <p>No requests logged yet.</p>
          <p className="text-sm mt-1">Start chatting in the User page to see data here.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 className="font-semibold text-gray-800">Recent Requests</h3>
        <span className="text-xs text-gray-400">{logs.length} requests</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            <tr>
              <th className="px-6 py-3">Time</th>
              <th className="px-6 py-3">Department</th>
              <th className="px-6 py-3">Role</th>
              <th className="px-6 py-3">Query</th>
              <th className="px-6 py-3 text-right">Latency</th>
              <th className="px-6 py-3 text-center">Sources</th>
              <th className="px-6 py-3 text-center">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {logs.map((log) => (
              <tr key={log.id} className="hover:bg-gray-50 transition">
                <td className="px-6 py-3 text-gray-500 text-xs whitespace-nowrap">
                  {new Date(log.timestamp).toLocaleTimeString()}
                </td>
                <td className="px-6 py-3 font-medium text-gray-700">{log.department}</td>
                <td className="px-6 py-3 text-gray-600">{log.role}</td>
                <td className="px-6 py-3 text-gray-800 max-w-xs truncate">
                  {log.query.length > 60 ? log.query.slice(0, 60) + '…' : log.query}
                </td>
                <td className="px-6 py-3 text-right font-mono text-xs">
                  {log.status === 'success' ? `${log.latency_ms}ms` : '—'}
                </td>
                <td className="px-6 py-3 text-center">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {log.source_count}
                  </span>
                </td>
                <td className="px-6 py-3 text-center">
                  {log.status === 'success' ? (
                    <span className="inline-flex items-center gap-1 text-green-600">
                      <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                      OK
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-red-600">
                      <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                      Error
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}