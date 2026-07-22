// src/components/SourceCard.tsx

import type { Source } from '../types';

interface SourceCardProps {
  source: Source;
  index: number;
}

export default function SourceCard({ source, index }: SourceCardProps) {
  const { scores, file, department, role, text_preview, chunk_id } = source;

  return (
    <div className="border border-gray-200 rounded-lg p-4 bg-gray-50 hover:bg-gray-100 transition">
      <div className="flex items-start justify-between">
        <div>
          <p className="font-medium text-gray-800 text-sm flex items-center gap-2">
            <span className="text-gray-400 text-xs font-mono bg-gray-200 px-1.5 py-0.5 rounded">
              #{index + 1}
            </span>
            {file}
          </p>
          <p className="text-xs text-gray-500">
            {department} / {role}
          </p>
          {chunk_id && (
            <p className="text-xs text-gray-400 font-mono mt-0.5">
              ID: {chunk_id.slice(-8)}
            </p>
          )}
        </div>
      </div>

      <div className="mt-2 flex flex-wrap gap-2 text-xs">
        {scores.vector !== null && scores.vector !== undefined && (
          <span className="bg-purple-50 text-purple-700 px-2 py-0.5 rounded border border-purple-100">
            Vector: {scores.vector.toFixed(3)}
          </span>
        )}
        {scores.rrf !== null && scores.rrf !== undefined && (
          <span className="bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded border border-indigo-100">
            RRF: {scores.rrf.toFixed(4)}
          </span>
        )}
        {scores.reranker !== null && scores.reranker !== undefined && (
          <span className="bg-pink-50 text-pink-700 px-2 py-0.5 rounded border border-pink-100">
            Reranker: {scores.reranker.toFixed(2)}
          </span>
        )}
      </div>

      <p className="mt-2 text-sm text-gray-700 line-clamp-3 leading-relaxed">
        {text_preview}
      </p>
    </div>
  );
}