# backend/app/security/logger.py

import logging
from datetime import datetime
from typing import Optional

from app.security.schemas import ScannerOutput

logger = logging.getLogger(__name__)


def log_security_event(
    session_id: Optional[str],
    department: str,
    role: str,
    query: str,
    verdict: ScannerOutput,
):
    """
    Log a security event to the console or a file.
    (Frontend logging via Zustand will handle the Admin Dashboard display.)
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id or "unknown",
        "department": department,
        "role": role,
        "query": query[:100],  # Truncate for safety
        "decision": verdict.decision,
        "category": verdict.category,
        "reason": verdict.reason,
        "risk_score": verdict.risk_score,
    }

    if verdict.decision == "BLOCK":
        logger.warning(f"Security event (BLOCKED): {log_entry}")
    else:
        logger.info(f"Security event (ALLOWED): {log_entry}")