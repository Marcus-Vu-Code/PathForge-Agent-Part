from __future__ import annotations

from app.models.schemas import CareerGoal, EvidenceItem
from app.services.options import requirements_for_goal


ROLE_REQUIREMENTS = {
    "applied ai engineer": ["python", "llm", "model integration", "evaluation", "fastapi", "deployment automation"],
    "backend ai platform engineer": ["python", "fastapi", "docker", "mlops", "cloud deployment", "sql"],
    "full-stack ai engineer": ["react", "typescript", "fastapi", "llm", "authentication", "model integration"],
    "ml engineer": ["python", "machine learning", "pytorch", "mlops", "cloud deployment", "statistics"],
    "machine learning engineer": ["python", "machine learning", "pytorch", "mlops", "cloud deployment", "statistics"],
    "ai engineer": ["python", "llm", "machine learning", "evaluation", "prompting", "deployment automation"],
    "medical ai engineer": ["python", "pytorch", "medical imaging", "model evaluation", "privacy", "mlops"],
    "clinical ml engineer": ["python", "machine learning", "health analytics", "privacy", "model evaluation", "deployment automation"],
    "robotics engineer": ["robotics", "control systems", "python", "c++", "simulation", "deployment"],
    "autonomy software engineer": ["robotics", "python", "c++", "simulation", "perception", "deployment"],
    "perception engineer": ["computer vision", "opencv", "python", "sensor fusion", "robotics", "model evaluation"],
    "health data scientist": ["python", "statistics", "health analytics", "sql", "privacy", "machine learning"],
    "quantum software engineer": ["python", "linear algebra", "quantum computing", "software engineering", "simulation"],
    "quantum ai engineer": ["python", "machine learning", "linear algebra", "quantum computing", "model evaluation"],
    "ai security engineer": ["python", "security", "model evaluation", "red teaming", "networking", "automation"],
    "security software engineer": ["python", "networking", "security", "linux", "automation", "testing"],
}


SPECIALIZATION_REQUIREMENTS = {
    "ai_data": ["python", "machine learning", "model evaluation", "statistics", "data preprocessing", "experimentation"],
    "applied_ai": ["llm", "model integration", "fastapi", "prompting", "evaluation", "user-facing AI workflows"],
    "mlops": ["docker", "model serving", "latency profiling", "monitoring", "deployment automation", "api reliability"],
    "software": ["api design", "testing", "sql", "system design", "authentication", "backend services"],
    "robotics_autonomy": ["robotics", "sensor fusion", "simulation", "controls", "computer vision", "python"],
    "health_ai": ["medical AI", "privacy", "model evaluation", "clinical workflows", "health analytics", "pytorch"],
    "bioinformatics": ["biology", "omics data", "python", "statistics", "scientific computing", "data pipelines"],
    "quantum_ai": ["linear algebra", "quantum computing", "python", "simulation", "scientific computing", "algorithms"],
    "security_ai": ["security", "threat modeling", "automation", "networking", "adversarial testing", "monitoring"],
    "fintech_ai": ["risk modeling", "fraud detection", "sql", "statistics", "financial data", "backend systems"],
    "education_ai": ["learning analytics", "personalization", "assessment", "llm", "product thinking", "data analysis"],
    "climate_ai": ["geospatial data", "forecasting", "optimization", "energy systems", "sensor data", "data engineering"],
    "public_sector_ai": ["responsible AI", "policy analysis", "compliance", "data governance", "analytics", "accessibility"],
    "creative_ai": ["generative AI", "interactive systems", "content workflows", "real-time inference", "typescript", "product thinking"],
    "commerce_ai": ["recommendation systems", "search relevance", "experimentation", "marketplace data", "sql", "personalization"],
    "legal_ai": ["document review", "privacy", "compliance", "risk controls", "governance", "auditability"],
    "data_engineering": ["etl pipelines", "sql", "data modeling", "orchestration", "data quality", "warehouse design"],
    "product_ai": ["product analytics", "experimentation", "user research", "ai feature design", "metrics", "roadmap tradeoffs"],
}


def gather_market_evidence(goal: CareerGoal, job_description: str | None = None) -> list[EvidenceItem]:
    """Return deterministic MVP market evidence with citation-capable metadata.

    OpenAI mode can enrich this with hosted web_search citations; fake/local tests stay deterministic.
    """

    evidence: list[EvidenceItem] = []
    if job_description:
        for line in job_description.splitlines():
            cleaned = line.strip(" -\t")
            if cleaned:
                evidence.append(
                    EvidenceItem(
                        claim=f"Job description requirement: {cleaned}",
                        source_type="job_description",
                        source_title="Submitted job description",
                        extracted_requirement=cleaned,
                        confidence=0.82,
                    )
                )
    requirements = requirements_for_goal(goal.target_sector, goal.target_role, goal.target_function)
    for requirement in requirements:
        evidence.append(
            EvidenceItem(
                claim=f"{goal.target_role} roles commonly require {requirement}.",
                source_type="fixture",
                source_title="PathForge deterministic role evidence fixture",
                extracted_requirement=requirement,
                confidence=0.64,
            )
        )
    return evidence
