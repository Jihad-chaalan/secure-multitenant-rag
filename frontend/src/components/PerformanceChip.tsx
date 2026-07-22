// src/components/PerformanceChip.tsx

import type { PerformanceMetrics } from '../types';

interface PerformanceChipProps {
  performance: PerformanceMetrics;
}

export default function PerformanceChip({ performance }: PerformanceChipProps) {
  return (
    <div className="inline-flex items-center flex-wrap gap-2 px-3 py-1.5 bg-gray-100 rounded-full text-xs text-gray-600 border border-gray-200">
      <span className="font-medium">⏱️ {performance.latency_ms}ms</span>
      <span className="text-gray-300">|</span>
      <span>Retrieval {performance.retrieval_ms}ms</span>
      <span className="text-gray-300">|</span>
      <span>Rerank {performance.reranking_ms}ms</span>
      <span className="text-gray-300">|</span>
      <span>LLM {performance.generation_ms}ms</span>
    </div>
  );
}