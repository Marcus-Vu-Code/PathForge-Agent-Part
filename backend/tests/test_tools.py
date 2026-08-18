from app.agent.tools import analyze_job_fit, analyze_skill_gaps, gather_market_evidence, rank_next_actions, recommend_projects
from app.models.schemas import CareerConstraints
from tests.fixtures.personas import BACKEND_SWE_TO_ML, ML_GOAL


def test_job_fit_returns_component_evidence():
    fit = analyze_job_fit(
        BACKEND_SWE_TO_ML,
        "Requirements: Python experience. Must know Kubernetes. Should have SQL.",
    )
    assert any(item.requirement for item in fit.matched)
    assert any("kubernetes" in item.requirement.lower() for item in fit.missing)


def test_skill_gap_ranking_uses_evidence_frequency():
    evidence = gather_market_evidence(ML_GOAL)
    gaps = analyze_skill_gaps(BACKEND_SWE_TO_ML, evidence)
    assert gaps
    assert gaps[0].relevance >= gaps[-1].relevance
    assert "python" not in [gap.skill for gap in gaps]


def test_project_and_action_logic_mentions_gaps_and_constraints():
    gaps = analyze_skill_gaps(BACKEND_SWE_TO_ML, gather_market_evidence(ML_GOAL))
    profile = BACKEND_SWE_TO_ML.model_copy(update={"constraints": CareerConstraints(time_budget_hours_per_week=4)})
    projects = recommend_projects(profile, ML_GOAL, gaps, 4)
    actions = rank_next_actions(profile, ML_GOAL, gaps, profile.constraints)
    assert 2 <= len(projects) <= 4
    assert projects[0].addressed_gaps
    assert actions[0].impact >= actions[0].effort
    assert actions[0].constraint_notes

