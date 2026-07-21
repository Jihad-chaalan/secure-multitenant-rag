# backend/app/rag/reranker.py

import logging
from typing import List, Dict, Any, Optional
from sentence_transformers import CrossEncoder

from app.config import RERANKER_MODEL

logger = logging.getLogger(__name__)

# Singleton pattern: Load the model once and reuse it
_reranker_model = None


def get_reranker() -> CrossEncoder:
    """Lazy-load the CrossEncoder model."""
    global _reranker_model
    if _reranker_model is None:
        logger.info(f"🔄 Loading Cross-Encoder model: {RERANKER_MODEL}")
        _reranker_model = CrossEncoder(RERANKER_MODEL)
        logger.info("✅ Cross-Encoder model loaded.")
    return _reranker_model


def rerank(
    query: str,
    documents: List[Dict[str, Any]],
    top_k: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Re-rank documents using a Cross-Encoder.

    Args:
        query: The user's question
        documents: List of dicts with 'text' and 'metadata'
        top_k: Number of top documents to return (default: uses config)

    Returns:
        The documents sorted by Cross-Encoder relevance score (highest first).
    """
    if not documents:
        return []

    # If only one document, skip the model (optimization)
    if len(documents) == 1:
        return documents

    # Import config here to avoid circular imports
    from app.config import RERANKER_TOP_K
    
    top_k = top_k or RERANKER_TOP_K
    model = get_reranker()

    # Prepare pairs for the Cross-Encoder: (query, passage_text)
    pairs = [(query, doc["text"]) for doc in documents]

    try:
        # Batch inference: scores are floats (higher = more relevant)
        scores = model.predict(pairs)
    except Exception as e:
        logger.error(f"Cross-Encoder inference failed: {e}")
        # Fallback: return original order
        return documents[:top_k]

    # Attach scores to documents
    for doc, score in zip(documents, scores):
        doc["reranker_score"] = float(score)

    # Sort by score descending (highest relevance first)
    documents.sort(key=lambda x: x["reranker_score"], reverse=True)

    # Log the top scores (for debugging)
    logger.info(f"✅ Reranking complete. Top score: {documents[0]['reranker_score']:.4f}")

    return documents[:top_k]


# backend/app/rag/reranker.py

def get_reranker_status() -> bool:
    """Return True if the reranker model is loaded, False otherwise."""
    return _reranker_model is not None