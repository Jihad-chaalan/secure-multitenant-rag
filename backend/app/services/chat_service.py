# backend/app/services/chat_service.py

import time
import logging
from typing import Dict, Any
import uuid 
from app.models.schemas import ChatRequest, ChatResponse, Source, ScoreInfo, ChatMetadata, Performance  
from app.rag.retriever import retrieve
from app.rag.reranker import rerank
from app.rag.generator import generate_answer
from app.config import TOP_K, USE_RERANKER, RERANKER_CANDIDATE_COUNT, RERANKER_MODEL

logger = logging.getLogger(__name__)


def ask(request: ChatRequest) -> ChatResponse:
    """
    Orchestrate the full RAG pipeline:
    1. Retrieve (Hybrid Search)
    2. Rerank (Cross-Encoder)
    3. Generate (LLM)
    
    All latencies are measured for observability.
    """
    # Generate a unique request ID for tracing
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    # Step 1: Retrieve (Hybrid Search)
    retrieval_start = time.perf_counter()
    results, ret_errors = retrieve(
        query=request.query,
        department=request.department,
        role=request.role,
        top_k=request.top_k or TOP_K,
        use_hybrid=True,
        use_reranker=USE_RERANKER
    )
    retrieval_time = (time.perf_counter() - retrieval_start) * 1000  # ms

    if ret_errors:
        logger.error(f"Retrieval errors: {ret_errors}")
        # Continue with empty results

    # Step 2: Rerank (Cross-Encoder)
    reranking_start = time.perf_counter()
    reranking_time = 0.0
    reranked_results = results

    if USE_RERANKER and results:
        reranked_results = rerank(
            query=request.query,
            documents=results,
            top_k=request.top_k or TOP_K
        )
        reranking_time = (time.perf_counter() - reranking_start) * 1000  # ms
    else:
        reranked_results = results[: (request.top_k or TOP_K)]

    # Step 3: Generate Answer (LLM)
    generation_start = time.perf_counter()
    answer, context = generate_answer(request.query, reranked_results)
    generation_time = (time.perf_counter() - generation_start) * 1000  # ms

    # Step 4: Build sources list
    sources = []
    for idx, r in enumerate(reranked_results):
        metadata = r.get('metadata', {})
        
        # Generate a chunk_id (if not available, use index)
        chunk_id = metadata.get('chunk_id', f"{request_id}_{idx}")
        
        score_info = ScoreInfo(
            vector=1 - r.get('distance', 1.0) if 'distance' in r else None,
            rrf=r.get('rrf_score', None),
            reranker=r.get('reranker_score', None)
        )
        sources.append(
            Source(
                chunk_id=chunk_id,  # <-- ADDED
                file=metadata.get('source_file', 'unknown'),
                department=metadata.get('department', request.department),
                role=metadata.get('role', request.role),
                text_preview=r.get('text', '')[:300] + ('...' if len(r.get('text', '')) > 300 else ''),
                scores=score_info
            )
        )

    # Step 5: Build response
    total_latency = (time.perf_counter() - start_time) * 1000  # ms

    # Determine retriever and reranker names
    retriever_name = "Hybrid (Vector + BM25 + RRF)"
    reranker_name = RERANKER_MODEL if USE_RERANKER else "Disabled"

    return ChatResponse(
        answer=answer,
        sources=sources,
        metadata=ChatMetadata(
            request_id=request_id,  # <-- ADDED
            department=request.department,
            role=request.role,
            retrieved_candidates=RERANKER_CANDIDATE_COUNT if USE_RERANKER else (request.top_k or TOP_K),
            returned_chunks=len(reranked_results),
            retriever=retriever_name,
            reranker=reranker_name
        ),
        performance=Performance(
            latency_ms=round(total_latency, 2),
            retrieval_ms=round(retrieval_time, 2),
            reranking_ms=round(reranking_time, 2),
            generation_ms=round(generation_time, 2)
        ),
        status="success"
    )