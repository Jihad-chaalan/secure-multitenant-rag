// src/types/index.ts

export interface ScoreInfo {
  vector: number | null;
  rrf: number | null;
  reranker: number | null;
}

export interface Source {
  chunk_id: string;
  file: string;
  department: string;
  role: string;
  text_preview: string;
  scores: ScoreInfo;
}

export interface PerformanceMetrics {
  latency_ms: number;
  retrieval_ms: number;
  reranking_ms: number;
  generation_ms: number;
  scanner_ms?: number;
}

export interface SecurityWarning {
  blocked: boolean;
  category: string;
  message: string;
  risk_score: number;
}

export interface ChatMetadata {
  request_id: string;
  department: string;
  role: string;
  retrieved_candidates: number;
  returned_chunks: number;
  retriever: string;
  reranker: string;
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  metadata: ChatMetadata;
  performance: PerformanceMetrics;
  status: string;
  security_warning: SecurityWarning | null;
}

export interface ChatRequest {
  query: string;
  department: string;
  role: string;
  top_k?: number;
}

// Admin Types
export interface RequestLog {
  id: string;
  timestamp: string;
  query: string;
  department: string;
  role: string;
  latency_ms: number;
  source_count: number;
  status: 'success' | 'error';
}

export interface SecurityEvent {
  id: string;
  timestamp: string;
  query: string;
  department: string;
  role: string;
  reason: string;
  category: string;
  risk_score: number;
  action_taken: 'warn' | 'block';
}