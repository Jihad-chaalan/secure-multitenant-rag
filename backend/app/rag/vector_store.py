# backend/app/rag/vector_store.py

import logging
import uuid
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path

import chromadb
from chromadb.config import Settings
from chromadb.errors import NotFoundError  # <-- IMPORTANT
from app.config import COLLECTION_NAME

logger = logging.getLogger(__name__)

# Persistent storage path (inside the backend folder)
CHROMA_PATH = Path(__file__).parent.parent.parent / "chroma_db"

# Singleton client
_client = None


def get_client() -> chromadb.PersistentClient:
    """Get or create the persistent ChromaDB client."""
    global _client
    if _client is None:
        logger.info(f"📁 Initializing ChromaDB at: {CHROMA_PATH}")
        _client = chromadb.PersistentClient(
            path=str(CHROMA_PATH),
            settings=Settings(anonymized_telemetry=False)
        )
        logger.info("✅ ChromaDB client ready.")
    return _client


def get_collection(collection_name: str = COLLECTION_NAME):
    """
    Get or create a collection.
    ChromaDB automatically creates it if it doesn't exist.
    """
    client = get_client()
    
    try:
        # Try to get existing collection
        collection = client.get_collection(collection_name)
        logger.info(f"📂 Using existing collection: {collection_name}")
    except (ValueError, NotFoundError):
        # Collection doesn't exist, create it
        collection = client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"✅ Created new collection: {collection_name}")
    
    return collection


def reset_collection(collection_name: str = COLLECTION_NAME):
    """
    Delete and recreate a collection (useful for testing).
    """
    client = get_client()
    try:
        client.delete_collection(collection_name)
        logger.info(f"🗑️ Deleted collection: {collection_name}")
    except (ValueError, NotFoundError):
        # Collection didn't exist, that's fine
        logger.info(f"ℹ️ Collection '{collection_name}' did not exist, skipping delete.")
    
    # Recreate it
    get_collection(collection_name)


def add_vectors(
    embedded_chunks: List[Dict[str, Any]],
    collection_name: str = COLLECTION_NAME
) -> Tuple[int, List[Dict[str, str]]]:
    """
    Add embedded chunks to ChromaDB.
    """
    if not embedded_chunks:
        logger.warning("No embedded chunks to add.")
        return 0, []

    collection = get_collection(collection_name)
    errors = []

    ids = []
    embeddings = []
    metadatas = []
    documents = []

    for chunk in embedded_chunks:
        try:
            chunk_id = f"{chunk['source_file']}_{chunk['chunk_index']}_{uuid.uuid4().hex[:8]}"
            
            ids.append(chunk_id)
            embeddings.append(chunk["embedding"])
            documents.append(chunk["text"])
            
            metadatas.append({
                "source_file": chunk["source_file"],
                "chunk_index": chunk["chunk_index"],
            })
            
        except KeyError as e:
            errors.append({
                "file": chunk.get("source_file", "unknown"),
                "error": f"Missing required field: {e}",
                "type": "validation"
            })

    if not ids:
        return 0, errors

    try:
        collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )
        logger.info(f"✅ Added {len(ids)} vectors to '{collection_name}'.")
    except Exception as e:
        logger.error(f"❌ Failed to add vectors: {e}")
        errors.append({
            "file": "batch",
            "error": f"ChromaDB batch add failed: {str(e)}",
            "type": "storage"
        })
        return 0, errors

    return len(ids), errors


def search(
    query_embedding: List[float],
    top_k: int = 5,
    filters: Optional[Dict[str, Any]] = None,
    collection_name: str = COLLECTION_NAME
) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """
    Search for similar vectors in ChromaDB.
    """
    collection = get_collection(collection_name)
    errors = []
    
    try:
        where_clause = None
        if filters:
            where_clause = filters
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause,
            include=["documents", "metadatas", "distances"]
        )
        
        formatted_results = []
        if results and results['ids'] and results['ids'][0]:
            for idx in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][idx],
                    "text": results['documents'][0][idx],
                    "metadata": results['metadatas'][0][idx],
                    "distance": results['distances'][0][idx]
                })
        
        logger.info(f"🔍 Found {len(formatted_results)} results.")
        return formatted_results, errors
        
    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        errors.append({
            "file": "search",
            "error": f"Search failed: {str(e)}",
            "type": "retrieval"
        })
        return [], errors