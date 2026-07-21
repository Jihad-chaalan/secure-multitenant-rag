# backend/tests/test_reranker.py

import pytest
from app.rag.reranker import rerank, get_reranker

# --- Mock the CrossEncoder for Unit Tests ---
def mock_crossencoder_predict(pairs):
    # Simulate scoring: return scores based on the length of the text (for testing)
    return [len(pair[1]) / 100 for pair in pairs]


def test_reranker_basic(monkeypatch):
    """Test that reranker sorts documents by score."""

    # Mock the model to avoid downloading it during unit tests
    monkeypatch.setattr("app.rag.reranker.get_reranker", lambda: type('Mock', (), {'predict': mock_crossencoder_predict})())

    documents = [
        {"text": "short text", "metadata": {"id": 1}},
        {"text": "This is a very long document that should get a higher score", "metadata": {"id": 2}},
    ]
    query = "test"
    reranked = rerank(query, documents, top_k=2)

    # The longer document should score higher
    assert reranked[0]["metadata"]["id"] == 2
    assert reranked[1]["metadata"]["id"] == 1


def test_reranker_skips_empty():
    """Test that reranker handles empty lists gracefully."""
    results = rerank("test", [])
    assert results == []


def test_reranker_preserves_metadata():
    """Test that metadata is preserved during reranking."""
    docs = [
        {"text": "Hello world", "metadata": {"source_file": "test.txt"}},
    ]
    reranked = rerank("test", docs)
    assert reranked[0]["metadata"]["source_file"] == "test.txt"
    assert "reranker_score" in reranked[0]  # Score should be attached