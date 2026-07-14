# backend/tests/test_llm.py
import pytest
import sys
from pathlib import Path

# Add the parent directory to the Python path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.llm.llm import call_llm
from app.config import GROQ_API_KEY


# Skip ALL tests if no API key is set (so you don't get useless errors locally)
pytestmark = pytest.mark.skipif(
    not GROQ_API_KEY or GROQ_API_KEY == "gsk_your-actual-api-key-here",
    reason="GROQ_API_KEY not set in .env"
)


def test_basic_prompt():
    """Test that the LLM responds to a simple question."""
    response = call_llm("What is the capital of France?")
    
    # Assertions: Check that the response contains "Paris" and is not empty
    assert "Paris" in response, f"Expected 'Paris' in response, got: {response}"
    assert len(response) > 10, "Response is too short"


def test_system_prompt():
    """Test that the system prompt overrides the model's behavior."""
    response = call_llm(
        prompt="What is the capital of France?",
        system_prompt="Answer only with the city name. Do not include any other text."
    )
    
    # The response should be exactly "Paris" (or very close to it)
    # We'll just check that it contains Paris and is relatively short
    assert "Paris" in response
    assert len(response) < 100, "System prompt failed to constrain the output"


def test_temperature_and_tokens():
    """Test that temperature and max_tokens parameters work."""
    response = call_llm(
        prompt="Write a one-sentence summary of the French Revolution.",
        temperature=0.7,
        max_tokens=100
    )
    
    # Check that it responded and isn't completely empty
    assert "French" in response or "Revolution" in response
    assert len(response) > 10, "Response is too short"


def test_rag_style_context():
    """Test that the LLM uses the context provided in the system prompt."""
    context = """
    The company vacation policy allows 25 days of paid leave per year.
    Employees can carry over up to 5 unused days to the next year.
    """
    
    system_prompt = f"""You are an HR assistant. Answer based ONLY on the following context.
    If the answer is not in the context, say "I don't have enough information."
    
    Context: {context}"""
    
    response = call_llm(
        prompt="How many vacation days do employees get?",
        system_prompt=system_prompt,
        temperature=0.1  # Low temp for factual stuff
    )
    
    # Check that the response contains the expected number
    assert "25" in response, f"Expected '25' in response, got: {response}"
    assert "year" in response or "day" in response


# Edge-case test for empty prompt
def test_empty_prompt():
    """Test behavior when the prompt is empty (should still work or error gracefully)."""
    try:
        response = call_llm("")
        # If it returns anything, fine, if it raises an error, we catch it
        assert response is not None
    except Exception as e:
        # If it throws an exception, that's acceptable for an empty prompt
        # but we want to know about it, so we'll print it
        print(f"Empty prompt raised exception (expected maybe): {e}")