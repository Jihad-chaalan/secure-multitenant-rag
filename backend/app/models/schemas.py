# backend/app/models/schemas.py

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# --- Request Models ---

class ChatRequest(BaseModel):
    """Request body for /api/v1/chat."""
    query: str = Field(..., description="The user's question", min_length=1)
    department: str = Field(..., description="Department name (e.g., Department_A)")
    role: str = Field(..., description="Role name (e.g., Engineering)")
    top_k: Optional[int] = Field(5, description="Number of chunks to return", ge=1, le=10)


# --- Response Models ---

class ScoreInfo(BaseModel):
    """Scores for a single source chunk."""
    vector: Optional[float] = None
    rrf: Optional[float] = None
    reranker: Optional[float] = None


class Source(BaseModel):
    """A single source document used to generate the answer."""
    chunk_id: Optional[str] = None  # <-- ADDED for traceability
    file: str
    department: str
    role: str
    text_preview: str
    scores: ScoreInfo


class ChatMetadata(BaseModel):
    """Contextual metadata about the request."""
    request_id: str  # <-- ADDED: unique ID for this request
    department: str
    role: str
    retrieved_candidates: int
    returned_chunks: int
    retriever: str
    reranker: str


class Performance(BaseModel):
    """Performance metrics for the request."""
    latency_ms: float
    retrieval_ms: float
    reranking_ms: float
    generation_ms: float


class ChatResponse(BaseModel):
    """Response body for /api/v1/chat."""
    answer: str
    sources: List[Source] = []
    metadata: ChatMetadata
    performance: Performance
    status: str = "success"