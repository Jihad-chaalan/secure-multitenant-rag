# backend/app/main.py

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.config import ALLOWED_ORIGINS, GROQ_API_KEY, USE_RERANKER
from app.rag.bm25_index import build_bm25_indexes, get_bm25_status
from app.rag.embeddings import get_embedding_status, get_encoder
from app.rag.reranker import get_reranker, get_reranker_status
from app.rag.vector_store import get_collection

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
    Preloads critical models to avoid cold‑start latency on the first request.
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

    # --- 🔥 4. PRELOAD EMBEDDING MODEL (cold‑start prevention) ---
    try:
        logger.info("🔄 Preloading embedding model...")
        get_encoder()  # forces model load into memory
        logger.info("✅ Embedding model loaded.")
    except Exception as e:
        logger.error(f"⚠️ Failed to preload embedding model: {e}")

    # --- 🔥 5. PRELOAD RERANKER (if enabled) ---
    if USE_RERANKER:
        try:
            logger.info("🔄 Preloading reranker model...")
            get_reranker()
            logger.info("✅ Reranker model loaded.")
        except Exception as e:
            logger.error(f"⚠️ Failed to preload reranker: {e}")

    # --- 6. Log startup summary ---
    elapsed = time.perf_counter() - start_time
    logger.info("=" * 60)
    logger.info("✅ FastAPI server is ready.")
    logger.info(f"   ChromaDB: {chromadb_status} ({vector_count} vectors)")
    logger.info(f"   BM25:     {bm25_status} ({bm25_groups} groups)")
    logger.info(f"   Groq:     {groq_status}")
    logger.info(f"   Embedder: {'loaded' if get_embedding_status() else 'failed'}")
    logger.info(f"   Reranker: {'loaded' if get_reranker_status() else 'lazy/off'}")
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
    description="Enterprise‑grade RAG with data isolation, hybrid search, and cross‑encoder reranking.",
    version="1.0.0",
    lifespan=lifespan,
)


# =======================================================
# EXCEPTION HANDLERS
# =======================================================
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return clean JSON for validation errors (422)."""
    return JSONResponse(
        status_code=422,
        content={
            "status": "validation_error",
            "detail": exc.errors(),
            "body": exc.body if hasattr(exc, "body") else None,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Return clean JSON for HTTP errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "detail": exc.detail},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Return clean JSON for unexpected server errors (500)."""
    import traceback

    logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"status": "internal_error", "detail": "An unexpected error occurred."},
    )


# =======================================================
# MIDDLEWARE
# =======================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =======================================================
# ROUTES
# =======================================================
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
            "llm integration (Groq)",
        ],
        "docs": "/docs",
        "api_v1": "/api/v1",
    }