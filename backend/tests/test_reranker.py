# backend/tests/test_reranker.py

import sys
from pathlib import Path

# Add the parent directory (backend/) to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from app.rag.reranker import rerank, get_reranker


# --- Correct Mock ---
# The CrossEncoder.predict() method expects exactly two arguments: (self, pairs)
# where pairs is a list of (query, text) tuples.
def mock_crossencoder_predict(pairs):
    """
    A deterministic scoring function for testing.
    Returns a score based on the length of the document text.
    This mimics a real CrossEncoder without downloading the model.
    """
    return [len(pair[1]) / 100 for pair in pairs]


# --- Unit Test: Basic sorting ---
def test_reranker_basic(monkeypatch):
    """Test that reranker correctly orders documents by score."""

    # Mock the entire get_reranker function to return a fake model
    # that uses our deterministic scoring function.
    class MockCrossEncoder:
        def predict(self, pairs):
            return mock_crossencoder_predict(pairs)

    monkeypatch.setattr("app.rag.reranker.get_reranker", lambda: MockCrossEncoder())

    documents = [
        {"text": "short text", "metadata": {"id": 1}},
        {"text": "This is a very long document that should get a higher score", "metadata": {"id": 2}},
    ]
    query = "test"
    reranked = rerank(query, documents, top_k=2)

    # The longer document should get a higher score and be ranked first
    assert reranked[0]["metadata"]["id"] == 2
    assert reranked[1]["metadata"]["id"] == 1
    # Scores should be attached
    assert "reranker_score" in reranked[0]
    assert "reranker_score" in reranked[1]


# --- Unit Test: Empty input ---
def test_reranker_skips_empty():
    """Test that reranker handles empty lists gracefully."""
    results = rerank("test", [])
    assert results == []


# --- Unit Test: Metadata preservation and scoring for multiple docs ---
def test_reranker_preserves_metadata(monkeypatch):
    """Test that metadata is preserved and scores are added when multiple docs exist."""

    class MockCrossEncoder:
        def predict(self, pairs):
            # Simple deterministic score: longer text = higher score
            return [len(pair[1]) / 100 for pair in pairs]

    monkeypatch.setattr("app.rag.reranker.get_reranker", lambda: MockCrossEncoder())

    docs = [
        {"text": "First document", "metadata": {"source_file": "doc1.txt"}},
        {"text": "Second longer document", "metadata": {"source_file": "doc2.txt"}},
    ]
    reranked = rerank("test", docs, top_k=2)

    # Metadata preserved
    assert reranked[0]["metadata"]["source_file"] == "doc2.txt"
    assert reranked[1]["metadata"]["source_file"] == "doc1.txt"
    # Scores attached
    assert "reranker_score" in reranked[0]
    assert "reranker_score" in reranked[1]