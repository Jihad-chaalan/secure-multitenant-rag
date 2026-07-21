# backend/app/rag/retriever.py

import logging
from typing import List, Dict, Tuple, Optional, Any

from app.rag.embeddings import embed_query
from app.rag.vector_store import search
from app.rag.bm25_index import search_bm25
from app.rag.reranker import rerank  # <-- NEW IMPORT
from app.config import TOP_K, USE_RERANKER, RERANKER_CANDIDATE_COUNT  # <-- NEW CONFIGS

logger = logging.getLogger(__name__)


def reciprocal_rank_fusion(
    vector_results: List[Dict[str, Any]],
    bm25_results: List[Dict[str, Any]],
    k: int = 60
) -> List[Dict[str, Any]]:
    """
    Merge two ranked lists using Reciprocal Rank Fusion (RRF).
    
    Args:
        vector_results: Results from vector search with a 'rank' field (or we compute it).
        bm25_results: Results from BM25 search.
        k: RRF constant (usually 60).
    
    Returns:
        A single ranked list of results (top 5).
    """
    # Build a dictionary to accumulate RRF scores
    fusion_dict: Dict[str, Dict[str, Any]] = {}
    
    # 1. Process vector results
    for rank, item in enumerate(vector_results, start=1):
        # Use a unique key (source_file + chunk_index + first 50 chars of text)
        # We need a reliable identifier. The metadata usually has source_file and chunk_index.
        file_name = item.get('metadata', {}).get('source_file', 'unknown')
        chunk_idx = item.get('metadata', {}).get('chunk_index', 0)
        doc_id = f"{file_name}_{chunk_idx}"
        
        rrf_score = 1 / (k + rank)
        
        # If this document already exists (from BM25), add the score
        if doc_id in fusion_dict:
            fusion_dict[doc_id]['rrf_score'] += rrf_score
            fusion_dict[doc_id]['vector_rank'] = rank
        else:
            fusion_dict[doc_id] = {
                "text": item.get('text', ''),
                "metadata": item.get('metadata', {}),
                "distance": item.get('distance', 1.0),
                "rrf_score": rrf_score,
                "vector_rank": rank,
                "bm25_rank": None,
            }
    
    # 2. Process BM25 results
    for rank, item in enumerate(bm25_results, start=1):
        file_name = item.get('metadata', {}).get('source_file', 'unknown')
        chunk_idx = item.get('metadata', {}).get('chunk_index', 0)
        doc_id = f"{file_name}_{chunk_idx}"
        
        rrf_score = 1 / (k + rank)
        
        if doc_id in fusion_dict:
            fusion_dict[doc_id]['rrf_score'] += rrf_score
            fusion_dict[doc_id]['bm25_rank'] = rank
            # If vector search didn't find it, we still have the text from BM25
            if not fusion_dict[doc_id]['text']:
                fusion_dict[doc_id]['text'] = item.get('text', '')
                fusion_dict[doc_id]['metadata'] = item.get('metadata', {})
        else:
            fusion_dict[doc_id] = {
                "text": item.get('text', ''),
                "metadata": item.get('metadata', {}),
                "bm25_score": item.get('bm25_score', 0.0),
                "rrf_score": rrf_score,
                "vector_rank": None,
                "bm25_rank": rank,
            }
    
    # 3. Convert to list and sort by RRF score
    results = list(fusion_dict.values())
    results.sort(key=lambda x: x['rrf_score'], reverse=True)
    
    return results


