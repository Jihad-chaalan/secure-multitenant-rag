# backend/app/rag/embeddings.py

import logging
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL, EMBEDDING_DIM

logger = logging.getLogger(__name__)

# Singleton: Load the model once and reuse it
_encoder = None


def get_encoder() -> SentenceTransformer:
    """Get or create the sentence transformer encoder."""
    global _encoder
    if _encoder is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _encoder = SentenceTransformer(EMBEDDING_MODEL)
        logger.info(f"✅ Model loaded. Embedding dimension: {EMBEDDING_DIM}")
    return _encoder


def embed_text(text: str) -> List[float]:
    """
    Generate embedding for a single text.

    Args:
        text: The text to embed

    Returns:
        List of floats (embedding vector)
    """
    encoder = get_encoder()
    return encoder.encode(text).tolist()


def embed_chunks(chunks: List[Dict[str, str]]) -> Tuple[List[Dict], List[Dict]]:
    """
    Generate embeddings for a list of chunks.

    Args:
        chunks: List of chunk dicts with 'text', 'source_file', 'chunk_index'

    Returns:
        A tuple of (embedded_chunks, errors):
            - embedded_chunks: List of chunk dicts with added 'embedding' field
            - errors: List of error dicts with 'file', 'error', 'type'
    """
    if not chunks:
        logger.warning("No chunks provided to embed.")
        return [], []

    encoder = get_encoder()
    embedded_chunks = []
    errors = []

    # Extract all texts for batch embedding
    texts = [chunk["text"] for chunk in chunks]

    try:
        logger.info(f"🔄 Generating embeddings for {len(texts)} chunks...")
        embeddings = encoder.encode(texts, show_progress_bar=True)

        # Add embeddings to the chunks
        for chunk, embedding in zip(chunks, embeddings):
            embedded_chunks.append({
                **chunk,  # Copy all existing fields (text, source_file, chunk_index)
                "embedding": embedding.tolist()
            })

        logger.info(f"✅ Embedded {len(embedded_chunks)} chunks successfully.")

    except Exception as e:
        logger.error(f"❌ Batch embedding failed: {e}")
        errors.append({
            "file": "batch",
            "error": f"Batch embedding failed: {str(e)}",
            "type": "embedding"
        })
        # Fallback: embed one by one (slower, but recovers from partial failures)
        logger.warning("Falling back to single embedding...")
        for chunk in chunks:
            try:
                embedding = encoder.encode(chunk["text"]).tolist()
                embedded_chunks.append({
                    **chunk,
                    "embedding": embedding
                })
            except Exception as e:
                errors.append({
                    "file": chunk.get("source_file", "unknown"),
                    "error": f"Failed to embed chunk {chunk.get('chunk_index', '?')}: {str(e)}",
                    "type": "embedding"
                })
                logger.error(f"   ❌ Failed to embed chunk from {chunk.get('source_file', 'unknown')}")

    logger.info(f"✅ Total embedded: {len(embedded_chunks)}. Errors: {len(errors)}")
    return embedded_chunks, errors


def embed_query(query: str) -> List[float]:
    """
    Generate embedding for a user query (used during retrieval).

    Args:
        query: The user's question

    Returns:
        List of floats (embedding vector)
    """
    return embed_text(query)

def get_embedding_status() -> bool:
    """Return True if the embedding model is loaded, False otherwise."""
    return _encoder is not None