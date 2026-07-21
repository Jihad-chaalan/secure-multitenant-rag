# backend/app/api/v1/health.py

from fastapi import APIRouter
from app.config import GROQ_API_KEY
from app.rag.vector_store import get_collection
from app.rag.bm25_index import get_bm25_status
from app.rag.embeddings import get_embedding_status
from app.rag.reranker import get_reranker_status

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Detailed health check endpoint for monitoring and debugging."""
    # ChromaDB status
    try:
        collection = get_collection()
        vector_count = collection.count()
        chromadb_status = "connected"
    except Exception:
        chromadb_status = "disconnected"
        vector_count = 0

    # BM25 status
    bm25_status = "unavailable"
    bm25_groups = 0
    try:
        bm25_groups = len(get_bm25_status())
        bm25_status = "available" if bm25_groups > 0 else "empty"
    except Exception:
        bm25_status = "failed"

    return {
        "status": "healthy" if chromadb_status == "connected" and GROQ_API_KEY else "degraded",
        "chromadb": {
            "status": chromadb_status,
            "vector_count": vector_count
        },
        "bm25": {
            "status": bm25_status,
            "groups": bm25_groups
        },
        "groq": "available" if (GROQ_API_KEY and GROQ_API_KEY != "gsk_your-actual-api-key-here") else "unavailable",
        "embedding_model": "loaded" if get_embedding_status() else "lazy",
        "reranker": "loaded" if get_reranker_status() else "lazy",
    }