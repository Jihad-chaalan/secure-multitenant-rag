# backend/app/security/schemas.py

from typing import Literal, Optional
from pydantic import BaseModel, Field


class ScannerInput(BaseModel):
    """Input to the LLM prompt scanner."""
    query: str = Field(..., description="The user's question")
    department: str = Field(..., description="User's department context")
    role: str = Field(..., description="User's role context")


class ScannerOutput(BaseModel):
    """Output from the LLM prompt scanner."""
    decision: Literal["ALLOW", "BLOCK"] = Field(..., description="Security decision")
    category: Literal[
        "none",
        "jailbreak",
        "cross_tenant",
        "injection",
        "privilege_escalation"
    ] = Field(..., description="Category of the threat")
    reason: str = Field(..., description="Human-readable explanation")
    risk_score: int = Field(..., ge=0, le=100, description="Risk score 0-100")


class SecurityWarning(BaseModel):
    """Security warning returned in the API response."""
    blocked: bool = Field(..., description="Whether the request was blocked")
    category: str = Field(..., description="Category of the threat")
    message: str = Field(..., description="User-facing warning message")
    risk_score: int = Field(..., ge=0, le=100, description="Risk score 0-100")