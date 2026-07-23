// src/components/admin/SecurityTable.tsx

import type { SecurityEvent } from '../../types';

interface SecurityTableProps {
  events: SecurityEvent[];
}

export default function SecurityTable({ events }: SecurityTableProps) {
  if (events.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="font-semibold text-gray-800">🛡️ Security Events</h3>
        </div>
        <div className="p-12 text-center text-gray-400">
          <p className="text-4xl mb-2">✅</p>
          <p>No security events detected.</p>
          <p className="text-sm mt-1">All queries have been safe.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 className="font-semibold text-gray-800">🛡️ Security Events</h3>
        <span className="text-xs text-red-500 font-medium">
          {events.length} blocked attempts
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
            <tr>
              <th className="px-6 py-3">Time</th>
              <th className="px-6 py-3">Department</th>
              <th className="px-6 py-3">Role</th>
              <th className="px-6 py-3">Query</th>
              <th className="px-6 py-3">Reason</th>
              <th className="px-6 py-3 text-center">Risk Score</th>
              <th className="px-6 py-3 text-center">Category</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {events.map((event) => (
              <tr key={event.id} className="hover:bg-red-50 transition">
                <td className="px-6 py-3 text-gray-500 text-xs whitespace-nowrap">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </td>
                <td className="px-6 py-3 font-medium text-gray-700">
                  {event.department}
                </td>
                <td className="px-6 py-3 text-gray-600">{event.role}</td>
                <td className="px-6 py-3 text-gray-800 max-w-xs truncate">
                  {event.query}
                </td>
                <td className="px-6 py-3 text-red-600 font-medium">
                  {event.reason}
                </td>
                <td className="px-6 py-3 text-center">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      event.risk_score >= 80
                        ? 'bg-red-100 text-red-800'
                        : event.risk_score >= 50
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-green-100 text-green-800'
                    }`}
                  >
                    {event.risk_score}
                  </span>
                </td>
                <td className="px-6 py-3 text-center">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    {event.category}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}