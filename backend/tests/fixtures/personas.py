from app.models.schemas import CareerConstraints, CareerGoal, CareerProfile, EducationItem, ExperienceItem, ProjectItem


BACKEND_SWE_TO_ML = CareerProfile(
    education=[EducationItem(degree="BS", field="Computer Science")],
    experience=[
        ExperienceItem(
            title="Backend Software Engineer",
            organization="SaaSCo",
            description="Built Python APIs, SQL data models, and production services.",
            skills=["Python", "SQL", "FastAPI", "Docker"],
        )
    ],
    skills=["Python", "SQL", "FastAPI", "Docker", "React"],
    projects=[ProjectItem(name="Analytics API", description="API for product analytics.", skills=["Python", "SQL"])],
)

MS_AI_TO_AI_ENGINEER = CareerProfile(
    education=[EducationItem(degree="MS", field="Artificial Intelligence")],
    experience=[ExperienceItem(title="Graduate Research Assistant", skills=["Python", "Machine Learning", "NLP"])],
    skills=["Python", "Machine Learning", "NLP", "PyTorch"],
    projects=[ProjectItem(name="LLM Evaluation Project", skills=["LLM", "Python"])],
)

MECH_CONTROLS_TO_ROBOTICS = CareerProfile(
    education=[EducationItem(degree="BS", field="Mechanical Engineering")],
    experience=[ExperienceItem(title="Controls Engineer", skills=["Control Systems", "Python"])],
    skills=["Control Systems", "Python", "Simulation"],
)

BIOLOGY_TO_HEALTH_DS = CareerProfile(
    education=[EducationItem(degree="BS", field="Biology")],
    experience=[ExperienceItem(title="Health Analytics Associate", skills=["Health Analytics", "SQL"])],
    skills=["Biology", "Health Analytics", "SQL", "Statistics"],
)

AMBIGUOUS_AI = CareerProfile(
    experience=[ExperienceItem(title="Operations Coordinator", description="Interested in AI tools.")],
    interests=["AI"],
    constraints=CareerConstraints(time_budget_hours_per_week=4),
)

ML_GOAL = CareerGoal(target_role="ML Engineer", target_sector="technology", target_function="ai_data", horizon_months=12)
AI_GOAL = CareerGoal(target_role="AI Engineer", target_sector="technology", target_function="ai_data", horizon_months=9)
ROBOTICS_GOAL = CareerGoal(target_role="Robotics Engineer", target_sector="engineering", target_function="engineering", horizon_months=18)
HEALTH_DS_GOAL = CareerGoal(target_role="Health Data Scientist", target_sector="health", target_function="data", horizon_months=12)

