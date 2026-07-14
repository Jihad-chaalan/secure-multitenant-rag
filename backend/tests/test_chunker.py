# backend/tests/test_chunker.py

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.chunker import chunk_documents
from app.rag.loader import load_documents


# --- UNIT TESTS (using raw dicts) ---

def test_chunker_with_valid_text():
    """Test chunking a simple document."""
    documents = {
        "test.txt": "Hello world. This is a test document. " * 50  # Long enough to split
    }
    chunks, errors = chunk_documents(documents)

    assert len(chunks) > 0
    assert len(errors) == 0
    assert chunks[0]["source_file"] == "test.txt"
    assert "chunk_index" in chunks[0]
    assert "text" in chunks[0]


def test_chunker_with_empty_text():
    """Test chunking an empty document."""
    documents = {
        "empty.txt": ""
    }
    chunks, errors = chunk_documents(documents)

    assert len(chunks) == 0
    assert len(errors) == 1
    assert errors[0]["file"] == "empty.txt"
    assert errors[0]["type"] == "empty"


def test_chunker_with_whitespace_only():
    """Test chunking a document with only whitespace."""
    documents = {
        "whitespace.txt": "   \n\n   "
    }
    chunks, errors = chunk_documents(documents)

    assert len(chunks) == 0
    assert len(errors) == 1
    assert errors[0]["type"] == "empty"


def test_chunker_with_multiple_documents():
    """Test chunking multiple documents."""
    documents = {
        "doc1.txt": "Short text.",
        "doc2.txt": "Another short text. " * 100,  # Longer
    }
    chunks, errors = chunk_documents(documents)

    assert len(errors) == 0
    assert len(chunks) >= 1

    # Check that source files are correctly tagged
    sources = {c["source_file"] for c in chunks}
    assert "doc1.txt" in sources
    assert "doc2.txt" in sources


# --- INTEGRATION TEST (uses your real data/documents folder) ---

def test_chunker_integration():
    """Run the chunker on your actual data/documents folder."""
    data_folder = Path(__file__).parent.parent / "app" / "data" / "documents"

    if not data_folder.exists():
        pytest.skip(f"Folder not found: {data_folder}")

    # 1. Load the documents
    documents, load_errors = load_documents(data_folder)

    if not documents:
        pytest.skip("No documents loaded to chunk.")

    # 2. Chunk them
    chunks, chunk_errors = chunk_documents(documents)

    # 3. Validate
    print(f"\n📊 Chunker Integration Test Summary:")
    print(f"   📄 Documents loaded: {len(documents)}")
    print(f"   ✂️ Total chunks created: {len(chunks)}")
    print(f"   ❌ Load errors: {len(load_errors)}")
    print(f"   ❌ Chunk errors: {len(chunk_errors)}")

    # Every chunk must have the required fields
    for chunk in chunks:
        assert "text" in chunk
        assert "source_file" in chunk
        assert "chunk_index" in chunk
        assert len(chunk["text"]) > 0

    # Chunk indices should be sequential for each file
    # (optional but good validation)
    if chunks:
        for file in {c["source_file"] for c in chunks}:
            indices = [c["chunk_index"] for c in chunks if c["source_file"] == file]
            assert sorted(indices) == list(range(len(indices))), f"Indices for {file} are not sequential"