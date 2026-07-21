# backend/app/main.py

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import GROQ_API_KEY, ALLOWED_ORIGINS
from app.rag.vector_store import get_collection
from app.rag.bm25_index import build_bm25_indexes
from app.rag.embeddings import get_embedding_status
from app.rag.reranker import get_reranker_status

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# =======================================================
# LIFECYCLE EVENTS (Startup / Shutdown)
# =======================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events with graceful degradation.
    """
    start_time = time.perf_counter()
    logger.info("🚀 Starting Secure Multi-Tenant RAG API...")

    # --- 1. Check ChromaDB ---
    chromadb_status = "disconnected"
    vector_count = 0
    try:
        collection = get_collection()
        vector_count = collection.count()
        chromadb_status = "connected"
        logger.info(f"✅ ChromaDB connected. {vector_count} vectors found.")
    except Exception as e:
        logger.error(f"❌ ChromaDB connection failed: {e}")

    # --- 2. Build BM25 indexes (graceful degradation) ---
    bm25_status = "unavailable"
    bm25_groups = 0
    if chromadb_status == "connected" and vector_count > 0:
        try:
            logger.info("🔄 Building BM25 indexes for hybrid search...")
            build_bm25_indexes()
            from app.rag.bm25_index import get_bm25_status
            bm25_status = "available"
            bm25_groups = len(get_bm25_status())
            logger.info(f"✅ BM25 indexes ready. {bm25_groups} groups built.")
        except Exception as e:
            logger.error(f"⚠️ BM25 initialization failed (continuing without it): {e}")
            bm25_status = "failed"
    else:
        logger.warning("⚠️ Skipping BM25 build (no vectors or DB down).")

    # --- 3. Check Groq API key ---
    groq_status = "available" if (GROQ_API_KEY and GROQ_API_KEY != "gsk_your-actual-api-key-here") else "unavailable"
    if groq_status == "available":
        logger.info("✅ Groq API key is configured.")
    else:
        logger.warning("⚠️ GROQ_API_KEY is not set. LLM service will not work.")

    # --- 4. Log startup summary ---
    elapsed = time.perf_counter() - start_time
    logger.info("=" * 60)
    logger.info("✅ FastAPI server is ready.")
    logger.info(f"   ChromaDB: {chromadb_status} ({vector_count} vectors)")
    logger.info(f"   BM25:     {bm25_status} ({bm25_groups} groups)")
    logger.info(f"   Groq:     {groq_status}")
    logger.info(f"   Reranker: {'loaded' if get_reranker_status() else 'lazy'}")
    logger.info(f"   Embedder: {'loaded' if get_embedding_status() else 'lazy'}")
    logger.info(f"   Startup completed in {elapsed:.2f} seconds")
    logger.info("=" * 60)

    yield  # Server runs here

    # --- SHUTDOWN ---
    logger.info("🛑 Shutting down Secure Multi-Tenant RAG API...")


# =======================================================
# FASTAPI APP
# =======================================================
app = FastAPI(
    title="Secure Multi-Tenant RAG API",
    description="Enterprise-grade RAG with data isolation, hybrid search, and cross-encoder reranking.",
    version="1.0.0",
    lifespan=lifespan,
)


# =======================================================
# MIDDLEWARE
# =======================================================

# CORS Middleware (restricted to specific origins for production safety)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,          # e.g., ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================================================
# API ROUTES (v1)
# =======================================================


from app.api.router import api_router
app.include_router(api_router, prefix="/api/v1")



# =======================================================
# ROOT ENDPOINT
# =======================================================
@app.get("/")
async def root():
    return {
        "name": "Secure Multi-Tenant RAG API",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "multi-tenancy (department/role isolation)",
            "hybrid search (BM25 + Vector)",
            "cross-encoder reranking",
            "google drive ingestion",
            "llm integration (Groq)"
        ],
        "docs": "/docs",
        "api_v1": "/api/v1"
    }




