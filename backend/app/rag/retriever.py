# backend/app/rag/retriever.py

import logging
from typing import List, Dict, Tuple, Optional, Any

from app.rag.embeddings import embed_query
from app.rag.vector_store import search
from app.config import TOP_K

logger = logging.getLogger(__name__)


def retrieve(
    query: str,
    department: str,     
    role: str,           
    top_k: int = TOP_K
) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """
    Retrieve relevant chunks from the vector database with multi-tenant filtering.

    Args:
        query: The user's question
        department: Department name (e.g., "Department_A")
        role: Role name (e.g., "Engineering")
        top_k: Number of results to return

    Returns:
        A tuple of (results, errors):
            - results: List of dicts with keys: id, text, metadata, distance
            - errors: List of error dicts
    """
    if not query or not query.strip():
        logger.warning("Empty query provided to retriever.")
        return [], [{
            "file": "query",
            "error": "Query is empty",
            "type": "validation"
        }]

    # --- HARD SECURITY CHECK ---
    # Enforce that department and role are provided
    if not department or not role:
        logger.error(f"Missing multi-tenant context. Department: {department}, Role: {role}")
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
        # This is the crucial security boundary!
        filters = {
            "department": department,
            "role": role
        }

        logger.info(f"🔍 Searching for '{query[:50]}...' (top_k={top_k})")
        logger.info(f"   🔒 Filtering by: department={department}, role={role}")

        # 3. Search with the hard filter
        results, search_errors = search(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters
        )

        # 4. Log a summary
        if results:
            logger.info(f"✅ Found {len(results)} relevant chunks for {department}/{role}.")
            for i, r in enumerate(results):
                logger.debug(f"   [{i+1}] {r['metadata'].get('source_file', 'unknown')} - Distance: {r['distance']:.4f}")
        else:
            logger.info(f"ℹ️ No relevant chunks found for {department}/{role}.")

        return results, search_errors

    except Exception as e:
        logger.error(f"❌ Retrieval failed: {e}")
        return [], [{
            "file": "retrieval",
            "error": f"Retrieval failed: {str(e)}",
            "type": "retrieval"
        }]


def format_results_for_prompt(results: List[Dict[str, Any]]) -> str:
    """
    Format retrieved results into a clean string for the LLM prompt.

    Args:
        results: List of search results from retrieve()

    Returns:
        A formatted string with sources and text
    """
    if not results:
        return "No relevant documents found."

    formatted_chunks = []
    for i, r in enumerate(results, 1):
        source = r['metadata'].get('source_file', 'unknown')
        dept = r['metadata'].get('department', 'unknown')
        role = r['metadata'].get('role', 'unknown')
        text = r['text'].strip()
        formatted_chunks.append(f"[Source {i}: {source} | {dept}/{role}]\n{text}")

    return "\n\n---\n\n".join(formatted_chunks)