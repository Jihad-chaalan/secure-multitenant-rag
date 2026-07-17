# backend/tests/test_retriever.py

import pytest
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.retriever import retrieve, format_results_for_prompt


# --- UNIT TESTS ---

def test_retrieve_empty_query():
    """Test retrieval with an empty query (should fail validation)."""
    results, errors = retrieve("", department="Department_A", role="Engineering")
    assert results == []
    assert len(errors) == 1
    assert errors[0]["type"] == "validation"


def test_retrieve_missing_context():
    """
    Test that retrieval fails hard if department or role is missing.
    This is a critical security test.
    """
    # Missing department
    results, errors = retrieve("What is the policy?", department="", role="Engineering")
    assert results == []
    assert len(errors) == 1
    assert errors[0]["type"] == "security"
    assert "Missing department or role" in errors[0]["error"]

    # Missing role
    results, errors = retrieve("What is the policy?", department="Department_A", role="")
    assert results == []
    assert len(errors) == 1
    assert errors[0]["type"] == "security"


@patch('app.rag.retriever.search')
def test_retrieve_with_multi_tenant_filter(mock_search):
    """Test that the retriever builds the correct hard filter."""
    mock_search.return_value = ([{"id": "1", "text": "Test", "metadata": {}, "distance": 0.1}], [])

    results, errors = retrieve(
        query="What is the API key?",
        department="Department_A",
        role="Engineering"
    )

    mock_search.assert_called_once()
    call_kwargs = mock_search.call_args[1]
    assert call_kwargs["filters"] == {"department": "Department_A", "role": "Engineering"}
    assert call_kwargs["top_k"] == 5
    assert len(errors) == 0


def test_format_results_for_prompt():
    """Test formatting search results into a prompt string."""
    mock_results = [
        {
            "text": "The capital of France is Paris.",
            "metadata": {"source_file": "france.txt", "department": "Dept_A", "role": "CEO"},
            "distance": 0.2
        },
        {
            "text": "The capital of Germany is Berlin.",
            "metadata": {"source_file": "germany.txt", "department": "Dept_A", "role": "CEO"},
            "distance": 0.3
        }
    ]

    formatted = format_results_for_prompt(mock_results)

    assert "France" in formatted
    assert "Paris" in formatted
    assert "Berlin" in formatted
    assert "france.txt" in formatted
    assert "germany.txt" in formatted
    assert "Dept_A/CEO" in formatted


def test_format_results_for_prompt_empty():
    """Test formatting an empty result list."""
    formatted = format_results_for_prompt([])
    assert formatted == "No relevant documents found."


# --- INTEGRATION TEST (Uses real ChromaDB and local data) ---

def test_retrieve_integration():
    """
    Integration test for the retriever with real data.
    Uses the local data folder to test actual retrieval with metadata.
    """
    data_folder = Path(__file__).parent.parent / "app" / "data" / "documents"
    if not data_folder.exists():
        pytest.skip("data folder not found. Skipping integration test.")

    from app.rag.loader import load_documents
    from app.rag.chunker import chunk_documents
    from app.rag.embeddings import embed_chunks
    from app.rag.vector_store import add_vectors, reset_collection

    docs, _ = load_documents(data_folder)
    if not docs:
        pytest.skip("No documents in data folder.")

    # Use the first document
    first_file = list(docs.keys())[0]
    chunks, _ = chunk_documents({first_file: docs[first_file]})
    if not chunks:
        pytest.skip("No chunks created.")

    embedded, _ = embed_chunks(chunks)

    test_collection = "test_retrieve_mt"
    reset_collection(test_collection)

    # Add vectors with multi-tenant metadata
    add_vectors(embedded, metadata={"department": "Department_A", "role": "Engineering"}, collection_name=test_collection)

    # Temporarily override the collection name for the test
    import app.rag.vector_store as vs
    original_collection = vs.COLLECTION_NAME
    try:
        vs.COLLECTION_NAME = test_collection

        results, errors = retrieve(
            query="What is the content of the document?",
            department="Department_A",
            role="Engineering"
        )

        # Verify that there are no errors from the retrieval process
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # If any results are returned, they must have the correct metadata
        for r in results:
            assert r["metadata"]["department"] == "Department_A"
            assert r["metadata"]["role"] == "Engineering"



    finally:
        vs.COLLECTION_NAME = original_collection
        reset_collection(test_collection)