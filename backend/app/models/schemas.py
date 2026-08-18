from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class ArtifactType(str, Enum):
    resume = "resume"
    transcript = "transcript"
    portfolio = "portfolio"
    certificate = "certificate"
    other = "other"


class UploadedArtifact(StrictBaseModel):
    artifact_id: str = Field(default_factory=lambda: str(uuid4()))
    artifact_type: ArtifactType = ArtifactType.resume
    filename: str | None = None
    content_type: str = "text/plain"
    text: str = Field(min_length=1, max_length=120_000)


class SourceArtifact(StrictBaseModel):
    artifact_id: str
    artifact_type: ArtifactType
    filename: str | None = None
    confidence: float = Field(ge=0, le=1, default=0.6)


class EducationItem(StrictBaseModel):
    institution: str | None = None
    degree: str | None = None
    field: str | None = None
    dates: str | None = None
    highlights: list[str] = Field(default_factory=list)


class ExperienceItem(StrictBaseModel):
    title: str
    organization: str | None = None
    dates: str | None = None
    description: str | None = None
    skills: list[str] = Field(default_factory=list)


class ProjectItem(StrictBaseModel):
    name: str
    description: str | None = None
    skills: list[str] = Field(default_factory=list)
    url: str | None = None


class CareerConstraints(StrictBaseModel):
    location: str | None = None
    timeline: str | None = None
    salary: str | None = None
    work_authorization: str | None = None
    time_budget_hours_per_week: int | None = Field(default=None, ge=1, le=80)
    other: list[str] = Field(default_factory=list)


class CareerProfile(StrictBaseModel):
    schema_version: str = "1.0"
    education: list[EducationItem] = Field(default_factory=list)
    experience: list[ExperienceItem] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[ProjectItem] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    constraints: CareerConstraints = Field(default_factory=CareerConstraints)
    source_artifacts: list[SourceArtifact] = Field(default_factory=list)

    @field_validator("skills", "certifications", "interests")
    @classmethod
    def normalize_strings(cls, values: list[str]) -> list[str]:
        seen: set[str] = set()
        normalized: list[str] = []
        for value in values:
            item = value.strip()
            key = item.lower()
            if item and key not in seen:
                seen.add(key)
                normalized.append(item)
        return normalized


class CareerGoal(StrictBaseModel):
    target_role: str = Field(min_length=2)
    target_sector: str | None = None
    target_function: str | None = None
    horizon_months: int = Field(ge=1, le=120, default=12)
    priorities: list[str] = Field(default_factory=list)


ProviderModeOption = Literal[
    "fake",
    "openai",
    "gemini",
    "qwen",
    "local",
    "hybrid-local-first",
    "hybrid-openai-first",
    "hybrid-gemini-first",
]


class EvidenceItem(StrictBaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    claim: str = Field(min_length=1)
    source_type: Literal["user_profile", "job_description", "market", "tool", "provider", "fixture"]
    source_title: str
    source_url: HttpUrl | str | None = None
    extracted_requirement: str | None = None
    confidence: float = Field(ge=0, le=1, default=0.7)


class RequirementMatch(StrictBaseModel):
    requirement: str
    evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1, default=0.5)


class JobFitAnalysis(StrictBaseModel):
    matched: list[RequirementMatch] = Field(default_factory=list)
    partial: list[RequirementMatch] = Field(default_factory=list)
    missing: list[RequirementMatch] = Field(default_factory=list)


class SkillGap(StrictBaseModel):
    skill: str
    relevance: float = Field(ge=0, le=1)
    evidence_count: int = Field(ge=0)
    reason: str
    supporting_evidence_ids: list[str] = Field(default_factory=list)


class ProjectRecommendation(StrictBaseModel):
    title: str
    description: str
    addressed_gaps: list[str]
    expected_artifacts: list[str] = Field(default_factory=list)
    estimated_weeks: int = Field(ge=1, le=52, default=4)


class NextAction(StrictBaseModel):
    title: str
    rationale: str
    impact: int = Field(ge=1, le=5)
    effort: int = Field(ge=1, le=5)
    priority: int = Field(ge=1)
    constraint_notes: list[str] = Field(default_factory=list)


class RecommendedPath(StrictBaseModel):
    title: str
    rationale: str
    fit_summary: str
    confidence: float = Field(ge=0, le=1)


