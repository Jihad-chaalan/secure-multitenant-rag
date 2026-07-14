# backend/tests/test_embeddings.py

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.embeddings import embed_text, embed_chunks, get_encoder
from app.rag.chunker import chunk_documents
from app.rag.loader import load_documents


# --- UNIT TESTS ---

def test_embed_text_returns_vector():
    """Test that embedding a text returns a list of floats."""
    vector = embed_text("Hello world")
    assert isinstance(vector, list)
    assert len(vector) > 0
    assert isinstance(vector[0], float)


def test_embed_text_consistent():
    """Test that the same text produces the same embedding."""
    text = "This is a test."
    v1 = embed_text(text)
    v2 = embed_text(text)
    assert v1 == v2


def test_embed_chunks_valid():
    """Test embedding a list of chunks."""
    chunks = [
        {"text": "First chunk", "source_file": "test.txt", "chunk_index": 0},
        {"text": "Second chunk", "source_file": "test.txt", "chunk_index": 1},
    ]
    embedded, errors = embed_chunks(chunks)

    assert len(errors) == 0
    assert len(embedded) == 2
    assert "embedding" in embedded[0]
    assert len(embedded[0]["embedding"]) > 0
    # Check that original fields are preserved
    assert embedded[0]["source_file"] == "test.txt"
    assert embedded[0]["chunk_index"] == 0


def test_embed_chunks_empty():
    """Test embedding an empty list."""
    embedded, errors = embed_chunks([])
    assert embedded == []
    assert errors == []


# --- INTEGRATION TEST (uses your real data) ---

def test_embedding_integration():
    """Run the full pipeline: load → chunk → embed on your real data."""
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

    print(f"\n📊 Embedding Integration Test Summary:")
    print(f"   📄 Documents loaded: {len(documents)}")
    print(f"   ✂️ Chunks created: {len(chunks)}")
    print(f"   🧠 Embedded: {len(embedded)}")
    print(f"   ❌ Load errors: {len(load_errors)}")
    print(f"   ❌ Chunk errors: {len(chunk_errors)}")
    print(f"   ❌ Embed errors: {len(embed_errors)}")

    # Validate
    assert len(embedded) > 0, "No chunks were embedded"
    for item in embedded:
        assert "embedding" in item
        assert len(item["embedding"]) == 384  # all-MiniLM-L6-v2 dimension
        assert "text" in item
        assert "source_file" in item
        assert "chunk_index" in item