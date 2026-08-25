from app.config import Settings
from app.services.options import generate_specializations, provider_options, requirements_for_goal


def test_every_sector_role_generates_corresponding_specializations_and_requirements():
    options = provider_options(Settings(PATHFORGE_PROVIDER_MODE="fake"))
    assert len(options.sectors) == 10
    visible_menus = set()

    for sector in options.sectors:
        assert len(sector.roles) == 10
        for role in sector.roles:
            specializations = generate_specializations(sector.value, role.value)
            labels = [specialization.label for specialization in specializations]
            values = [specialization.value for specialization in specializations]
            assert len(specializations) >= 4
            assert len(values) == len(set(values))
            assert "Career Transition Story" not in labels
            assert "Portfolio / Experience Evidence" not in labels
            visible_menus.add(tuple(labels))
            requirements = requirements_for_goal(sector.value, role.value, values[0])
            assert len(requirements) >= 4

    assert len(visible_menus) == 100


def test_representative_roles_start_with_domain_specific_tracks():
    expected_first_tracks = {
        ("business_operations", "Project Coordinator"): "Project Delivery",
        ("healthcare_wellness", "Clinical Research Coordinator"): "Study Coordination",
        ("education_training", "Corporate Trainer"): "Facilitation / Delivery",
        ("skilled_trades_construction", "Maintenance Planner"): "Preventive Maintenance Strategy",
        ("public_service_government", "Public Administration Analyst"): "Government Program Analysis",
        ("arts_media_design", "Digital Marketing Designer"): "Campaign Creative",
        ("law_policy_compliance", "Privacy Analyst"): "Privacy Operations",
        ("sales_marketing_customer", "Growth Marketing Analyst"): "Growth Experimentation",
        ("finance_accounting_real_estate", "Financial Analyst"): "Financial Modeling",
        ("science_engineering_environment", "Robotics Engineer"): "Robot Perception",
    }

    for (sector, role), expected in expected_first_tracks.items():
        assert generate_specializations(sector, role)[0].label == expected


def test_selected_specialization_changes_the_highest_priority_requirements():
    capacity = requirements_for_goal(
        "business_operations",
        "Operations Analyst",
        "operations_analyst__capacity_service_analysis",
    )
    metrics = requirements_for_goal(
        "business_operations",
        "Operations Analyst",
        "operations_analyst__operations_kpi_design",
    )

    assert capacity[:3] == ["capacity analysis", "service-level analysis", "spreadsheet modeling"]
    assert metrics[:3] == ["kpi definition", "dashboard design", "metric governance"]
    assert capacity != metrics


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
