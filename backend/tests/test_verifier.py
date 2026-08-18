from app.agent.verifier import verify_plan
from app.models.schemas import CareerPlan, RecommendedPath
from tests.fixtures.personas import BACKEND_SWE_TO_ML


def test_verifier_catches_invented_user_skill():
    plan = CareerPlan(
        recommended_paths=[RecommendedPath(title="ML path", rationale="Roles require ML evidence.", fit_summary="Good fit.", confidence=0.9)],
        strengths=["Demonstrated quantum computing"],
        overall_confidence=0.92,
    )
    result = verify_plan(plan, BACKEND_SWE_TO_ML, [])
    assert result.unsupported_profile_claims == ["Demonstrated quantum computing"]
    assert result.unsupported_market_claims == ["ML path"]
    assert result.confidence_adjustment < 0

