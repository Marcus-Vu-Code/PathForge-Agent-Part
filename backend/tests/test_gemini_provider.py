from types import SimpleNamespace

import pytest

from app.config import Settings
from app.models.schemas import CareerPlan, CareerReasoningRequest, RecommendedPath
from app.providers.gemini_provider import GeminiCareerReasoner
from tests.fixtures.personas import BACKEND_SWE_TO_ML, ML_GOAL


class FakeGeminiCompletions:
    def __init__(self):
        self.calls = []

    async def parse(self, **kwargs):
        self.calls.append(kwargs)
        plan = CareerPlan(
            recommended_paths=[
                RecommendedPath(
                    title="Gemini ML path",
                    rationale="Evidence-backed",
                    fit_summary="Python and backend experience",
                    confidence=0.7,
                )
            ],
            overall_confidence=0.7,
        )
        message = SimpleNamespace(parsed=plan, content=plan.model_dump_json())
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeGeminiClient:
    def __init__(self):
        completions = FakeGeminiCompletions()
        self.beta = SimpleNamespace(chat=SimpleNamespace(completions=completions))
        self.completions = completions


@pytest.mark.asyncio
async def test_gemini_reasoner_uses_openai_compatible_parse_boundary():
    client = FakeGeminiClient()
    settings = Settings(
        PATHFORGE_PROVIDER_MODE="gemini",
        GEMINI_API_KEY="test",
        GEMINI_MODEL="gemini-test-model",
    )
    provider = GeminiCareerReasoner(settings, client=client)
    result = await provider.reason(CareerReasoningRequest(profile=BACKEND_SWE_TO_ML, goal=ML_GOAL))
    assert result.provider == "gemini"
    assert result.model_version == "gemini-test-model"
    assert result.plan.recommended_paths[0].title == "Gemini ML path"
    assert client.completions.calls[0]["response_format"] is CareerPlan

