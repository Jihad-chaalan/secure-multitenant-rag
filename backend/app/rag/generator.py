# backend/app/rag/generator.py

import logging
from typing import List, Dict, Any

from app.llm.llm import call_llm

logger = logging.getLogger(__name__)


def build_rag_prompt(query: str, context: str) -> str:
    """
    Build a prompt for the LLM with context and a user query.

    Args:
        query: The user's question
        context: The formatted context string (from format_results_for_prompt)

    Returns:
        A string prompt ready for the LLM
    """
    system_prompt = """You are a helpful assistant. Answer the user's question based strictly on the provided context.

CRITICAL RULES:
- ONLY use information from the context below.
- If the context does NOT contain the answer, say "I don't have enough information to answer that."
- Do NOT make up facts or use outside knowledge.
- Keep your answer concise and relevant.

--- CONTEXT ---
{context}

--- USER QUESTION ---
{query}

--- ANSWER ---"""

    return system_prompt.format(context=context, query=query)


def generate_answer(
    query: str,
    results: List[Dict[str, Any]],
    temperature: float = 0.1
) -> tuple[str, str]:
    """
    Generate an answer using the LLM based on retrieved chunks.

    Args:
        query: The user's question
        results: List of search results from retrieve()
        temperature: LLM temperature (lower = more deterministic)

    Returns:
        A tuple of (answer, context_used):
            - answer: The LLM's response
            - context_used: The formatted context string (for debugging/UX)
    """
    if not query or not query.strip():
        return "Please ask a valid question.", ""

    # 1. Format the context
    from app.rag.retriever import format_results_for_prompt
    context = format_results_for_prompt(results)
    
    if not results:
        return "I don't have enough information to answer that. No relevant documents were found.", context

    # 2. Build the prompt
    prompt = build_rag_prompt(query, context)

    # 3. Call the LLM
    try:
        logger.info("🤖 Generating answer with LLM...")
        answer = call_llm(
            prompt=prompt,
            temperature=temperature,
            system_prompt=None  # The system prompt is built into the prompt string
        )
        logger.info("✅ Answer generated.")
        return answer, context
        
    except Exception as e:
        logger.error(f"❌ LLM generation failed: {e}")
        return f"Sorry, I encountered an error while generating the answer: {str(e)}", context