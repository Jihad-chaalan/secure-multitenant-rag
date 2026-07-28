# backend/app/api/v1/health.py

from datetime import datetime
from fastapi import APIRouter
from app.config import GROQ_API_KEY, COLLECTION_NAME
from app.rag.vector_store import get_client  # ✅ Use get_client
from app.rag.bm25_index import get_bm25_status
from app.rag.embeddings import get_embedding_status
from app.rag.reranker import get_reranker_status
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Detailed health check endpoint for monitoring and debugging."""
    
    # 🔥 Initialize with default values
    chromadb_status = "disconnected"
    vector_count = 0
    
    # --- Qdrant status (use get_client) ---
    try:
        client = get_client()
        result = client.count(collection_name=COLLECTION_NAME)
        vector_count = result.count
        chromadb_status = "connected"  # ✅ Set to connected on success
        logger.info(f"✅ Qdrant connected with {vector_count} vectors")
    except Exception as e:
        chromadb_status = "disconnected"
        vector_count = 0
        logger.error(f"❌ Qdrant health check failed: {e}")

    # --- BM25 status ---
    bm25_status = "unavailable"
    bm25_groups = 0
    try:
        bm25_groups = len(get_bm25_status())
        bm25_status = "available" if bm25_groups > 0 else "empty"
    except Exception:
        bm25_status = "failed"

    # --- Groq status ---
    groq_status = "available" if (GROQ_API_KEY and GROQ_API_KEY != "gsk_your-actual-api-key-here") else "unavailable"

    # --- Overall status ---
    overall_status = "healthy" if chromadb_status == "connected" and groq_status == "available" else "degraded"

    return {
        "status": overall_status,
        "chromadb": {
            "status": chromadb_status,
            "vector_count": vector_count
        },
        "bm25": {
            "status": bm25_status,
            "groups": bm25_groups
        },
        "groq": groq_status,
        "embedding_model": "loaded" if get_embedding_status() else "lazy",
        "reranker": "loaded" if get_reranker_status() else "lazy",
    }


@router.get("/heartbeat")
async def heartbeat():
    """Lightweight liveness check for Docker/Kubernetes."""
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }