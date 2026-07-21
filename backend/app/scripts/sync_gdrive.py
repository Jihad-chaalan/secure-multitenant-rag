# backend/app/scripts/sync_gdrive.py

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.config import GDRIVE_ROOT_FOLDER_ID
from app.rag.gdrive_loader import stream_documents_from_gdrive
from app.rag.chunker import chunk_documents
from app.rag.embeddings import embed_chunks
from app.rag.vector_store import reset_collection, add_vectors
from app.rag.bm25_index import build_bm25_indexes  

def run_sync():
    """Run the full sync pipeline."""
    print("🔄 Starting Google Drive Sync...")
    reset_collection()
    
    total_docs = 0
    total_chunks = 0
    
    for doc in stream_documents_from_gdrive(GDRIVE_ROOT_FOLDER_ID):
        total_docs += 1
        chunks, _ = chunk_documents({doc["file_name"]: doc["text"]})
        embedded, _ = embed_chunks(chunks)
        count, _ = add_vectors(
            embedded,
            metadata={
                "department": doc["department"],
                "role": doc["role"]
            }
        )
        total_chunks += count
    
    build_bm25_indexes()
    print(f"✅ Sync complete: {total_docs} docs, {total_chunks} chunks")
    return total_docs, total_chunks

if __name__ == "__main__":
    run_sync()