"""
Output schema for AI Fraud-Review Copilot.

Defines the CaseNote "form" every drafted case note must fit, plus the
Recommendation enum (escalate / clear). agent.py passes CaseNote to
Gemini as the required response shape, and Pydantic validates the reply.
A missing field, an out-of-range confidence, or any recommendation other
than "escalate" or "clear" raises an error instead of reaching the analyst.

The recommendation is only a suggestion; a human analyst always makes
the final decision.
"""

from pydantic import BaseModel, Field
from enum import Enum

class Recommendation(str, Enum):
    ESCALATE = "escalate"
    CLEAR = "clear"

class CaseNote(BaseModel):
    flag_reason: str          # why it got flagged
    risk_factors: list[str]   # evidence points
    evidence: str              # the explanation text
    recommendation: Recommendation   # only "escalate" or "clear", nothing else
    confidence: float = Field(ge=0.0, le=1.0)   # a number between 0 and 1