class CareerPlan(StrictBaseModel):
    schema_version: str = "1.0"
    recommended_paths: list[RecommendedPath] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    gaps: list[SkillGap] = Field(default_factory=list)
    next_actions: list[NextAction] = Field(default_factory=list)
    project_recommendations: list[ProjectRecommendation] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    overall_confidence: float = Field(ge=0, le=1, default=0.65)


class RoutingScore(StrictBaseModel):
    expert: str
    score: float = Field(ge=0, le=1)


class RoutingTrace(StrictBaseModel):
    sector: list[RoutingScore] = Field(default_factory=list)
    function: list[RoutingScore] = Field(default_factory=list)
    selected: list[str] = Field(default_factory=list)


class AgentTrace(StrictBaseModel):
    provider: str
    model_version: str | None = None
    tools_called: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    latency_ms: int = Field(ge=0, default=0)
    fallback_events: list[str] = Field(default_factory=list)
    routing_trace: RoutingTrace | None = None
    warnings: list[str] = Field(default_factory=list)


class EvidenceSpan(StrictBaseModel):
    label: str
    text: str
    confidence: float = Field(ge=0, le=1, default=0.6)


class BackgroundArtifactExtraction(StrictBaseModel):
    artifact_id: str
    artifact_type: ArtifactType
    raw_text: str | None = None
    entities: CareerProfile
    evidence_spans: list[EvidenceSpan] = Field(default_factory=list)
    extraction_confidence: float = Field(ge=0, le=1, default=0.6)
    warnings: list[str] = Field(default_factory=list)


class CareerReasoningRequest(StrictBaseModel):
    run_id: UUID = Field(default_factory=uuid4)
    profile: CareerProfile
    goal: CareerGoal
    evidence: list[EvidenceItem] = Field(default_factory=list)
    job_fit: JobFitAnalysis | None = None
    gaps: list[SkillGap] = Field(default_factory=list)
    projects: list[ProjectRecommendation] = Field(default_factory=list)
    next_actions: list[NextAction] = Field(default_factory=list)
    task: Literal["career_plan"] = "career_plan"
    routing: dict[str, Any] = Field(
        default_factory=lambda: {
            "mode": "auto",
            "sector_hint": None,
            "function_hint": None,
            "top_k": 2,
        }
    )


class CareerReasoningResult(StrictBaseModel):
    plan: CareerPlan
    provider: str
    model_version: str | None = None
    latency_ms: int = Field(ge=0, default=0)
    routing_trace: RoutingTrace | None = None
    warnings: list[str] = Field(default_factory=list)


class VerificationResult(StrictBaseModel):
    warnings: list[str] = Field(default_factory=list)
    unsupported_profile_claims: list[str] = Field(default_factory=list)
    unsupported_market_claims: list[str] = Field(default_factory=list)
    confidence_adjustment: float = Field(ge=-1, le=0, default=0)


class ProfileCreateResponse(StrictBaseModel):
    id: str
    profile: CareerProfile


class DocumentSourceSummary(StrictBaseModel):
    filename: str
    artifact_type: ArtifactType
    content_type: str
    character_count: int = Field(ge=0)


class BackgroundPromptResponse(StrictBaseModel):
    background_prompt: str = Field(min_length=1, max_length=120_000)
    profile: CareerProfile
    extraction: BackgroundArtifactExtraction
    sources: list[DocumentSourceSummary] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class CareerPlanRequest(StrictBaseModel):
    profile_id: str | None = None
    profile: CareerProfile | None = None
    goal: CareerGoal
    job_description: str | None = None
    provider_mode: ProviderModeOption | None = None


class SelectOption(StrictBaseModel):
    value: str
    label: str
    description: str | None = None


class RoleOption(SelectOption):
    specializations: list[str] = Field(default_factory=list)


class SectorOption(SelectOption):
    roles: list[RoleOption]


class IntelligentSystemOption(SelectOption):
    provider_mode: ProviderModeOption
    configured: bool = True


class ProviderOptionsResponse(StrictBaseModel):
    default_provider_mode: ProviderModeOption
    intelligent_systems: list[IntelligentSystemOption]
    sectors: list[SectorOption]
    specializations: list[SelectOption]


class CareerPlanResponse(StrictBaseModel):
    run_id: str
    profile_id: str | None = None
    plan: CareerPlan
    trace: AgentTrace
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
