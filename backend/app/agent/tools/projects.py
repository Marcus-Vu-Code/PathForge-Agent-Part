from __future__ import annotations

from app.models.schemas import CareerGoal, CareerProfile, ProjectRecommendation, SkillGap


def recommend_projects(
    profile: CareerProfile,
    goal: CareerGoal,
    gaps: list[SkillGap],
    time_budget: int | None = None,
) -> list[ProjectRecommendation]:
    """Recommend portfolio projects that explicitly cover ranked gaps."""

    selected = [gap.skill for gap in gaps[:6]]
    if not selected:
        selected = ["clear proof you can do this role", "clear interview explanation of your projects"]
    weeks = 3 if (time_budget or 8) < 6 else 4
    role = goal.target_role
    projects = [
        ProjectRecommendation(
            title=f"{role} proof-of-skill project",
            description=(
                "Build a small app, notebook, or portfolio page that shows the inputs, your process, the result, "
                "and what decisions someone could make from it. For AI roles, this could show model output, "
                "confidence, latency, evaluation results, and failure cases."
            ),
            addressed_gaps=selected[:3],
            expected_artifacts=["GitHub repository", "README explaining decisions", "screenshots or short demo recording"],
            estimated_weeks=weeks,
        ),
        ProjectRecommendation(
            title="End-to-end role workflow",
            description=(
                "Show one complete process from start to finish. For AI engineering, that means input, preprocessing, "
                "model call, validation, result, logging/trace, and error handling."
            ),
            addressed_gaps=selected[2:5] or selected[:2],
            expected_artifacts=["deployed demo or local setup", "test report", "simple architecture diagram"],
            estimated_weeks=weeks + 1,
        ),
    ]
    if len(selected) >= 4:
        projects.append(
            ProjectRecommendation(
                title="Target-sector case study",
                description="Write and implement a compact case study tailored to the target sector, showing domain constraints and evaluation criteria.",
                addressed_gaps=selected[3:6],
                expected_artifacts=["case study", "evaluation checklist"],
                estimated_weeks=weeks,
            )
        )
    if profile.projects:
        projects.append(
            ProjectRecommendation(
                title="Upgrade an existing project",
                description=(
                    "Take a project you already have and make the target-role proof obvious: add tests, setup instructions, "
                    "before/after notes, metrics, screenshots, and a README that explains why the work matters."
                ),
                addressed_gaps=selected[:2],
                expected_artifacts=["before/after README", "issue list", "merged improvements"],
                estimated_weeks=2,
            )
        )
    return projects[:4]
