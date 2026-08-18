from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.agent.orchestrator import CareerAgent
from app.config import Settings
from app.models.schemas import CareerGoal
from tests.fixtures import personas


CASES = [
    ("backend_swe_to_ml", personas.BACKEND_SWE_TO_ML, personas.ML_GOAL),
    ("ms_ai_to_ai_engineer", personas.MS_AI_TO_AI_ENGINEER, personas.AI_GOAL),
    ("controls_to_robotics", personas.MECH_CONTROLS_TO_ROBOTICS, personas.ROBOTICS_GOAL),
    ("biology_to_health_ds", personas.BIOLOGY_TO_HEALTH_DS, personas.HEALTH_DS_GOAL),
    ("ambiguous_ai", personas.AMBIGUOUS_AI, CareerGoal(target_role="AI Engineer", horizon_months=6)),
]


async def run(provider_mode: str, output: Path) -> None:
    settings = Settings(PATHFORGE_PROVIDER_MODE=provider_mode)
    agent = CareerAgent(settings)
    rows = []
    for case_id, profile, goal in CASES:
        started = time.perf_counter()
        response = await agent.create_plan(profile, goal)
        rows.append(
            {
                "case_id": case_id,
                "schema_success": True,
                "verifier_failures": len(response.trace.warnings),
                "unsupported_profile_claims": [warning for warning in response.trace.warnings if "profile" in warning.lower()],
                "evidence_citation_coverage": len(response.plan.evidence),
                "latency_ms": int((time.perf_counter() - started) * 1000),
                "provider": response.trace.provider,
                "fallback": response.trace.fallback_events,
                "tool_count": len(response.trace.tools_called),
                "routing_trace": response.trace.routing_trace.model_dump(mode="json") if response.trace.routing_trace else None,
            }
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"Wrote {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run PathForge evaluation fixtures.")
    parser.add_argument("--provider", default="fake")
    parser.add_argument("--output", default="backend/evaluation/results.json")
    args = parser.parse_args()
    asyncio.run(run(args.provider, Path(args.output)))


if __name__ == "__main__":
    main()
