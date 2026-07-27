// src/pages/AdminPage.tsx

import { useState } from 'react';
import { useAppStore } from '../store/useAppStore';
import MetricsGrid from '../components/admin/MetricsGrid';
import RequestTable from '../components/admin/RequestTable';
import SecurityTable from '../components/admin/SecurityTable';
import TokenUsageTable from '../components/admin/TokenUsageTable';
import SimpleTooltip from '../components/SimpleTooltip';
import { syncApi } from '../api/client';

export default function AdminPage() {
  const { requestHistory, securityHistory, clearHistory, clearSecurityHistory } = useAppStore();
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleClearAll = () => {
    if (window.confirm('Clear all history (requests + security events)?')) {
      clearHistory();
      clearSecurityHistory();
    }
  };

  const handleSync = async () => {
    setIsSyncing(true);
    setSyncMessage(null);

    try {
      const response = await syncApi.triggerSync();
      setSyncMessage({
        type: 'success',
        text: response.message || 'Knowledge base refreshed successfully!',
      });
    } catch (error) {
      setSyncMessage({
        type: 'error',
        text: 'Failed to refresh knowledge base. Please try again.',
      });
      console.error('Sync error:', error);
    } finally {
      setIsSyncing(false);
      setTimeout(() => setSyncMessage(null), 5000);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">📊 Admin Dashboard</h2>
          <p className="text-sm text-gray-500 mt-1">
            {requestHistory.length} requests · {securityHistory.length} security events
          </p>
        </div>
        <button
          onClick={handleClearAll}
          className="text-sm text-red-500 hover:text-red-700 hover:underline transition"
        >
          Clear All History
        </button>
      </div>

      <MetricsGrid history={requestHistory} />
      <RequestTable logs={requestHistory} />
      <TokenUsageTable />
      <SecurityTable events={securityHistory} />

      {/* Footer with Sync Button + Info Tooltip */}
      <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="text-xs text-gray-400 dark:text-gray-500">
          Knowledge Base • {requestHistory.length > 0 ? `${requestHistory.length} queries` : 'No queries yet'}
        </div>

        <div className="flex items-center gap-4">
          {syncMessage && (
            <span
              className={`text-sm font-medium ${
                syncMessage.type === 'success' ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {syncMessage.text}
            </span>
          )}

          <div className="flex items-center gap-2">
            <button
              onClick={handleSync}
              disabled={isSyncing}
              className={`
                flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all
                ${
                  isSyncing
                    ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm'
                }
              `}
            >
              {isSyncing ? (
                <>
                  <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                  </svg>
                  Refreshing...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h5" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 20v-5h-5" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4l5 5" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 20l-5-5" />
                  </svg>
                  Refresh Knowledge Base
                </>
              )}
            </button>

            <SimpleTooltip>
              <h4 className="font-bold text-gray-800 dark:text-white text-sm mb-1">
                📘 About Refresh Knowledge Base
              </h4>
              <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed">
                This manually triggers a full re‑index of all documents from Google Drive.
              </p>
              <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                <p className="text-xs font-medium text-gray-700 dark:text-gray-200">
                  Why manual?
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  • The demo runs on a single VM with a small dataset (~7 docs).<br />
                  • A full re‑index takes ~2 seconds, so manual sync is perfectly fine.<br />
                  • In production, this would be replaced by a cron job (auto‑sync every 6 hours) or a webhook (instant updates via Google Drive notifications).
                </p>
              </div>
              <div className="mt-2 pt-1 border-t border-gray-200 dark:border-gray-700">
                <p className="text-xs font-medium text-gray-700 dark:text-gray-200">
                  Why not workers/queues?
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  • The ingestion pipeline is lightweight and runs synchronously.<br />
                  • For a portfolio project, adding Redis/RQ would over‑engineer the solution.<br />
                  • The <span className="font-mono">/sync</span> endpoint is designed to be easily hooked into a background scheduler if needed.
                </p>
              </div>
            </SimpleTooltip>
          </div>
        </div>
      </div>
    </div>
  );
}