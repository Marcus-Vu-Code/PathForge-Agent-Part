from __future__ import annotations

import re
from collections import Counter, defaultdict

from app.agent.tools.job_fit import _profile_terms
from app.models.schemas import CareerProfile, EvidenceItem, SkillGap


SKILL_SYNONYMS = {
    "ml": "machine learning",
    "k8s": "kubernetes",
    "ci/cd": "deployment automation",
    "llm": "llm",
    "llms": "llm",
}


def analyze_skill_gaps(profile: CareerProfile, role_evidence: list[EvidenceItem]) -> list[SkillGap]:
    """Rank missing role requirements by evidence frequency and profile absence."""

    owned = _profile_terms(profile)
    counts: Counter[str] = Counter()
    evidence_ids: dict[str, list[str]] = defaultdict(list)
    for item in role_evidence:
        requirement = item.extracted_requirement or item.claim
        for skill in _candidate_skills(requirement):
            normalized = SKILL_SYNONYMS.get(skill, skill)
            counts[normalized] += 1
            evidence_ids[normalized].append(item.id)

    gaps: list[SkillGap] = []
    if not counts:
        return gaps

    max_count = max(counts.values())
    for skill, count in counts.items():
        tokens = set(skill.split())
        if skill in owned or tokens.intersection(owned):
            continue
        relevance = min(1.0, 0.45 + 0.55 * (count / max_count))
        gaps.append(
            SkillGap(
                skill=skill,
                relevance=round(relevance, 2),
                evidence_count=count,
                reason=f"Appears in {count} evidence item(s) for the target role and is not clearly present in the profile.",
                supporting_evidence_ids=evidence_ids[skill],
            )
        )
    return sorted(gaps, key=lambda gap: (-gap.relevance, -gap.evidence_count, gap.skill))[:10]


def _candidate_skills(text: str) -> set[str]:
    lowered = text.lower()
    known = [
        "python",
        "sql",
        "machine learning",
        "deep learning",
        "pytorch",
        "tensorflow",
        "statistics",
        "data engineering",
        "mlops",
        "docker",
        "kubernetes",
        "cloud deployment",
        "aws",
        "azure",
        "gcp",
        "react",
        "typescript",
        "robotics",
        "control systems",
        "health analytics",
        "nlp",
        "llm",
    ]
    hits = {skill for skill in known if skill in lowered}
    for token in re.findall(r"\b[A-Za-z][A-Za-z0-9+#./-]{2,}\b", text):
        clean = token.lower().strip("./-")
        if clean in {"experience", "required", "preferred", "candidate", "skills", "build", "using"}:
            continue
        if clean in SKILL_SYNONYMS or clean in known:
            hits.add(clean)
    return hits

