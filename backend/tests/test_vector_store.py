# backend/tests/test_vector_store.py

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.vector_store import (
    get_client,
    get_collection,
    add_vectors,
    search,
    reset_collection,
)
from app.rag.embeddings import embed_text, embed_chunks
from app.rag.chunker import chunk_documents
from app.rag.loader import load_documents
from app.config import COLLECTION_NAME


# =======================================================
# 1. UNIT TESTS (Isolated logic using temporary collections)
# =======================================================

def test_client_initialization():
    """Test that ChromaDB client initializes."""
    client = get_client()
    assert client is not None


def test_collection_creation():
    """Test that collection is created and accessible."""
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

    chunks = [
        {"text": "The capital of France is Paris.", "source_file": "test.txt", "chunk_index": 0},
        {"text": "The capital of Germany is Berlin.", "source_file": "test.txt", "chunk_index": 1},
    ]

    embedded, embed_errors = embed_chunks(chunks)
    assert len(embed_errors) == 0

    count, add_errors = add_vectors(embedded, collection_name=test_collection)
    assert len(add_errors) == 0
    assert count == 2

    query_embedding = embed_text("What is the capital of France?")
    results, search_errors = search(
        query_embedding=query_embedding,
        top_k=1,
        collection_name=test_collection
    )

    assert len(search_errors) == 0
    assert len(results) == 1
    assert "Paris" in results[0]["text"]

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


# =======================================================
# 2. INTEGRATION TEST (Uses your local data folder)
# =======================================================

def test_full_pipeline_with_chromadb():
    """Run the full pipeline: load → chunk → embed → store → search."""
    data_folder = Path(__file__).parent.parent / "app" / "data" / "documents"

    if not data_folder.exists():
        pytest.skip(f"Folder not found: {data_folder}")

    documents, load_errors = load_documents(data_folder)
    if not documents:
        pytest.skip("No documents loaded.")

    chunks, chunk_errors = chunk_documents(documents)
    if not chunks:
        pytest.skip("No chunks created.")

    embedded, embed_errors = embed_chunks(chunks)
    if not embedded:
        pytest.skip("No chunks embedded.")

    test_collection = "test_full_pipeline"
    reset_collection(test_collection)
    count, store_errors = add_vectors(embedded, collection_name=test_collection)

    print(f"\n📊 ChromaDB Integration Test Summary:")
    print(f"   📄 Documents loaded: {len(documents)}")
    print(f"   ✂️ Chunks created: {len(chunks)}")
    print(f"   🧠 Embedded: {len(embedded)}")
    print(f"   💾 Vectors stored: {count}")
    print(f"   ❌ Errors: Load={len(load_errors)}, Chunk={len(chunk_errors)}, Embed={len(embed_errors)}, Store={len(store_errors)}")

    query_embedding = embed_text("What are the vacation days?")
    results, search_errors = search(
        query_embedding=query_embedding,
        top_k=3,
        collection_name=test_collection
    )

    print(f"   🔍 Search results: {len(results)}")
    for r in results:
        print(f"      - {r['text'][:100]}... (Source: {r['metadata']['source_file']})")

    assert count > 0
    assert len(results) > 0

    reset_collection(test_collection)


# =======================================================
# 3. MULTI-TENANCY TESTS (Department & Role Metadata)
# =======================================================

def test_add_vectors_with_metadata():
    """Test that metadata (department, role) is stored correctly."""
    test_collection = "test_metadata"
    reset_collection(test_collection)

    chunks = [
        {"text": "This is from Department A, Engineering.", "source_file": "test.txt", "chunk_index": 0},
        {"text": "This is from Department B, Marketing.", "source_file": "test2.txt", "chunk_index": 0},
    ]

    embedded, _ = embed_chunks(chunks)

    # Add with metadata
    add_vectors(
        embedded,
        metadata={"department": "Department_A", "role": "Engineering"},
        collection_name=test_collection
    )

    query_embedding = [0.0] * 384
    results, _ = search(
        query_embedding=query_embedding,
        top_k=5,
        collection_name=test_collection
    )

    # Check that metadata exists
    for r in results:
        assert "department" in r["metadata"]
        assert "role" in r["metadata"]
        assert r["metadata"]["department"] in ["Department_A", "Department_B"]
        assert r["metadata"]["role"] in ["Engineering", "Marketing"]

    reset_collection(test_collection)


def test_search_with_multi_tenant_filters():
    """
    Test that filtering by department and role enforces strict isolation.
    A user from Department_A should NEVER see Department_B's documents.
    """
    test_collection = "test_multi_tenant"
    reset_collection(test_collection)

    chunks = [
        {"text": "Department A - Engineering content.", "source_file": "dept_a.txt", "chunk_index": 0},
        {"text": "Department B - Marketing content.", "source_file": "dept_b.txt", "chunk_index": 0},
    ]

    embedded, _ = embed_chunks(chunks)

    # Store Dept A document with metadata
    add_vectors(
        [embedded[0]],
        metadata={"department": "Department_A", "role": "Engineering"},
        collection_name=test_collection
    )
    # Store Dept B document with metadata
    add_vectors(
        [embedded[1]],
        metadata={"department": "Department_B", "role": "Marketing"},
        collection_name=test_collection
    )

    query_embedding = [0.0] * 384

    # 1. Search as Department_A user
    results_a, _ = search(
        query_embedding=query_embedding,
        top_k=5,
        filters={"department": "Department_A"},
        collection_name=test_collection
    )

    # 2. Search as Department_B user
    results_b, _ = search(
        query_embedding=query_embedding,
        top_k=5,
        filters={"department": "Department_B"},
        collection_name=test_collection
    )

    # Assert isolation: Department_A user only sees Dept A docs
    for r in results_a:
        assert r["metadata"]["department"] == "Department_A"
    
    # Assert isolation: Department_B user only sees Dept B docs
    for r in results_b:
        assert r["metadata"]["department"] == "Department_B"

    # Specifically check that Dept A user does NOT see the Dept B document
    dept_b_found = any(r["metadata"]["department"] == "Department_B" for r in results_a)
    assert not dept_b_found, "❌ FAIL: Department_A user saw a Department_B document!"

    dept_a_found = any(r["metadata"]["department"] == "Department_A" for r in results_b)
    assert not dept_a_found, "❌ FAIL: Department_B user saw a Department_A document!"

    print("\n🔒 Multi-Tenant Isolation Test Passed:")
    print(f"   ✅ User A (Dept A) saw {len(results_a)} results.")
    print(f"   ✅ User B (Dept B) saw {len(results_b)} results.")
    print("   ✅ Zero cross-department data leakage detected.")

    reset_collection(test_collection)