# backend/app/api/v1/chat.py

import time
import uuid
import logging
from fastapi import APIRouter, Request
from app.models.schemas import ChatRequest, ChatResponse, Performance, SecurityWarning
from app.services.chat_service import ask
from app.security.prompt_scanner import scan_prompt
from app.config import ENABLE_AI_SECURITY_LAYER

logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, req: Request):
    # Generate a session ID for tracking (if not provided)
    session_id = request.session_id or str(uuid.uuid4())

    # --- 1. RUN AI SECURITY SCANNER ---
    scanner_start = time.perf_counter()
    verdict = scan_prompt(
        query=request.query,
        department=request.department,
        role=request.role,
    )
    scanner_ms = (time.perf_counter() - scanner_start) * 1000

    # --- 2. IF BLOCKED → SKIP RAG AND RETURN WARNING ---
    if verdict.decision == "BLOCK":
        return ChatResponse(
            answer=None,
            sources=[],
            performance=Performance(
                latency_ms=scanner_ms,
                retrieval_ms=0.0,
                reranking_ms=0.0,
                generation_ms=0.0,
                scanner_ms=round(scanner_ms, 2),
            ),
            metadata=None,
            status="blocked",
            security_warning=SecurityWarning(
                blocked=True,
                category=verdict.category,
                message="Your request was blocked by the AI security layer.",
                risk_score=verdict.risk_score,
            ),
        )

    # --- 3. IF SAFE → RUN RAG PIPELINE ---
    response = ask(request)

    # Attach scanner metrics
    if response.performance:
        response.performance.scanner_ms = round(scanner_ms, 2)
        response.performance.latency_ms += scanner_ms  # Add scanner time to total

    # No security warning for safe requests
    response.security_warning = None
    response.status = "success"

    return response