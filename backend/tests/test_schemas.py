import pytest
from pydantic import ValidationError

from app.models.schemas import CareerGoal, CareerPlan, CareerProfile, EvidenceItem


def test_core_schema_validation():
    profile = CareerProfile(skills=["Python", "python", " SQL "])
    assert profile.skills == ["Python", "SQL"]
    goal = CareerGoal(target_role="AI Engineer", horizon_months=6)
    evidence = EvidenceItem(claim="Role requires Python.", source_type="fixture", source_title="fixture")
    plan = CareerPlan(evidence=[evidence], overall_confidence=0.6)
    assert goal.target_role == "AI Engineer"
    assert plan.evidence[0].confidence == 0.7


def test_goal_horizon_bounds():
    with pytest.raises(ValidationError):
        CareerGoal(target_role="AI Engineer", horizon_months=0)

