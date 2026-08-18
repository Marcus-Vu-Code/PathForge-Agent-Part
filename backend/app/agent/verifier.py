from __future__ import annotations

import re

from app.agent.tools.job_fit import _profile_terms
from app.models.schemas import CareerPlan, CareerProfile, EvidenceItem, VerificationResult


MARKET_WORDS = {"require", "roles", "market", "employers", "hiring", "salary", "growth", "demand"}


def verify_plan(plan: CareerPlan, profile: CareerProfile, evidence: list[EvidenceItem]) -> VerificationResult:
    """Flag unsupported user claims and market claims before returning a plan."""

    profile_terms = _profile_terms(profile)
    evidence_text = " ".join([item.claim for item in evidence + plan.evidence]).lower()
    warnings: list[str] = []
    unsupported_profile_claims: list[str] = []
    unsupported_market_claims: list[str] = []

    for strength in plan.strengths:
        terms = _important_terms(strength)
        if terms and not any(term in profile_terms for term in terms):
            unsupported_profile_claims.append(strength)

    for path in plan.recommended_paths:
        text = f"{path.rationale} {path.fit_summary}".lower()
        if any(word in text for word in MARKET_WORDS) and not evidence_text:
            unsupported_market_claims.append(path.title)

    if plan.overall_confidence > 0.85 and (unsupported_profile_claims or unsupported_market_claims):
        warnings.append("Plan confidence was too high for the detected support gaps.")

    if unsupported_profile_claims:
        warnings.append("Some claimed user strengths were not found in the structured profile.")
    if unsupported_market_claims:
        warnings.append("Some market claims lacked supporting evidence.")

    penalty = -0.1 * len(warnings)
    return VerificationResult(
        warnings=warnings,
        unsupported_profile_claims=unsupported_profile_claims,
        unsupported_market_claims=unsupported_market_claims,
        confidence_adjustment=max(-0.35, penalty),
    )


def _important_terms(text: str) -> set[str]:
    words = set(re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.-]{2,}\b", text.lower()))
    return words - {"demonstrated", "experience", "with", "and", "the", "role", "strong"}