def retrieve(
    query: str,
    department: str,
    role: str,
    top_k: int = TOP_K,
    use_hybrid: bool = True,
    use_reranker: bool = USE_RERANKER  # <-- NEW PARAMETER (default from config)
) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """
    Retrieve relevant chunks with optional hybrid (Vector + BM25) search and Cross-Encoder Reranker.
    """
    if not query or not query.strip():
        return [], [{"file": "query", "error": "Query is empty", "type": "validation"}]

    if not department or not role:
        return [], [{
            "file": "security",
            "error": "Missing department or role. Multi-tenant context required.",
            "type": "security"
        }]

    try:
        # 1. Embed the query
        logger.info("🔄 Embedding query...")
        query_embedding = embed_query(query)

        # 2. Build the hard filter
        filters = {"department": department, "role": role}
        logger.info(f"🔍 Searching for '{query[:50]}...'")
        logger.info(f"   🔒 Filtering by: department={department}, role={role}")

        # 3. Determine how many candidates to fetch
        # If reranker is enabled, fetch more candidates to rerank.
        candidate_count = RERANKER_CANDIDATE_COUNT if use_reranker else top_k
        logger.info(f"   📊 Fetching {candidate_count} candidates for {'reranking' if use_reranker else 'final results'}.")

        # 4. Vector Search (always run)
        vector_results, search_errors = search(
            query_embedding=query_embedding,
            top_k=candidate_count,
            filters=filters
        )

        if search_errors:
            return [], search_errors

        # 5. BM25 Search (if hybrid is enabled)
        if use_hybrid:
            logger.info("   🔍 Running BM25 search...")
            bm25_results = search_bm25(query, department, role, top_k=candidate_count)
            
            # 6. Fuse results using RRF
            logger.info("   🔄 Fusing results with RRF...")
            fused_results = reciprocal_rank_fusion(vector_results, bm25_results)
            candidates = fused_results[:candidate_count]
        else:
            candidates = vector_results[:candidate_count]

        # 7. 🔥 CROSS-ENCODER RERANKER (NEW)
        if use_reranker and candidates:
            logger.info(f"   🔁 Running Cross-Encoder Reranker on {len(candidates)} candidates...")
            reranked_results = rerank(query, candidates, top_k=top_k)
            final_results = reranked_results
        else:
            final_results = candidates[:top_k]

        # 8. Format the final results
        formatted_results = []
        for item in final_results:
            result_entry = {
                "id": f"{item['metadata'].get('source_file', 'unknown')}_{item['metadata'].get('chunk_index', 0)}",
                "text": item['text'],
                "metadata": item['metadata'],
                "distance": item.get('distance', 0.0),
                "rrf_score": item.get('rrf_score', 0.0),
            }
            # Include reranker score if available
            if 'reranker_score' in item:
                result_entry["reranker_score"] = item['reranker_score']
            formatted_results.append(result_entry)
        
        # Log the retrieval method used
        if use_reranker:
            logger.info(f"✅ Reranked search found {len(formatted_results)} results.")
        elif use_hybrid:
            logger.info(f"✅ Hybrid search found {len(formatted_results)} results.")
        else:
            logger.info(f"✅ Vector search found {len(formatted_results)} results.")
            
        return formatted_results, []

    except Exception as e:
        logger.error(f"❌ Retrieval failed: {e}")
        return [], [{
            "file": "retrieval",
            "error": f"Retrieval failed: {str(e)}",
            "type": "retrieval"
        }]


def format_results_for_prompt(results: List[Dict[str, Any]]) -> str:
    """Format results for the LLM prompt."""
    if not results:
        return "No relevant documents found."

    formatted_chunks = []
    for i, r in enumerate(results, 1):
        source = r.get('metadata', {}).get('source_file', 'unknown')
        dept = r.get('metadata', {}).get('department', 'unknown')
        role_src = r.get('metadata', {}).get('role', 'unknown')
        text = r.get('text', '').strip()
        
        # Build score information
        score_info = []
        if 'reranker_score' in r:
            score_info.append(f"Reranker: {r['reranker_score']:.4f}")
        if 'rrf_score' in r:
            score_info.append(f"Fusion: {r['rrf_score']:.4f}")
        if 'distance' in r and 'reranker_score' not in r:
            score_info.append(f"Relevancy: {1 - r['distance']:.2%}")
        
        score_str = f" | {', '.join(score_info)}" if score_info else ""
        
        formatted_chunks.append(f"[Source {i}: {source} ({dept}/{role_src}){score_str}]\n{text}")

    return "\n\n---\n\n".join(formatted_chunks)