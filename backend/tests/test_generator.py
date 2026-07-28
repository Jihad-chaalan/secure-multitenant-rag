# backend/tests/test_generator.py

import pytest
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.generator import build_rag_prompt, generate_answer


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
    
    # ✅ generate_answer returns 3 values: (answer, usage, context)
    answer, usage, context = generate_answer(query, results)
    
    assert "I don't have enough information" in answer or "No relevant documents" in answer
    assert isinstance(usage, dict)
    # context is the formatted string from format_results_for_prompt([])
    assert context == "No relevant documents found."


def test_generate_answer_with_results():
    """Test generate_answer with mock results (using patched LLM call)."""
    with patch('app.rag.generator.call_llm') as mock_call_llm:
        # Mock returns (answer, usage) - 2 values
        mock_call_llm.return_value = ("The capital of France is Paris.", {"total_tokens": 100})
        
        query = "What is the capital of France?"
        mock_results = [
            {
                "text": "The capital of France is Paris. It is located on the Seine River.",
                "metadata": {"source_file": "france.txt"},
                "distance": 0.2
            }
        ]
        
        # ✅ generate_answer returns 3 values: (answer, usage, context)
        answer, usage, context = generate_answer(query, mock_results, temperature=0.1)
        
        mock_call_llm.assert_called_once()
        assert "Paris" in answer
        assert "france.txt" in context
        assert isinstance(usage, dict)
        assert "total_tokens" in usage


def test_generate_answer_empty_query():
    """Test generate_answer with an empty query."""
    query = ""
    results = [{"text": "Some text", "metadata": {}}]
    
    # ✅ generate_answer returns 2 values here: (answer, context)
    # This is the ONLY case where it returns 2 values
    answer, context = generate_answer(query, results)
    
    assert "Please ask a valid question" in answer or "valid question" in answer
    assert context == ""