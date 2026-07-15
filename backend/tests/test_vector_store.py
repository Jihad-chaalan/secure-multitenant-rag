# backend/tests/test_vector_store.py

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.vector_store import get_client, get_collection, add_vectors, search, reset_collection
from app.rag.embeddings import embed_text, embed_chunks
from app.rag.chunker import chunk_documents
from app.rag.loader import load_documents
from app.config import COLLECTION_NAME


# --- UNIT TESTS ---

def test_client_initialization():
    """Test that ChromaDB client initializes."""
    client = get_client()
    assert client is not None


def test_collection_creation():
    """Test that collection is created and accessible."""
    # Use a unique name for testing to avoid conflicts
    test_collection = "test_collection"
    reset_collection(test_collection)
    collection = get_collection(test_collection)
    assert collection is not None
    assert collection.name == test_collection
    reset_collection(test_collection)


def test_add_and_search():
    """Test adding vectors and searching them."""
    test_collection = "test_add_search"
    reset_collection(test_collection)
    
    # Create sample embedded chunks
    chunks = [
        {"text": "The capital of France is Paris.", "source_file": "test.txt", "chunk_index": 0},
        {"text": "The capital of Germany is Berlin.", "source_file": "test.txt", "chunk_index": 1},
    ]
    
    # Embed them
    embedded, embed_errors = embed_chunks(chunks)
    assert len(embed_errors) == 0
    
    # Add to ChromaDB
    count, add_errors = add_vectors(embedded, collection_name=test_collection)
    assert len(add_errors) == 0
    assert count == 2
    
    # Search
    query_embedding = embed_text("What is the capital of France?")
    results, search_errors = search(
        query_embedding=query_embedding,
        top_k=1,
        collection_name=test_collection
    )
    
    assert len(search_errors) == 0
    assert len(results) == 1
    assert "Paris" in results[0]["text"]
    
    # Cleanup
    reset_collection(test_collection)


def test_search_with_filters():
    """Test that metadata filters work."""
    test_collection = "test_filters"
    reset_collection(test_collection)
    
    chunks = [
        {"text": "HR Policy: 25 vacation days.", "source_file": "hr_policy.txt", "chunk_index": 0},
        {"text": "Engineering Policy: 20 vacation days.", "source_file": "eng_policy.txt", "chunk_index": 0},
    ]
    
    embedded, _ = embed_chunks(chunks)
    add_vectors(embedded, collection_name=test_collection)
    
    query_embedding = embed_text("vacation days")
    
    # Filter by source_file
    results, _ = search(
        query_embedding=query_embedding,
        top_k=5,
        filters={"source_file": "hr_policy.txt"},
        collection_name=test_collection
    )
    
    assert len(results) == 1
    assert "HR Policy" in results[0]["text"]
    assert "Engineering" not in results[0]["text"]
    
    reset_collection(test_collection)


# --- INTEGRATION TEST (uses your real data) ---

def test_full_pipeline_with_chromadb():
    """Run the full pipeline: load → chunk → embed → store → search."""
    data_folder = Path(__file__).parent.parent / "app" / "data" / "documents"
    
    if not data_folder.exists():
        pytest.skip(f"Folder not found: {data_folder}")
    
    # 1. Load
    documents, load_errors = load_documents(data_folder)
    if not documents:
        pytest.skip("No documents loaded.")
    
    # 2. Chunk
    chunks, chunk_errors = chunk_documents(documents)
    if not chunks:
        pytest.skip("No chunks created.")
    
    # 3. Embed
    embedded, embed_errors = embed_chunks(chunks)
    if not embedded:
        pytest.skip("No chunks embedded.")
    
    # 4. Store (use a test collection to avoid polluting your main one)
    test_collection = "test_full_pipeline"
    reset_collection(test_collection)
    count, store_errors = add_vectors(embedded, collection_name=test_collection)
    
    print(f"\n📊 ChromaDB Integration Test Summary:")
    print(f"   📄 Documents loaded: {len(documents)}")
    print(f"   ✂️ Chunks created: {len(chunks)}")
    print(f"   🧠 Embedded: {len(embedded)}")
    print(f"   💾 Vectors stored: {count}")
    print(f"   ❌ Load errors: {len(load_errors)}")
    print(f"   ❌ Chunk errors: {len(chunk_errors)}")
    print(f"   ❌ Embed errors: {len(embed_errors)}")
    print(f"   ❌ Store errors: {len(store_errors)}")
    
    # 5. Search
    query_embedding = embed_text("What are the vacation days?")
    results, search_errors = search(
        query_embedding=query_embedding,
        top_k=3,
        collection_name=test_collection
    )
    
    print(f"   🔍 Search results: {len(results)}")
    for r in results:
        print(f"      - {r['text'][:100]}... (Source: {r['metadata']['source_file']})")
    
    # Validate
    assert count > 0
    assert len(results) > 0
    
    # Cleanup
    reset_collection(test_collection)