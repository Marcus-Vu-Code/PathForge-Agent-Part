import json

import pytest

from app.config import Settings
from app.models.schemas import CareerPlan, CareerReasoningRequest, RecommendedPath
from app.providers.openai_provider import OpenAICareerReasoner
from tests.fixtures.personas import BACKEND_SWE_TO_ML, ML_GOAL


class FakeResponses:
    def __init__(self):
        self.calls = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        plan = CareerPlan(
            recommended_paths=[RecommendedPath(title="ML Engineer", rationale="Evidence-backed", fit_summary="Python", confidence=0.7)],
            overall_confidence=0.7,
        )
        return {"output_text": plan.model_dump_json()}


class FakeOpenAIClient:
    def __init__(self):
        self.responses = FakeResponses()


@pytest.mark.asyncio
async def test_openai_provider_uses_responses_api_boundary():
    client = FakeOpenAIClient()
    provider = OpenAICareerReasoner(Settings(PATHFORGE_PROVIDER_MODE="openai", OPENAI_API_KEY="test"), client=client)
    result = await provider.reason(CareerReasoningRequest(profile=BACKEND_SWE_TO_ML, goal=ML_GOAL))
    assert result.plan.recommended_paths[0].title == "ML Engineer"
    assert client.responses.calls
    assert "tools" in client.responses.calls[0]
    assert client.responses.calls[0]["model"]

