# tests/test_api.py

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "Secure Multi-Tenant RAG API"


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "chromadb" in data
    assert "status" in data


def test_chat_endpoint_validation():
    """Test that missing fields trigger a 422 validation error."""
    payload = {
        "query": "Test",
        # Missing department and role
    }
    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 422
    assert response.json()["status"] == "validation_error"


def test_chat_endpoint_success():
    """Mock the chat_service to avoid hitting real models/databases."""
    from app.models.schemas import ChatResponse, ChatMetadata, Performance, Source, ScoreInfo

    def mock_ask(request):
        return ChatResponse(
            answer="Mock answer",
            sources=[Source(
                file="mock.txt",
                department="Dept",
                role="Role",
                text_preview="Mock preview",
                scores=ScoreInfo()
            )],
            metadata=ChatMetadata(
                request_id="123",
                department="Dept",
                role="Role",
                retrieved_candidates=5,
                returned_chunks=1,
                retriever="Mock",
                reranker="Mock"
            ),
            performance=Performance(
                latency_ms=10.0,
                retrieval_ms=5.0,
                reranking_ms=2.0,
                generation_ms=3.0
            ),
            status="success"
        )

    # 🔥 Use patch to mock the ask function at the module level
    with patch("app.api.v1.chat.ask", side_effect=mock_ask):
        payload = {
            "query": "Test query",
            "department": "Department_A",
            "role": "Engineering"
        }
        response = client.post("/api/v1/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Mock answer"
    assert data["status"] == "success"
    assert "metadata" in data
    assert "performance" in data