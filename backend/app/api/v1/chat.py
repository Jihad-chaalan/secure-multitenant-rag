# backend/app/api/v1/chat.py

import time
import logging
from fastapi import APIRouter, HTTPException, status

from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_service import ask

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Ask a question to the RAG system.

    - **query**: The user's question
    - **department**: Department context (e.g., Department_A)
    - **role**: Role context (e.g., Engineering)
    - **top_k**: Number of chunks to return (default: 5)
    """
    try:
        start_time = time.perf_counter()
        response = ask(request)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred while processing your request."
        )