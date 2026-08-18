from __future__ import annotations

from app.models.schemas import CareerConstraints, CareerGoal, CareerProfile, NextAction, SkillGap


def rank_next_actions(
    profile: CareerProfile,
    goal: CareerGoal,
    gaps: list[SkillGap],
    constraints: CareerConstraints,
) -> list[NextAction]:
    """Prioritize actions by impact, effort, and stated constraints."""

    actions: list[NextAction] = []
    top_gap = gaps[0].skill if gaps else "target-role evidence"
    time_note = []
    effort = 3
    if constraints.time_budget_hours_per_week and constraints.time_budget_hours_per_week < 6:
        time_note.append("Low weekly time budget: prefer narrow, portfolio-visible work.")
        effort = 2

    actions.append(
        NextAction(
            title=f"Close the top gap: {top_gap}",
            rationale=(
                f"Create clearer proof for {top_gap}. This means building, improving, or documenting work that shows "
                f"a reviewer you can already handle that part of a {goal.target_role} role."
            ),
            impact=5,
            effort=effort,
            priority=1,
            constraint_notes=time_note,
        )
    )
    actions.append(
        NextAction(
            title="Rewrite profile narrative for the target role",
            rationale=(
                "Describe the same real experience using the language of the target role. For example, explain the "
                "problem, tools, tradeoffs, metrics, failures, and outcome for each strong project."
            ),
            impact=4,
            effort=2,
            priority=2,
            constraint_notes=[],
        )
    )
    actions.append(
        NextAction(
            title="Run two informational interviews or portfolio reviews",
            rationale=(
                "Ask people near the role, such as working professionals, recruiters, professors, or advanced students, "
                "to review your portfolio/resume and tell you which proof is missing or unclear."
            ),
            impact=4,
            effort=3,
            priority=3,
            constraint_notes=[f"Location constraint: {constraints.location}"] if constraints.location else [],
        )
    )
    if goal.horizon_months <= 6:
        actions.append(
            NextAction(
                title="Choose applications that value adjacent experience",
                rationale="The short horizon favors roles where existing strengths outweigh missing credentials.",
                impact=4,
                effort=2,
                priority=4,
                constraint_notes=["Short timeline: avoid long prerequisite chains."],
            )
        )
    return sorted(actions, key=lambda action: (action.priority, action.effort))
