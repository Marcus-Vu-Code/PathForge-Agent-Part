from __future__ import annotations

import time
from uuid import uuid4

from app.agent.tools import (
    analyze_job_fit,
    analyze_skill_gaps,
    gather_market_evidence,
    rank_next_actions,
    recommend_projects,
)
from app.agent.verifier import verify_plan
from app.config import Settings
from app.models.schemas import (
    AgentTrace,
    CareerGoal,
    CareerPlanResponse,
    CareerProfile,
    CareerReasoningRequest,
    UploadedArtifact,
)
from app.providers.base import BackgroundExtractor, CareerReasoner, ProviderContractError, ProviderUnavailableError
from app.providers.fake_provider import FakeBackgroundExtractor, FakeCareerReasoner
from app.providers.gemini_provider import GeminiBackgroundExtractor, GeminiCareerReasoner
from app.providers.local_mole_provider import LocalMoLECareerReasoner, LocalMultimodalExtractor
from app.providers.openai_provider import OpenAIBackgroundExtractor, OpenAICareerReasoner
from app.providers.qwen_provider import QwenBackgroundExtractor, QwenCareerReasoner


class CareerAgent:
    def __init__(
        self,
        settings: Settings,
        extractor: BackgroundExtractor | None = None,
        reasoner: CareerReasoner | None = None,
    ):
        self.settings = settings
        self.extractor = extractor
        self.reasoner = reasoner

    async def extract_background(self, artifact: UploadedArtifact):
        extractor = self.extractor or self._primary_extractor()
        fallback_events: list[str] = []
        try:
            return await extractor.extract(artifact)
        except (ProviderUnavailableError, ProviderContractError) as exc:
            if self.settings.provider_mode.startswith("hybrid") or self.settings.provider_mode in {"openai", "gemini", "qwen", "local"}:
                fallback_events.append(str(exc))
                return await FakeBackgroundExtractor().extract(artifact)
            raise

    async def create_plan(
        self,
        profile: CareerProfile,
        goal: CareerGoal,
        job_description: str | None = None,
        profile_id: str | None = None,
    ) -> CareerPlanResponse:
        started = time.perf_counter()
        run_id = uuid4()
        evidence = gather_market_evidence(goal, job_description)
        tools_called = ["gather_market_evidence"]
        job_fit = analyze_job_fit(profile, job_description) if job_description else None
        if job_fit:
            tools_called.append("analyze_job_fit")
        gaps = analyze_skill_gaps(profile, evidence)
        tools_called.append("analyze_skill_gaps")
        projects = recommend_projects(profile, goal, gaps, profile.constraints.time_budget_hours_per_week)
        next_actions = rank_next_actions(profile, goal, gaps, profile.constraints)
        tools_called.extend(["recommend_projects", "rank_next_actions"])

        request = CareerReasoningRequest(
            run_id=run_id,
            profile=profile,
            goal=goal,
            evidence=evidence,
            job_fit=job_fit,
            gaps=gaps,
            projects=projects,
            next_actions=next_actions,
            routing={
                "mode": "auto",
                "sector_hint": goal.target_sector,
                "function_hint": goal.target_function,
                "top_k": 2,
            },
        )
        fallback_events: list[str] = []
        reasoner = self.reasoner or self._primary_reasoner()
        try:
            result = await reasoner.reason(request)
        except (ProviderUnavailableError, ProviderContractError) as exc:
            fallback_events.append(str(exc))
            result = await self._fallback_reasoner(reasoner).reason(request)

        verification = verify_plan(result.plan, profile, evidence)
        result.plan.caveats.extend(verification.warnings)
        if verification.confidence_adjustment:
            result.plan.overall_confidence = max(0.0, result.plan.overall_confidence + verification.confidence_adjustment)
        tools_called.append("verify_plan")

        trace = AgentTrace(
            provider=result.provider,
            model_version=result.model_version,
            tools_called=tools_called,
            evidence_ids=[item.id for item in evidence + result.plan.evidence],
            latency_ms=result.latency_ms or int((time.perf_counter() - started) * 1000),
            fallback_events=fallback_events,
            routing_trace=result.routing_trace,
            warnings=result.warnings + verification.warnings + _low_confidence_warnings(profile),
        )
        result.plan.evidence = _dedupe_evidence(evidence + result.plan.evidence)
        return CareerPlanResponse(run_id=str(run_id), profile_id=profile_id, plan=result.plan, trace=trace)

    def _primary_extractor(self) -> BackgroundExtractor:
        mode = self.settings.provider_mode
        if mode == "local" or mode == "hybrid-local-first":
            return LocalMultimodalExtractor(self.settings)
        if mode == "gemini" or mode == "hybrid-gemini-first":
            return GeminiBackgroundExtractor(self.settings)
        if mode == "qwen":
            if self.settings.qwen_fast_background_extraction:
                return FakeBackgroundExtractor()
            return QwenBackgroundExtractor(self.settings)
        if mode == "openai" or mode == "hybrid-openai-first":
            return OpenAIBackgroundExtractor(self.settings)
        return FakeBackgroundExtractor()

    def _primary_reasoner(self) -> CareerReasoner:
        mode = self.settings.provider_mode
        if mode == "local" or mode == "hybrid-local-first":
            return LocalMoLECareerReasoner(self.settings)
        if mode == "gemini" or mode == "hybrid-gemini-first":
            return GeminiCareerReasoner(self.settings)
        if mode == "qwen":
            return QwenCareerReasoner(self.settings)
        if mode == "openai" or mode == "hybrid-openai-first":
            return OpenAICareerReasoner(self.settings)
        return FakeCareerReasoner()

    def _fallback_reasoner(self, failed_reasoner: CareerReasoner) -> CareerReasoner:
        if (
            self.settings.provider_mode == "hybrid-local-first"
            and self.settings.enable_openai_fallback
            and self.settings.openai_api_key
        ):
            return OpenAICareerReasoner(self.settings)
        if self.settings.provider_mode == "hybrid-openai-first" and self.settings.local_model_base_url:
            if self.settings.local_model_base_url not in {"http://localhost:8080", "http://127.0.0.1:8080"}:
                return LocalMoLECareerReasoner(self.settings)
        if self.settings.provider_mode == "openai" and self.settings.enable_openai_fallback:
            return FakeCareerReasoner()
        if self.settings.provider_mode == "gemini" and self.settings.enable_openai_fallback:
            return FakeCareerReasoner()
        if self.settings.provider_mode == "qwen" and self.settings.enable_openai_fallback:
            return FakeCareerReasoner()
        if self.settings.provider_mode == "hybrid-gemini-first" and self.settings.enable_openai_fallback:
            if self.settings.openai_api_key:
                return OpenAICareerReasoner(self.settings)
            return FakeCareerReasoner()
        if self.settings.provider_mode == "local" and self.settings.enable_openai_fallback and self.settings.openai_api_key:
            return OpenAICareerReasoner(self.settings)
        return FakeCareerReasoner()


def _low_confidence_warnings(profile: CareerProfile) -> list[str]:
    warnings: list[str] = []
    for artifact in profile.source_artifacts:
        if artifact.confidence < 0.55:
            warnings.append("Low-confidence background extraction: ask the user to review or edit the profile.")
            break
    return warnings


def _dedupe_evidence(items):
    seen = set()
    deduped = []
    for item in items:
        key = (item.claim, str(item.source_url))
        if key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped
