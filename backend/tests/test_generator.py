# backend/tests/test_generator.py

import pytest
from pathlib import Path
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.generator import build_rag_prompt, generate_answer
from app.rag.retriever import format_results_for_prompt


def test_build_rag_prompt():
    """Test that the RAG prompt is built correctly."""
    query = "What is the capital of France?"
    context = "The capital of France is Paris."
    
    prompt = build_rag_prompt(query, context)
    
    assert "What is the capital of France?" in prompt
    assert "The capital of France is Paris." in prompt
    assert "CRITICAL RULES" in prompt


def test_generate_answer_no_results():
    """Test generate_answer when there are no search results."""
    query = "What is the capital of France?"
    results = []
    
    answer, context = generate_answer(query, results)
    
    assert "I don't have enough information" in answer or "No relevant documents" in answer


def test_generate_answer_with_results():
    """Test generate_answer with mock results (using patched LLM call)."""
    # We mock the LLM call to avoid needing a real API key
    with patch('app.rag.generator.call_llm') as mock_call_llm:
        # Set up the mock to return a sample response
        mock_call_llm.return_value = "The capital of France is Paris."
        
        # Create mock search results
        query = "What is the capital of France?"
        mock_results = [
            {
                "text": "The capital of France is Paris. It is located on the Seine River.",
                "metadata": {"source_file": "france.txt"},
                "distance": 0.2
            }
        ]
        
        # Call generate_answer
        answer, context = generate_answer(query, mock_results, temperature=0.1)
        
        # Verify the mock was called
        mock_call_llm.assert_called_once()
        
        # Verify the answer is what we expect
        assert "Paris" in answer
        
        # Verify context is returned
        assert "france.txt" in context