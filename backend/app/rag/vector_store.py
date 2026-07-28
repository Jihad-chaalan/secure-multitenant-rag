# backend/app/rag/vector_store.py

import logging
import uuid
from typing import List, Dict, Tuple, Optional, Any

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse

from app.config import COLLECTION_NAME, QDRANT_URL, QDRANT_API_KEY, EMBEDDING_DIM

logger = logging.getLogger(__name__)

# Singleton client
_client = None


def get_client() -> QdrantClient:
    """Get or create the Qdrant client."""
    global _client
    if _client is None:
        if not QDRANT_URL or not QDRANT_API_KEY:
            raise ValueError(
                "QDRANT_URL and QDRANT_API_KEY must be set in environment variables. "
                "Please add them to your .env file."
            )
        logger.info(f"📁 Initializing Qdrant client at: {QDRANT_URL}")
        _client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
            timeout=60,
        )
        logger.info("✅ Qdrant client ready.")
    return _client


def create_payload_indexes(collection_name: str = COLLECTION_NAME):
    """
    Create payload indexes for filtering fields.
    This is required for efficient filtering on metadata fields.
    """
    client = get_client()
    index_created = False
    
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="department",
            field_type="keyword",
        )
        logger.info("✅ Created payload index for 'department'")
        index_created = True
    except Exception as e:
        if "already exists" in str(e).lower():
            logger.info("ℹ️ Index 'department' already exists")
        else:
            logger.warning(f"⚠️ Could not create index for 'department': {e}")
    
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="role",
            field_type="keyword",
        )
        logger.info("✅ Created payload index for 'role'")
        index_created = True
    except Exception as e:
        if "already exists" in str(e).lower():
            logger.info("ℹ️ Index 'role' already exists")
        else:
            logger.warning(f"⚠️ Could not create index for 'role': {e}")
    
    try:
        client.create_payload_index(
            collection_name=collection_name,
            field_name="source_file",
            field_type="keyword",
        )
        logger.info("✅ Created payload index for 'source_file'")
        index_created = True
    except Exception as e:
        if "already exists" in str(e).lower():
            logger.info("ℹ️ Index 'source_file' already exists")
        else:
            logger.warning(f"⚠️ Could not create index for 'source_file': {e}")
    
    if not index_created:
        logger.info("ℹ️ No new indexes were created (they may already exist).")
    
    return index_created


def get_collection(collection_name: str = COLLECTION_NAME):
    """
    Get or create a collection.
    """
    client = get_client()
    
    try:
        client.get_collection(collection_name)
        logger.info(f"📂 Using existing collection: {collection_name}")
    except UnexpectedResponse:
        # Collection doesn't exist, create it
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=EMBEDDING_DIM,
                distance=models.Distance.COSINE,
            ),
        )
        logger.info(f"✅ Created new collection: {collection_name}")
        
        # 🔥 Create payload indexes for filtering
        create_payload_indexes(collection_name)
    
    return client


def reset_collection(collection_name: str = COLLECTION_NAME):
    """
    Delete and recreate a collection (useful for testing).
    """
    client = get_client()
    try:
        client.delete_collection(collection_name)
        logger.info(f"🗑️ Deleted collection: {collection_name}")
    except UnexpectedResponse:
        logger.info(f"ℹ️ Collection '{collection_name}' did not exist, skipping delete.")
    
    # Recreate it
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=EMBEDDING_DIM,
            distance=models.Distance.COSINE,
        ),
    )
    logger.info(f"✅ Recreated collection: {collection_name}")
    
    # 🔥 Always recreate payload indexes
    create_payload_indexes(collection_name)


def add_vectors(
    embedded_chunks: List[Dict[str, Any]],
    metadata: Optional[Dict[str, str]] = None,
    collection_name: str = COLLECTION_NAME
) -> Tuple[int, List[Dict[str, str]]]:
    """
    Add embedded chunks to Qdrant with optional metadata.
    """
    if not embedded_chunks:
        logger.warning("No embedded chunks to add.")
        return 0, []

    client = get_client()
    errors = []
    points = []

    for chunk in embedded_chunks:
        try:
            # Generate a UUID for the point
            chunk_id = str(uuid.uuid4())
            
            # Build payload (metadata)
            payload = {
                "text": chunk["text"],
                "source_file": chunk["source_file"],
                "chunk_index": chunk["chunk_index"],
            }
            
            # Add department and role if provided
            if metadata:
                if "department" in metadata:
                    payload["department"] = metadata["department"]
                if "role" in metadata:
                    payload["role"] = metadata["role"]
            
            points.append(
                models.PointStruct(
                    id=chunk_id,
                    vector=chunk["embedding"],
                    payload=payload,
                )
            )
            
        except KeyError as e:
            errors.append({
                "file": chunk.get("source_file", "unknown"),
                "error": f"Missing required field: {e}",
                "type": "validation"
            })

    if not points:
        return 0, errors

    try:
        # Upsert points to Qdrant
        client.upsert(
            collection_name=collection_name,
            points=points,
        )
        logger.info(f"✅ Added {len(points)} vectors to '{collection_name}'.")
        
        if metadata:
            logger.info(f"   🏷️ Metadata: department={metadata.get('department', 'N/A')}, role={metadata.get('role', 'N/A')}")
        
    except Exception as e:
        logger.error(f"❌ Failed to add vectors: {e}")
        errors.append({
            "file": "batch",
            "error": f"Qdrant batch add failed: {str(e)}",
            "type": "storage"
        })
        return 0, errors

    return len(points), errors


def search(
    query_embedding: List[float],
    top_k: int = 5,
    filters: Optional[Dict[str, Any]] = None,
    collection_name: str = COLLECTION_NAME
) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """
    Search for similar vectors in Qdrant.
    """
    client = get_client()
    errors = []
    
    try:
        # Build filter if provided
        filter_condition = None
        if filters:
            must_conditions = []
            for key, value in filters.items():
                must_conditions.append(
                    models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value),
                    )
                )
            filter_condition = models.Filter(
                must=must_conditions,
            )
        
        # Use query_points() for qdrant-client 1.18.0
        search_result = client.query_points(
            collection_name=collection_name,
            query=query_embedding,
            query_filter=filter_condition,
            limit=top_k,
            with_payload=True,
        )
        
        # Format results
        formatted_results = []
        for hit in search_result.points:
            formatted_results.append({
                "id": hit.id,
                "text": hit.payload.get("text", ""),
                "metadata": {
                    "source_file": hit.payload.get("source_file", "unknown"),
                    "chunk_index": hit.payload.get("chunk_index", 0),
                    "department": hit.payload.get("department", "unknown"),
                    "role": hit.payload.get("role", "unknown"),
                },
                "distance": hit.score,
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