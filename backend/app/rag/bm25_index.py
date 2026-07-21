# backend/app/rag/bm25_index.py

import logging
from typing import Dict, List, Tuple, Any
from rank_bm25 import BM25Okapi

from app.rag.vector_store import get_collection
from app.config import COLLECTION_NAME

logger = logging.getLogger(__name__)

# Cache: stores BM25 indexes for each department/role combination
_bm25_indexes: Dict[str, BM25Okapi] = {}
_bm25_corpus: Dict[str, List[Dict[str, Any]]] = {}


def build_bm25_indexes(collection_name: str = COLLECTION_NAME):
    """
    Fetch all documents from ChromaDB, group by (department, role),
    and build a BM25 index for each group.
    """
    global _bm25_indexes, _bm25_corpus
    
    logger.info("🔄 Building BM25 indexes from ChromaDB...")
    
    collection = get_collection(collection_name)
    
    # Fetch all documents with their metadata
    try:
        all_data = collection.get(include=["documents", "metadatas"])
    except Exception as e:
        logger.error(f"Failed to fetch documents from ChromaDB: {e}")
        return
    
    if not all_data or not all_data['documents']:
        logger.warning("No documents found in ChromaDB. BM25 indexes will be empty.")
        return
    
    # Group by (department, role)
    grouped: Dict[str, Tuple[List[str], List[Dict]]] = {}
    
    for doc, meta in zip(all_data['documents'], all_data['metadatas']):
        dept = meta.get('department', 'Unknown')
        role = meta.get('role', 'Unknown')
        key = f"{dept}_{role}"
        
        if key not in grouped:
            grouped[key] = ([], [])
        
        grouped[key][0].append(doc)      # The text
        grouped[key][1].append(meta)     # The metadata (source_file, etc.)
    
    # Build BM25 index for each group
    for key, (texts, metadatas) in grouped.items():
        if not texts:
            continue
        
        # Tokenize: split on whitespace for simplicity
        tokenized_texts = [text.split() for text in texts]
        
        # Build BM25 index
        bm25 = BM25Okapi(tokenized_texts)
        
        # Store in cache
        _bm25_indexes[key] = bm25
        _bm25_corpus[key] = [
            {"text": texts[i], "metadata": metadatas[i]} 
            for i in range(len(texts))
        ]
        
        logger.info(f"✅ BM25 index built for {key} ({len(texts)} documents)")
    
    logger.info(f"✅ BM25 indexes built for {len(_bm25_indexes)} department/role groups.")


def search_bm25(
    query: str,
    department: str,
    role: str,
    top_k: int = 20
) -> List[Dict[str, Any]]:
    """
    Search using BM25 for a specific department and role.
    
    Returns a list of dicts with 'text', 'metadata', and 'bm25_score'.
    """
    if not _bm25_indexes:
        logger.warning("BM25 indexes are empty. Run build_bm25_indexes() first.")
        return []
    
    key = f"{department}_{role}"
    
    if key not in _bm25_indexes:
        logger.info(f"No BM25 index found for {key}. Returning empty results.")
        return []
    
    bm25 = _bm25_indexes[key]
    corpus = _bm25_corpus[key]
    
    # Tokenize the query
    tokenized_query = query.split()
    
    # Get BM25 scores
    scores = bm25.get_scores(tokenized_query)
    
    # Pair scores with corpus and sort
    results = []
    for i, score in enumerate(scores):
        results.append({
            "text": corpus[i]["text"],
            "metadata": corpus[i]["metadata"],
            "bm25_score": score,
        })
    
    # Sort by score descending and take top_k
    results.sort(key=lambda x: x["bm25_score"], reverse=True)
    return results[:top_k]


def get_bm25_status() -> Dict[str, int]:
    """Return a summary of the BM25 indexes."""
    return {
        key: len(_bm25_corpus.get(key, []))
        for key in _bm25_indexes.keys()
    }

