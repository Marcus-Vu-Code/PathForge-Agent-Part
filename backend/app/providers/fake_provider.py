from __future__ import annotations

import re
import time

from app.models.schemas import (
    ArtifactType,
    BackgroundArtifactExtraction,
    CareerPlan,
    CareerProfile,
    CareerReasoningRequest,
    CareerReasoningResult,
    EducationItem,
    EvidenceSpan,
    ExperienceItem,
    ProjectItem,
    RecommendedPath,
    SourceArtifact,
    UploadedArtifact,
)


KNOWN_SKILLS = [
    "python",
    "sql",
    "fastapi",
    "react",
    "typescript",
    "machine learning",
    "ml",
    "pytorch",
    "tensorflow",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "data analysis",
    "statistics",
    "control systems",
    "robotics",
    "biology",
    "health analytics",
    "nlp",
]


class FakeBackgroundExtractor:
    async def extract(self, artifact: UploadedArtifact) -> BackgroundArtifactExtraction:
        text = artifact.text
        lowered = text.lower()
        skills = [skill for skill in KNOWN_SKILLS if skill in lowered]
        if "ml" in skills and "machine learning" not in skills:
            skills.append("machine learning")

        title = "Candidate"
        title_match = re.search(r"(software engineer|data scientist|mechanical engineer|ai engineer|student|graduate)", lowered)
        if title_match:
            title = title_match.group(1).title()

        education: list[EducationItem] = []
        if re.search(r"\b(ms|m\.s\.|master|graduate)\b", lowered):
            education.append(EducationItem(degree="MS", field="AI or related field"))
        elif re.search(r"\b(bs|b\.s\.|bachelor)\b", lowered):
            education.append(EducationItem(degree="BS", field="STEM or related field"))

        projects: list[ProjectItem] = []
        for line in text.splitlines():
            if "project" in line.lower() and len(line.strip()) > 8:
                projects.append(ProjectItem(name=line.strip()[:80], description=line.strip(), skills=skills[:5]))

        profile = CareerProfile(
            education=education,
            experience=[ExperienceItem(title=title, description="Extracted from submitted background.", skills=skills[:8])],
            skills=skills,
            projects=projects[:4],
            interests=["AI"] if "ai" in lowered or "machine learning" in lowered else [],
            source_artifacts=[
                SourceArtifact(
                    artifact_id=artifact.artifact_id,
                    artifact_type=ArtifactType(artifact.artifact_type),
                    filename=artifact.filename,
                    confidence=0.72,
                )
            ],
        )
        confidence = 0.78 if skills else 0.45
        warnings = [] if skills else ["Low-confidence extraction: no known skills were detected."]
        return BackgroundArtifactExtraction(
            artifact_id=artifact.artifact_id,
            artifact_type=artifact.artifact_type,
            raw_text=text[:10_000],
            entities=profile,
            evidence_spans=[EvidenceSpan(label="skills", text=", ".join(skills), confidence=confidence)] if skills else [],
            extraction_confidence=confidence,
            warnings=warnings,
        )


class FakeCareerReasoner:
    async def reason(self, request: CareerReasoningRequest) -> CareerReasoningResult:
        started = time.perf_counter()
        goal = request.goal
        top_gaps = request.gaps[:5]
        strengths = request.profile.skills[:6] or ["Existing domain experience"]
        plan = CareerPlan(
            recommended_paths=[
                RecommendedPath(
                    title=f"{goal.target_role} transition path",
                    rationale="Build from demonstrated strengths while closing the highest-evidence gaps first.",
                    fit_summary=f"Current strengths include {', '.join(strengths[:3])}.",
                    confidence=0.72 if request.evidence else 0.62,
                )
            ],
            strengths=[f"Demonstrated {skill}" for skill in strengths[:5]],
            gaps=top_gaps,
            next_actions=request.next_actions,
            project_recommendations=request.projects,
            evidence=request.evidence,
            caveats=["Synthetic fake provider output for local demos; use a configured live provider for live reasoning."],
            overall_confidence=0.7 if request.evidence else 0.6,
        )
        return CareerReasoningResult(
            plan=plan,
            provider="fake",
            model_version="fake-career-reasoner-v1",
            latency_ms=int((time.perf_counter() - started) * 1000),
        )
