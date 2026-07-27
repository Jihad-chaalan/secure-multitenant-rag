// src/components/InfoTooltip.tsx

import { useState } from 'react';

export default function InfoTooltip() {
  const [isVisible, setIsVisible] = useState(false);

  return (
    <div
      className="relative inline-flex items-center ml-1"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {/* Info Icon */}
      <button
        className="w-5 h-5 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs font-bold flex items-center justify-center hover:bg-gray-300 dark:hover:bg-gray-600 transition"
        aria-label="Project info"
      >
        i
      </button>

      {/* Tooltip */}
      {isVisible && (
        <div className="absolute top-full left-0 mt-2 w-80 sm:w-96 p-5 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 z-50 text-left max-h-[80vh] overflow-y-auto">
          {/* Title */}
          <h4 className="font-bold text-gray-800 dark:text-white text-base mb-2">
            🔒 Enterprise RAG
          </h4>

          {/* Description */}
          <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed mb-3">
            Production‑style AI knowledge assistant that answers questions
            about your internal documents using advanced retrieval techniques.
          </p>

          {/* How It Works */}
          <div className="mb-3">
            <p className="text-xs font-semibold text-gray-700 dark:text-gray-200 uppercase tracking-wider mb-1">
              ⚙️ How It Works
            </p>
            <ol className="text-xs text-gray-600 dark:text-gray-300 space-y-0.5 list-decimal list-inside">
              <li>Documents are chunked, embedded, and stored in a vector database.</li>
              <li>Your question is embedded and compared against the database.</li>
              <li>Hybrid search (BM25 + Vector) finds the most relevant chunks.</li>
              <li>A Cross‑Encoder reranker re‑orders the chunks by relevance.</li>
              <li>The LLM (Groq) generates a final answer with sources.</li>
            </ol>
          </div>

          {/* Features */}
          <div className="mb-3">
            <p className="text-xs font-semibold text-gray-700 dark:text-gray-200 uppercase tracking-wider mb-1">
              ✨ Key Features
            </p>
            <ul className="text-xs text-gray-600 dark:text-gray-300 space-y-0.5 list-disc list-inside">
              <li><span className="font-medium">Multi‑Tenancy:</span> Each department and role has isolated data.</li>
              <li><span className="font-medium">Hybrid Search:</span> BM25 + Vector for maximum recall.</li>
              <li><span className="font-medium">Reranking:</span> Cross‑Encoder re‑ranks for precision.</li>
              <li><span className="font-medium">AI Firewall:</span> Detects and blocks jailbreak attempts.</li>
              <li><span className="font-medium">Google Drive Sync:</span> Documents are ingested from Google Drive.</li>
            </ul>
          </div>

          {/* Test Multi‑User */}
          <div className="mb-2 p-2.5 bg-blue-50 dark:bg-blue-950/30 rounded-lg border border-blue-100 dark:border-blue-800/50">
            <p className="text-xs font-medium text-blue-700 dark:text-blue-300">
              🧪 Test Multi‑User Isolation
            </p>
            <p className="text-xs text-blue-600 dark:text-blue-400 mt-0.5">
              Change the <span className="font-semibold">Department</span> and{' '}
              <span className="font-semibold">Role</span> in the sidebar.
              Each combination has tailored documents and sample questions.
              Try switching from <span className="font-semibold">Department_A / Engineering</span>{' '}
              to <span className="font-semibold">Department_B / Marketing</span> to see different data.
            </p>
          </div>

          {/* Tech Stack */}
          <div className="flex flex-wrap gap-1.5 mt-1 pt-2 border-t border-gray-200 dark:border-gray-700">
            <span className="text-[10px] bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-0.5 rounded-full">
              FastAPI
            </span>
            <span className="text-[10px] bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 px-2 py-0.5 rounded-full">
              React
            </span>
            <span className="text-[10px] bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 px-2 py-0.5 rounded-full">
              ChromaDB
            </span>
            <span className="text-[10px] bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 px-2 py-0.5 rounded-full">
              Groq
            </span>
            <span className="text-[10px] bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 px-2 py-0.5 rounded-full">
              Sentence‑Transformers
            </span>
          </div>
        </div>
      )}
    </div>
  );
}