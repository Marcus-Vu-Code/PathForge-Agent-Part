from fastapi.testclient import TestClient

from app.main import create_app
from tests.fixtures.personas import BACKEND_SWE_TO_ML, ML_GOAL


def test_end_to_end_fastapi_run():
    client = TestClient(create_app())
    with client:
        health = client.get("/api/health")
        assert health.status_code == 200

        options = client.get("/api/provider-options")
        assert options.status_code == 200
        payload = options.json()
        assert len(payload["sectors"]) == 10
        assert all(len(sector["roles"]) == 10 for sector in payload["sectors"])
        assert any(system["provider_mode"] == "gemini" for system in payload["intelligent_systems"])

        specializations = client.get(
            "/api/goal-specializations",
            params={"sector": "business_operations", "target_role": "Operations Analyst"},
        )
        assert specializations.status_code == 200
        assert len(specializations.json()) >= 3

        profile_response = client.post("/api/profiles", json=BACKEND_SWE_TO_ML.model_dump(mode="json"))
        assert profile_response.status_code == 200
        profile_id = profile_response.json()["id"]

        plan_response = client.post(
            "/api/career-plan",
            json={"profile_id": profile_id, "goal": ML_GOAL.model_dump(mode="json"), "provider_mode": "fake"},
        )
        assert plan_response.status_code == 200
        run = plan_response.json()
        assert run["plan"]["recommended_paths"]
        assert run["trace"]["tools_called"]

        fetched = client.get(f"/api/runs/{run['run_id']}")
        assert fetched.status_code == 200
        assert fetched.json()["run_id"] == run["run_id"]


def test_background_prompt_from_multiple_documents():
    client = TestClient(create_app())
    with client:
        response = client.post(
            "/api/background-prompt",
            data={"provider_mode": "fake"},
            files=[
                (
                    "files",
                    (
                        "resume.txt",
                        b"AI Engineer with Python, FastAPI, Docker, React, PyTorch, and model evaluation projects.",
                        "text/plain",
                    ),
                ),
                (
                    "files",
                    (
                        "transcript.txt",
                        b"BS Software Engineering. Coursework: Statistics, Machine Learning, Data Structures.",
                        "text/plain",
                    ),
                ),
            ],
        )
        assert response.status_code == 200
        payload = response.json()
        assert "Candidate Background" in payload["background_prompt"]
        assert "resume.txt" in payload["background_prompt"]
        assert len(payload["sources"]) == 2
        assert "python" in [skill.lower() for skill in payload["profile"]["skills"]]
