import pytest

from app.agent.orchestrator import CareerAgent
from app.config import Settings
from app.models.schemas import CareerReasoningRequest, CareerReasoningResult
from app.providers.base import ProviderContractError, ProviderUnavailableError
from app.providers.fake_provider import FakeBackgroundExtractor, FakeCareerReasoner
from app.providers.gemini_provider import GeminiCareerReasoner
from app.providers.qwen_provider import QwenBackgroundExtractor, QwenCareerReasoner
from tests.fixtures.personas import BACKEND_SWE_TO_ML, ML_GOAL


@pytest.mark.asyncio
async def test_fake_provider_agent_run():
    settings = Settings(PATHFORGE_PROVIDER_MODE="fake")
    response = await CareerAgent(settings).create_plan(BACKEND_SWE_TO_ML, ML_GOAL)
    assert response.plan.recommended_paths
    assert response.trace.provider == "fake"
    assert "verify_plan" in response.trace.tools_called


class TimeoutReasoner:
    async def reason(self, request: CareerReasoningRequest) -> CareerReasoningResult:
        raise ProviderUnavailableError("timeout")


class MalformedReasoner:
    async def reason(self, request: CareerReasoningRequest) -> CareerReasoningResult:
        raise ProviderContractError("invalid schema")


@pytest.mark.asyncio
@pytest.mark.parametrize("reasoner", [TimeoutReasoner(), MalformedReasoner()])
async def test_provider_failure_falls_back_once(reasoner):
    settings = Settings(PATHFORGE_PROVIDER_MODE="hybrid-openai-first")
    response = await CareerAgent(settings, reasoner=reasoner).create_plan(BACKEND_SWE_TO_ML, ML_GOAL)
    assert response.trace.provider == "fake"
    assert len(response.trace.fallback_events) == 1


@pytest.mark.asyncio
async def test_counterfactual_gap_changes_with_added_deployment_project():
    settings = Settings(PATHFORGE_PROVIDER_MODE="fake")
    baseline = await CareerAgent(settings, reasoner=FakeCareerReasoner()).create_plan(BACKEND_SWE_TO_ML, ML_GOAL)
    upgraded = BACKEND_SWE_TO_ML.model_copy(update={"skills": BACKEND_SWE_TO_ML.skills + ["MLOps", "cloud deployment"]})
    changed = await CareerAgent(settings, reasoner=FakeCareerReasoner()).create_plan(upgraded, ML_GOAL)
    baseline_gaps = {gap.skill for gap in baseline.plan.gaps}
    changed_gaps = {gap.skill for gap in changed.plan.gaps}
    assert "cloud deployment" in baseline_gaps
    assert "cloud deployment" not in changed_gaps


def test_gemini_mode_selects_gemini_reasoner():
    settings = Settings(PATHFORGE_PROVIDER_MODE="gemini", GEMINI_API_KEY="test")
    assert isinstance(CareerAgent(settings)._primary_reasoner(), GeminiCareerReasoner)


def test_qwen_mode_selects_qwen_reasoner():
    settings = Settings(PATHFORGE_PROVIDER_MODE="qwen")
    assert isinstance(CareerAgent(settings)._primary_reasoner(), QwenCareerReasoner)


def test_qwen_mode_uses_fast_background_extractor_by_default():
    settings = Settings(PATHFORGE_PROVIDER_MODE="qwen")
    assert isinstance(CareerAgent(settings)._primary_extractor(), FakeBackgroundExtractor)


def test_qwen_mode_can_use_transformers_background_extractor_when_requested():
    settings = Settings(PATHFORGE_PROVIDER_MODE="qwen", QWEN_FAST_BACKGROUND_EXTRACTION=False)
    assert isinstance(CareerAgent(settings)._primary_extractor(), QwenBackgroundExtractor)
