import pytest

from app.config import Settings
from app.models.schemas import CareerPlan, CareerReasoningRequest, CareerReasoningResult, RecommendedPath
from app.providers.base import ProviderContractError
from app.providers.local_mole_provider import LocalCareerReasoningResponse
from tests.fixtures.personas import BACKEND_SWE_TO_ML, ML_GOAL


def test_local_provider_contract_parsing():
    payload = {
        "plan": {
            "recommended_paths": [{"title": "AI Engineer", "rationale": "Good fit", "fit_summary": "Python", "confidence": 0.7}],
            "overall_confidence": 0.7,
        },
        "routing_trace": {
            "sector": [{"expert": "technology", "score": 0.61}],
            "function": [{"expert": "ai_data", "score": 0.72}],
            "selected": ["technology", "ai_data"],
        },
        "model_trace": {"model_version": "pathforge-mm-test", "latency_ms": 12, "warnings": []},
    }
    parsed = LocalCareerReasoningResponse.model_validate(payload)
    assert parsed.routing_trace.selected == ["technology", "ai_data"]
    assert parsed.model_trace.model_version == "pathforge-mm-test"


def test_malformed_local_response_is_contract_error_shape():
    with pytest.raises(Exception):
        LocalCareerReasoningResponse.model_validate({"routing_trace": {}})

