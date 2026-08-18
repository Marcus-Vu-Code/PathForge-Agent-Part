from app.config import Settings
from app.services.options import generate_specializations, provider_options, requirements_for_goal


def test_every_sector_role_generates_corresponding_specializations_and_requirements():
    options = provider_options(Settings(PATHFORGE_PROVIDER_MODE="fake"))
    assert len(options.sectors) == 10

    for sector in options.sectors:
        assert len(sector.roles) == 10
        for role in sector.roles:
            specializations = generate_specializations(sector.value, role.value)
            labels = [specialization.label for specialization in specializations]
            values = [specialization.value for specialization in specializations]
            assert len(specializations) >= 4
            assert len(values) == len(set(values))
            assert labels[0] != "Career Transition Story"
            requirements = requirements_for_goal(sector.value, role.value, values[0])
            assert len(requirements) >= 4


def test_google_api_first_is_the_default_website_mode(monkeypatch):
    monkeypatch.delenv("PATHFORGE_PROVIDER_MODE", raising=False)
    options = provider_options(Settings(_env_file=None))
    assert options.default_provider_mode == "hybrid-gemini-first"
    assert options.intelligent_systems[0].provider_mode == "hybrid-gemini-first"
    assert options.intelligent_systems[0].configured is True


def test_ai_engineer_has_expanded_ai_native_specializations():
    specializations = generate_specializations("science_engineering_environment", "AI Engineer")
    labels = {specialization.label for specialization in specializations}
    assert len(specializations) >= 8
    assert "RAG / Knowledge Systems" in labels
    assert "AI Agent Workflows" in labels
    assert "Model Fine-Tuning" in labels
    assert "Responsible AI / Safety" in labels
