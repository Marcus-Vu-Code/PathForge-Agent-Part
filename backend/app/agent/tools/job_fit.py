from __future__ import annotations

import re

from app.models.schemas import CareerProfile, JobFitAnalysis, RequirementMatch


STOPWORDS = {
    "and",
    "or",
    "with",
    "the",
    "for",
    "to",
    "in",
    "of",
    "a",
    "an",
    "experience",
    "requirements",
    "requirement",
    "required",
    "knowledge",
    "must",
    "should",
    "have",
    "know",
    "ability",
}


def analyze_job_fit(profile: CareerProfile, job_description: str) -> JobFitAnalysis:
    """Compare a profile to explicit requirements from a job description."""

    requirements = _extract_requirements(job_description)
    profile_terms = _profile_terms(profile)
    matched: list[RequirementMatch] = []
    partial: list[RequirementMatch] = []
    missing: list[RequirementMatch] = []

    for requirement in requirements:
        tokens = _keywords(requirement)
        hits = sorted(token for token in tokens if token in profile_terms)
        confidence = len(hits) / max(len(tokens), 1)
        evidence = [term for term in hits]
        item = RequirementMatch(requirement=requirement, evidence=evidence, confidence=round(confidence, 2))
        if confidence >= 0.55:
            matched.append(item)
        elif confidence > 0:
            partial.append(item)
        else:
            missing.append(item)

    return JobFitAnalysis(matched=matched, partial=partial, missing=missing)


def _extract_requirements(job_description: str) -> list[str]:
    chunks = re.split(r"[\n.;]+", job_description)
    candidates = []
    for chunk in chunks:
        line = chunk.strip(" -•\t")
        if len(line) < 4:
            continue
        lowered = line.lower()
        if any(word in lowered for word in ["require", "must", "should", "experience", "skill", "proficiency", "knowledge"]):
            candidates.append(line)
    return candidates[:20] or [line.strip() for line in chunks if line.strip()][:10]


def _profile_terms(profile: CareerProfile) -> set[str]:
    text_parts = list(profile.skills) + profile.certifications + profile.interests
    text_parts.extend(exp.title for exp in profile.experience)
    text_parts.extend(exp.description or "" for exp in profile.experience)
    text_parts.extend(skill for exp in profile.experience for skill in exp.skills)
    text_parts.extend(project.name for project in profile.projects)
    text_parts.extend(project.description or "" for project in profile.projects)
    text_parts.extend(skill for project in profile.projects for skill in project.skills)
    text = " ".join(text_parts).lower()
    return _keywords(text)


def _keywords(text: str) -> set[str]:
    raw = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.\-]{1,}", text.lower())
    tokens = {token.strip(".-") for token in raw if token not in STOPWORDS}
    phrases = set()
    for phrase in ["machine learning", "data analysis", "control systems", "health analytics", "cloud deployment"]:
        if phrase in text.lower():
            phrases.add(phrase)
    return tokens | phrases
