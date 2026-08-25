from __future__ import annotations

from importlib.util import find_spec
import re

from app.config import Settings
from app.models.schemas import IntelligentSystemOption, ProviderOptionsResponse, RoleOption, SectorOption, SelectOption


def role(value: str) -> RoleOption:
    return RoleOption(value=value, label=value, specializations=[])


SECTORS = [
    SectorOption(
        value="business_operations",
        label="Business / Operations",
        description="Operations, project and program delivery, human resources, supply chain, administration, and consulting.",
        roles=[
            role("Operations Analyst"),
            role("Business Analyst"),
            role("Project Coordinator"),
            role("Program Manager"),
            role("Operations Manager"),
            role("Supply Chain Coordinator"),
            role("Human Resources Coordinator"),
            role("Executive Assistant"),
            role("Process Improvement Specialist"),
            role("Management Consultant"),
        ],
    ),
    SectorOption(
        value="healthcare_wellness",
        label="Healthcare / Wellness",
        description="Clinical support, patient services, health administration, wellness, and public health.",
        roles=[
            role("Clinical Research Coordinator"),
            role("Healthcare Administrator"),
            role("Patient Care Coordinator"),
            role("Medical Assistant"),
            role("Public Health Analyst"),
            role("Health Educator"),
            role("Behavioral Health Technician"),
            role("Pharmacy Technician"),
            role("Wellness Program Coordinator"),
            role("Health Information Specialist"),
        ],
    ),
    SectorOption(
        value="education_training",
        label="Education / Training",
        description="Teaching, tutoring, learning design, student support, and workforce training.",
        roles=[
            role("Teacher"),
            role("Tutor"),
            role("Instructional Designer"),
            role("Academic Advisor"),
            role("Training Coordinator"),
            role("Curriculum Developer"),
            role("Student Success Coach"),
            role("Education Program Manager"),
            role("Learning Experience Designer"),
            role("Corporate Trainer"),
        ],
    ),
    SectorOption(
        value="skilled_trades_construction",
        label="Skilled Trades / Construction / Manufacturing",
        description="Construction, maintenance, field service, manufacturing, safety, facilities, and technical operations.",
        roles=[
            role("Electrician Apprentice"),
            role("HVAC Technician"),
            role("Construction Project Coordinator"),
            role("Manufacturing Technician"),
            role("Quality Control Inspector"),
            role("Field Service Technician"),
            role("Facilities Coordinator"),
            role("CNC Operator"),
            role("Safety Coordinator"),
            role("Maintenance Planner"),
        ],
    ),
    SectorOption(
        value="public_service_government",
        label="Public Service / Government / Nonprofit",
        description="Government operations, civic programs, emergency management, policy, community services, and nonprofits.",
        roles=[
            role("Policy Analyst"),
            role("City Planner"),
            role("Public Administration Analyst"),
            role("Emergency Management Specialist"),
            role("Community Outreach Coordinator"),
            role("Nonprofit Program Coordinator"),
            role("Case Manager"),
            role("Grant Writer"),
            role("Compliance Specialist"),
            role("Legislative Aide"),
        ],
    ),
    SectorOption(
        value="arts_media_design",
        label="Arts / Media / Design",
        description="Design, content, communications, production, UX, and creative operations.",
        roles=[
            role("Graphic Designer"),
            role("UX Designer"),
            role("Content Strategist"),
            role("Video Producer"),
            role("Social Media Manager"),
            role("Copywriter"),
            role("Brand Strategist"),
            role("Product Designer"),
            role("Digital Marketing Designer"),
            role("Game Designer"),
        ],
    ),
    SectorOption(
        value="law_policy_compliance",
        label="Law / Policy / Compliance",
        description="Legal support, governance, privacy, regulatory operations, and risk controls.",
        roles=[
            role("Paralegal"),
            role("Legal Assistant"),
            role("Compliance Analyst"),
            role("Privacy Analyst"),
            role("Contract Administrator"),
            role("Risk Analyst"),
            role("Regulatory Affairs Specialist"),
            role("Policy Research Assistant"),
            role("Audit Associate"),
            role("Trust and Safety Analyst"),
        ],
    ),
    SectorOption(
        value="sales_marketing_customer",
        label="Sales / Marketing / Customer Success",
        description="Sales, partnerships, growth, customer success, support, community, and market communication.",
        roles=[
            role("Sales Development Representative"),
            role("Account Manager"),
            role("Customer Success Manager"),
            role("Marketing Coordinator"),
            role("Growth Marketing Analyst"),
            role("Product Marketing Associate"),
            role("Business Development Representative"),
            role("Customer Support Specialist"),
            role("Market Research Analyst"),
            role("Community Manager"),
        ],
    ),
    SectorOption(
        value="finance_accounting_real_estate",
        label="Finance / Accounting / Real Estate",
        description="Accounting, financial planning, banking, insurance, real estate, and investment support.",
        roles=[
            role("Financial Analyst"),
            role("Accountant"),
            role("Bookkeeper"),
            role("Loan Officer"),
            role("Insurance Claims Analyst"),
            role("Real Estate Analyst"),
            role("Portfolio Analyst"),
            role("Tax Associate"),
            role("Budget Analyst"),
            role("Procurement Analyst"),
        ],
    ),
    SectorOption(
        value="science_engineering_environment",
        label="Science / Engineering / Technology",
        description="Scientific research, engineering, environmental analysis, data, software, robotics, and AI systems.",
        roles=[
            role("Research Assistant"),
            role("Lab Technician"),
            role("Environmental Analyst"),
            role("Mechanical Engineer"),
            role("Civil Engineering Technician"),
            role("Data Analyst"),
            role("Software Engineer"),
            role("Quality Engineer"),
            role("Robotics Engineer"),
            role("AI Engineer"),
        ],
    ),
]


SECTOR_REQUIREMENTS = {
    "business_operations": ["process mapping", "spreadsheet modeling", "stakeholder communication", "project tracking"],
    "healthcare_wellness": ["patient privacy", "healthcare workflows", "documentation accuracy", "service coordination"],
    "education_training": ["instructional planning", "learner support", "assessment design", "clear communication"],
    "skilled_trades_construction": ["safety practices", "technical documentation", "field coordination", "quality checks"],
    "public_service_government": ["policy research", "public communication", "compliance awareness", "program documentation"],
    "arts_media_design": ["portfolio quality", "audience understanding", "visual communication", "creative production"],
    "law_policy_compliance": ["document review", "risk controls", "regulatory research", "attention to detail"],
    "sales_marketing_customer": ["customer discovery", "crm discipline", "communication", "metrics tracking"],
    "finance_accounting_real_estate": ["financial analysis", "data accuracy", "reporting", "regulatory awareness"],
    "science_engineering_environment": ["technical analysis", "experimentation", "documentation", "problem solving"],
}


ROLE_KEYWORD_REQUIREMENTS = {
    "ml": ["machine learning", "pytorch", "mlops", "cloud deployment", "statistics"],
    "machine learning": ["machine learning", "pytorch", "mlops", "cloud deployment", "statistics"],
    "analyst": ["analysis", "reporting", "data interpretation", "recommendation writing"],
    "engineer": ["technical problem solving", "system design", "testing", "implementation"],
    "designer": ["user needs", "prototyping", "portfolio evidence", "design critique"],
    "coordinator": ["scheduling", "cross-functional communication", "documentation", "follow-through"],
    "manager": ["prioritization", "team coordination", "metrics ownership", "decision making"],
    "assistant": ["administrative accuracy", "research support", "communication", "organization"],
    "technician": ["hands-on troubleshooting", "standard procedures", "equipment/tool familiarity", "safety"],
    "teacher": ["lesson planning", "classroom communication", "assessment", "student support"],
    "tutor": ["subject explanation", "student support", "practice design", "progress tracking"],
    "writer": ["research", "clear writing", "editing", "audience adaptation"],
    "marketing": ["campaign execution", "market research", "content planning", "performance metrics"],
    "sales": ["prospecting", "discovery calls", "crm hygiene", "objection handling"],
    "research": ["literature review", "experimental design", "documentation", "analysis"],
    "data": ["sql", "data cleaning", "dashboarding", "statistical reasoning"],
    "software": ["programming", "api design", "testing", "debugging"],
    "ai": ["machine learning fundamentals", "model evaluation", "prompting", "applied AI workflows"],
}


SpecializationTemplate = tuple[str, str, str]


GENERIC_ROLE_KEYS = {
    "analyst",
    "assistant",
    "coordinator",
    "designer",
    "engineer",
    "manager",
    "specialist",
    "technician",
}


ROLE_SPECIALIZATION_RULES: dict[str, list[SpecializationTemplate]] = {
    "operations": [
        ("workflow_optimization", "Workflow Optimization", "Improve throughput, handoffs, bottlenecks, and operating rhythms."),
        ("operations_reporting", "Operations Reporting", "Use dashboards and recurring metrics to guide operational decisions."),
        ("vendor_process_coordination", "Vendor / Process Coordination", "Coordinate people, vendors, timelines, documentation, and service quality."),
    ],
    "operations analyst": [
        ("capacity_service_analysis", "Capacity / Service Analysis", "Analyze workload, capacity, service levels, and operating constraints."),
        ("operations_kpi_design", "Operations KPI Design", "Define useful measures for throughput, quality, cost, timeliness, and reliability."),
        ("root_cause_recommendations", "Root-Cause Recommendations", "Investigate operating problems and turn findings into measurable recommendations."),
    ],
    "operations manager": [
        ("service_delivery_management", "Service Delivery Management", "Lead daily execution, escalations, quality, and customer or internal service outcomes."),
        ("capacity_resource_planning", "Capacity / Resource Planning", "Align staffing, vendors, schedules, and resources with demand."),
        ("operational_excellence", "Operational Excellence", "Establish standard work, performance reviews, and sustained improvement systems."),
    ],
    "process improvement": [
        ("process_mapping", "Process Mapping", "Document current-state workflows, handoffs, delays, and control points."),
        ("lean_continuous_improvement", "Lean / Continuous Improvement", "Reduce waste and variation through measurable improvement cycles."),
        ("change_adoption", "Change Adoption", "Turn process changes into standard work, training, and sustained team adoption."),
    ],
    "business analyst": [
        ("requirements_analysis", "Requirements Analysis", "Translate stakeholder needs into clear requirements, workflows, and acceptance criteria."),
        ("business_intelligence", "Business Intelligence", "Build dashboards, reports, and insight summaries for business decisions."),
        ("process_modeling", "Process Modeling", "Map current and future-state workflows and identify measurable improvements."),
    ],
    "analyst": [
        ("analysis_reporting", "Analysis / Reporting", "Analyze information, create reports, explain patterns, and recommend next steps."),
        ("data_decision_support", "Data-Driven Decision Support", "Use metrics, spreadsheets, dashboards, or research to support decisions."),
        ("insight_communication", "Insight Communication", "Translate findings into clear summaries, visuals, and recommendations."),
    ],
    "engineer": [
        ("technical_implementation", "Technical Implementation", "Build, test, troubleshoot, and improve technical systems or products."),
        ("systems_design", "Systems Design", "Design reliable processes, components, architecture, and tradeoff-aware solutions."),
        ("validation_testing", "Validation / Testing", "Verify quality, performance, safety, and requirements through structured testing."),
    ],
    "coordinator": [
        ("coordination_operations", "Coordination Operations", "Coordinate schedules, tasks, documentation, stakeholders, and follow-through."),
        ("service_delivery", "Service Delivery", "Support reliable delivery of programs, services, events, or customer workflows."),
        ("communication_tracking", "Communication / Tracking", "Keep updates, records, handoffs, and action items clear and current."),
    ],
    "manager": [
        ("team_program_leadership", "Team / Program Leadership", "Lead priorities, people, execution, meetings, and accountability systems."),
        ("performance_management", "Performance Management", "Track goals, metrics, risks, outcomes, and improvement actions."),
        ("operational_planning", "Operational Planning", "Plan resources, timelines, budgets, capacity, and delivery constraints."),
    ],
    "assistant": [
        ("administrative_support", "Administrative Support", "Handle scheduling, records, correspondence, documentation, and request tracking."),
        ("research_documentation", "Research / Documentation", "Gather information, prepare summaries, organize files, and maintain accuracy."),
        ("stakeholder_service", "Stakeholder Service", "Support clients, executives, teams, students, or patients with clear communication."),
    ],
    "specialist": [
        ("domain_operations", "Domain Operations", "Develop specialized knowledge and execute the workflows central to the role."),
        ("quality_compliance_support", "Quality / Compliance Support", "Maintain standards, records, checks, and improvement evidence."),
        ("case_problem_solving", "Case / Problem Solving", "Investigate cases, resolve issues, and document practical recommendations."),
    ],
    "technician": [
        ("hands_on_service", "Hands-On Service", "Perform practical setup, inspection, troubleshooting, maintenance, or support tasks."),
        ("technical_documentation", "Technical Documentation", "Record procedures, findings, issues, repairs, and quality checks accurately."),
        ("safety_procedures", "Safety Procedures", "Apply safety practices, equipment protocols, and standard operating procedures."),
    ],
    "designer": [
        ("design_execution", "Design Execution", "Create polished visual, product, learning, or experience artifacts."),
        ("user_audience_research", "User / Audience Research", "Understand user needs, constraints, feedback, and context."),
        ("portfolio_case_studies", "Portfolio Case Studies", "Document process, decisions, iterations, and results in a strong portfolio."),
    ],
    "project": [
        ("project_delivery", "Project Delivery", "Coordinate scope, timelines, risks, owners, and execution checkpoints."),
        ("stakeholder_coordination", "Stakeholder Coordination", "Keep teams aligned through communication, documentation, and escalation paths."),
        ("project_controls", "Project Controls", "Track schedules, budgets, risks, and delivery health."),
    ],
    "program": [
        ("program_operations", "Program Operations", "Run repeatable program systems, reporting cadences, and stakeholder rituals."),
        ("portfolio_coordination", "Portfolio Coordination", "Coordinate multiple workstreams, dependencies, metrics, and outcomes."),
        ("change_management", "Change Management", "Support adoption, training, communications, and rollout planning."),
    ],
    "supply chain": [
        ("inventory_planning", "Inventory Planning", "Manage inventory signals, replenishment, demand, and service constraints."),
        ("logistics_coordination", "Logistics Coordination", "Coordinate shipping, vendors, routing, and exception handling."),
        ("supplier_performance", "Supplier Performance", "Track supplier quality, lead times, costs, and reliability."),
    ],
    "human resources": [
        ("talent_operations", "Talent Operations", "Support hiring, onboarding, employee records, and people-process workflows."),
        ("employee_programs", "Employee Programs", "Coordinate training, engagement, performance cycles, and internal communications."),
        ("hr_compliance", "HR Compliance", "Maintain accurate records, policy adherence, and sensitive employee documentation."),
    ],
    "executive assistant": [
        ("executive_operations", "Executive Operations", "Manage scheduling, prioritization, follow-ups, and executive workflow systems."),
        ("meeting_communications", "Meeting / Communications Support", "Prepare agendas, notes, correspondence, and action tracking."),
        ("administrative_coordination", "Administrative Coordination", "Coordinate logistics, vendors, documents, and confidential requests."),
    ],
    "management consultant": [
        ("strategy_analysis", "Strategy Analysis", "Frame ambiguous business problems and produce evidence-backed recommendations."),
        ("operating_model_design", "Operating Model Design", "Design processes, roles, governance, and performance systems."),
        ("client_delivery", "Client Delivery", "Manage client communications, analysis workstreams, and presentation-ready outputs."),
    ],
    "clinical research": [
        ("study_coordination", "Study Coordination", "Coordinate study visits, documentation, participants, and research timelines."),
        ("clinical_data_quality", "Clinical Data Quality", "Maintain accurate clinical data, source documents, and audit-ready records."),
        ("regulatory_documentation", "Regulatory Documentation", "Support consent, protocol, IRB, and compliance documentation workflows."),
    ],
    "healthcare administrator": [
        ("clinic_operations", "Clinic Operations", "Improve scheduling, staffing, patient flow, and service delivery workflows."),
        ("healthcare_reporting", "Healthcare Reporting", "Track operational, financial, quality, and patient-service metrics."),
        ("healthcare_compliance", "Healthcare Compliance", "Support policies, records, privacy, and regulatory readiness."),
    ],
    "patient": [
        ("patient_navigation", "Patient Navigation", "Coordinate appointments, referrals, resources, and patient communication."),
        ("care_coordination", "Care Coordination", "Support continuity between care teams, services, and documentation."),
        ("patient_experience", "Patient Experience", "Improve access, communication, service recovery, and satisfaction."),
    ],
    "medical assistant": [
        ("clinical_support", "Clinical Support", "Support vitals, rooming, documentation, and clinical workflows."),
        ("medical_records", "Medical Records", "Maintain accurate health records, forms, and privacy-sensitive documentation."),
        ("patient_service", "Patient Service", "Coordinate patient communication, scheduling, and front/back-office support."),
    ],
    "public health": [
        ("population_health_analysis", "Population Health Analysis", "Analyze health trends, needs, outcomes, and intervention opportunities."),
        ("community_health_programs", "Community Health Programs", "Coordinate outreach, education, resources, and program delivery."),
        ("health_policy_evaluation", "Health Policy / Evaluation", "Evaluate programs, policies, and public health evidence."),
    ],
    "health educator": [
        ("health_curriculum", "Health Curriculum", "Design clear health education materials, workshops, and learning outcomes."),
        ("community_outreach", "Community Outreach", "Deliver accessible health messaging through community partnerships."),
        ("behavior_change_support", "Behavior Change Support", "Support sustainable health behavior through coaching and resources."),
    ],
    "behavioral health": [
        ("behavioral_support", "Behavioral Support", "Support care plans, patient communication, de-escalation, and documentation."),
        ("case_documentation", "Case Documentation", "Maintain accurate behavioral health notes, records, and service tracking."),
        ("care_team_coordination", "Care Team Coordination", "Coordinate with clinicians, families, and support services."),
    ],
    "pharmacy": [
        ("medication_operations", "Medication Operations", "Support dispensing workflows, inventory, accuracy checks, and patient service."),
        ("pharmacy_records", "Pharmacy Records", "Maintain prescription, insurance, inventory, and compliance documentation."),
        ("patient_medication_support", "Patient Medication Support", "Communicate medication instructions, access issues, and refill workflows."),
    ],
    "wellness": [
        ("wellness_program_design", "Wellness Program Design", "Design wellness initiatives, resources, events, and participation workflows."),
        ("participant_engagement", "Participant Engagement", "Support adoption through communication, coaching, and feedback loops."),
        ("wellness_metrics", "Wellness Metrics", "Measure participation, outcomes, satisfaction, and program improvement."),
    ],
    "health information specialist": [
        ("health_information_management", "Health Information Management", "Organize accurate clinical information across records, coding, and care workflows."),
        ("health_data_quality", "Health Data Quality", "Validate completeness, consistency, and appropriate use of health data."),
        ("privacy_release_records", "Privacy / Release of Records", "Apply privacy rules and authorization procedures to health-information requests."),
    ],
    "teacher": [
        ("classroom_instruction", "Classroom Instruction", "Plan lessons, facilitate learning, assess progress, and support students."),
        ("curriculum_planning", "Curriculum Planning", "Create standards-aligned units, activities, materials, and assessments."),
        ("student_support", "Student Support", "Differentiate support for individual needs, behavior, and academic growth."),
    ],
    "tutor": [
        ("one_on_one_instruction", "One-on-One Instruction", "Explain concepts, diagnose gaps, and adapt practice for individual learners."),
        ("study_plan_design", "Study Plan Design", "Build structured learning plans, practice sets, and progress checkpoints."),
        ("academic_coaching", "Academic Coaching", "Support motivation, habits, confidence, and independent learning."),
    ],
    "instructional designer": [
        ("learning_experience_design", "Learning Experience Design", "Design learner-centered modules, activities, assessments, and materials."),
        ("elearning_development", "E-Learning Development", "Create digital learning assets, courses, and interactive training experiences."),
        ("training_evaluation", "Training Evaluation", "Measure learning outcomes, feedback, transfer, and improvement opportunities."),
    ],
    "learning experience designer": [
        ("learner_research", "Learner Research", "Study learner goals, contexts, barriers, and feedback to shape effective experiences."),
        ("learning_journey_design", "Learning Journey Design", "Sequence instruction, practice, feedback, and support across a complete learning journey."),
        ("learning_prototyping", "Learning Prototyping", "Prototype and test activities, interfaces, and learning materials with users."),
    ],
    "advisor": [
        ("student_advising", "Student Advising", "Guide students through plans, resources, requirements, and next steps."),
        ("case_management", "Case Management", "Track student needs, interventions, referrals, and outcomes."),
        ("academic_success_programs", "Academic Success Programs", "Coordinate retention, onboarding, coaching, and support initiatives."),
    ],
    "training": [
        ("training_delivery", "Training Delivery", "Facilitate workshops, onboarding, skill sessions, and learner support."),
        ("training_operations", "Training Operations", "Coordinate schedules, materials, attendance, completion, and reporting."),
        ("enablement_content", "Enablement Content", "Create playbooks, guides, exercises, and job aids."),
    ],
    "corporate trainer": [
        ("facilitation_delivery", "Facilitation / Delivery", "Lead practical employee learning through workshops, demonstrations, and coached practice."),
        ("workplace_enablement", "Workplace Enablement", "Create job aids, onboarding paths, and performance support tied to business needs."),
        ("training_measurement", "Training Measurement", "Evaluate participation, skill transfer, behavior change, and workplace outcomes."),
    ],
    "curriculum": [
        ("curriculum_development", "Curriculum Development", "Build learning sequences, objectives, materials, and assessments."),
        ("assessment_alignment", "Assessment Alignment", "Align exams, rubrics, projects, and outcomes."),
        ("instructional_materials", "Instructional Materials", "Create clear lessons, worksheets, slides, and digital resources."),
    ],
    "coach": [
        ("coaching_programs", "Coaching Programs", "Support learners or clients through goals, habits, accountability, and progress."),
        ("success_planning", "Success Planning", "Create action plans, milestones, resources, and follow-up systems."),
        ("learner_engagement", "Learner Engagement", "Improve participation, confidence, retention, and feedback loops."),
    ],
    "electrician": [
        ("electrical_installation", "Electrical Installation", "Support wiring, circuits, panels, fixtures, and code-aware installation workflows."),
        ("electrical_troubleshooting", "Electrical Troubleshooting", "Diagnose faults, test systems, and document repairs safely."),
        ("jobsite_safety", "Jobsite Safety", "Apply safety procedures, tools, PPE, and field documentation."),
    ],
    "hvac": [
        ("hvac_diagnostics", "HVAC Diagnostics", "Troubleshoot heating, cooling, airflow, controls, and performance issues."),
        ("preventive_maintenance", "Preventive Maintenance", "Perform inspections, tune-ups, documentation, and service planning."),
        ("customer_field_service", "Customer Field Service", "Communicate service findings, options, and next steps clearly."),
    ],
    "construction": [
        ("construction_coordination", "Construction Coordination", "Coordinate schedules, crews, materials, RFIs, and site communication."),
        ("site_documentation", "Site Documentation", "Maintain drawings, logs, safety records, punch lists, and progress updates."),
        ("cost_schedule_tracking", "Cost / Schedule Tracking", "Track budgets, timelines, change orders, and delivery risks."),
    ],
    "manufacturing": [
        ("production_operations", "Production Operations", "Support production flow, throughput, equipment use, and work instructions."),
        ("manufacturing_quality", "Manufacturing Quality", "Inspect outputs, track defects, and improve repeatability."),
        ("continuous_improvement", "Continuous Improvement", "Use lean methods, root-cause analysis, and operational metrics."),
    ],
    "quality control": [
        ("inspection_testing", "Inspection / Testing", "Inspect products or processes against standards and document results."),
        ("defect_analysis", "Defect Analysis", "Analyze defects, root causes, trends, and corrective actions."),
        ("quality_systems", "Quality Systems", "Maintain procedures, audit trails, and quality documentation."),
    ],
    "field service": [
        ("field_diagnostics", "Field Diagnostics", "Troubleshoot customer or site issues with structured investigation."),
        ("service_documentation", "Service Documentation", "Record work performed, findings, parts, and follow-up actions."),
        ("customer_technical_support", "Customer Technical Support", "Explain technical issues and service options to customers."),
    ],
    "facilities": [
        ("facilities_operations", "Facilities Operations", "Coordinate maintenance, vendors, work orders, and building services."),
        ("preventive_maintenance_planning", "Preventive Maintenance Planning", "Plan inspections, repairs, schedules, and asset upkeep."),
        ("safety_compliance", "Safety / Compliance", "Support inspections, incident prevention, documentation, and standards."),
    ],
    "cnc": [
        ("machine_setup", "Machine Setup", "Set up tooling, programs, materials, and machine parameters."),
        ("precision_quality", "Precision Quality", "Measure tolerances, inspect parts, and document quality checks."),
        ("production_troubleshooting", "Production Troubleshooting", "Resolve machine, tooling, material, and process issues."),
    ],
    "safety": [
        ("safety_programs", "Safety Programs", "Coordinate training, inspections, hazard controls, and incident prevention."),
        ("incident_documentation", "Incident Documentation", "Document incidents, corrective actions, audits, and compliance evidence."),
        ("risk_assessment", "Risk Assessment", "Identify hazards, evaluate risk, and recommend practical controls."),
    ],
    "maintenance planner": [
        ("preventive_maintenance_strategy", "Preventive Maintenance Strategy", "Build preventive and predictive maintenance plans around asset criticality."),
        ("work_planning_scheduling", "Work Planning / Scheduling", "Define job scope, labor, parts, permits, and coordinated maintenance windows."),
        ("reliability_asset_history", "Reliability / Asset History", "Use failure history and work-order data to improve uptime and maintenance decisions."),
    ],
    "policy": [
        ("policy_research", "Policy Research", "Research laws, programs, stakeholders, evidence, and policy alternatives."),
        ("policy_evaluation", "Policy Evaluation", "Assess outcomes, tradeoffs, implementation, and public impact."),
        ("briefing_writing", "Briefing Writing", "Write concise memos, summaries, recommendations, and stakeholder briefings."),
    ],
    "public administration analyst": [
        ("government_program_analysis", "Government Program Analysis", "Analyze public-service operations, outcomes, constraints, and improvement options."),
        ("public_budget_performance", "Public Budget / Performance", "Connect budgets, service measures, and performance reporting for public decisions."),
        ("administrative_policy_implementation", "Administrative Policy Implementation", "Translate statutes and policy into procedures, controls, and service delivery."),
    ],
    "city planner": [
        ("urban_planning", "Urban Planning", "Support land use, transportation, housing, and community planning work."),
        ("community_engagement", "Community Engagement", "Collect input, facilitate outreach, and translate public feedback."),
        ("planning_analysis", "Planning Analysis", "Analyze maps, codes, demographics, and project impacts."),
    ],
    "emergency": [
        ("emergency_planning", "Emergency Planning", "Build preparedness plans, response protocols, exercises, and resource maps."),
        ("incident_coordination", "Incident Coordination", "Coordinate communications, logistics, documentation, and response support."),
        ("risk_resilience", "Risk / Resilience", "Assess hazards, vulnerabilities, continuity needs, and mitigation options."),
    ],
    "outreach": [
        ("community_partnerships", "Community Partnerships", "Build relationships, events, resources, and trusted communication channels."),
        ("public_communications", "Public Communications", "Create clear messages, materials, and updates for community audiences."),
        ("program_engagement", "Program Engagement", "Increase participation, feedback, retention, and service access."),
    ],
    "nonprofit": [
        ("nonprofit_programs", "Nonprofit Programs", "Coordinate services, volunteers, partners, outcomes, and reporting."),
        ("funding_reporting", "Funding / Reporting", "Support grants, donor reporting, budgets, and impact narratives."),
        ("community_services", "Community Services", "Deliver accessible resources, referrals, and client-centered support."),
    ],
    "case manager": [
        ("client_assessment", "Client Assessment", "Assess needs, goals, risks, resources, and service eligibility."),
        ("service_coordination", "Service Coordination", "Coordinate referrals, follow-ups, records, and support plans."),
        ("case_documentation", "Case Documentation", "Maintain accurate notes, compliance records, and progress tracking."),
    ],
    "grant": [
        ("grant_research", "Grant Research", "Find funders, requirements, priorities, and fit with program goals."),
        ("proposal_writing", "Proposal Writing", "Write narratives, budgets, outcomes, and supporting documentation."),
        ("grant_reporting", "Grant Reporting", "Track deliverables, metrics, compliance, and funder updates."),
    ],
    "legislative": [
        ("constituent_services", "Constituent Services", "Support casework, communications, records, and public responsiveness."),
        ("legislative_research", "Legislative Research", "Research bills, issues, stakeholders, and policy implications."),
        ("office_operations", "Office Operations", "Coordinate schedules, briefings, correspondence, and documentation."),
    ],
    "graphic": [
        ("visual_identity", "Visual Identity", "Design brand systems, layouts, typography, and reusable visual assets."),
        ("marketing_design", "Marketing Design", "Create campaign assets, social visuals, ads, and collateral."),
        ("portfolio_production", "Portfolio Production", "Build polished case studies, process artifacts, and presentation-ready work."),
    ],
    "digital marketing designer": [
        ("campaign_creative", "Campaign Creative", "Design channel-ready campaign assets aligned to audience, offer, and conversion goals."),
        ("conversion_design", "Conversion Design", "Improve landing pages, email, ads, and calls to action through structured testing."),
        ("creative_performance", "Creative Performance", "Use engagement and conversion data to iterate visual concepts and formats."),
    ],
    "ux": [
        ("user_research", "User Research", "Study user needs, behaviors, journeys, pain points, and usability."),
        ("interaction_design", "Interaction Design", "Design flows, wireframes, prototypes, and interaction patterns."),
        ("usability_testing", "Usability Testing", "Plan tests, analyze feedback, and iterate designs."),
    ],
    "content": [
        ("content_strategy", "Content Strategy", "Plan messaging, information architecture, editorial systems, and audience journeys."),
        ("content_operations", "Content Operations", "Manage calendars, workflows, publishing, governance, and performance."),
        ("editorial_analytics", "Editorial Analytics", "Use performance data to improve topics, channels, and content quality."),
    ],
    "video": [
        ("video_production", "Video Production", "Plan shoots, capture footage, manage production, and coordinate assets."),
        ("post_production", "Post-Production", "Edit, sequence, caption, polish, and export finished video work."),
        ("story_development", "Story Development", "Shape scripts, storyboards, interviews, and narrative structure."),
    ],
    "social media": [
        ("social_strategy", "Social Strategy", "Plan channels, voice, calendars, campaigns, and community goals."),
        ("community_engagement", "Community Engagement", "Respond to audiences, moderate discussion, and build participation."),
        ("social_analytics", "Social Analytics", "Track reach, engagement, conversion, and content performance."),
    ],
    "copywriter": [
        ("conversion_copy", "Conversion Copy", "Write persuasive copy for pages, ads, emails, and product flows."),
        ("brand_voice", "Brand Voice", "Develop consistent tone, messaging, and editorial guidelines."),
        ("content_research", "Content Research", "Research audiences, claims, examples, and competitive positioning."),
    ],
    "brand": [
        ("brand_positioning", "Brand Positioning", "Define audience, differentiation, messaging, and market narrative."),
        ("campaign_strategy", "Campaign Strategy", "Plan campaigns, creative briefs, channels, and performance goals."),
        ("market_insight", "Market Insight", "Analyze customers, competitors, trends, and positioning opportunities."),
    ],
    "product designer": [
        ("product_discovery", "Product Discovery", "Understand user needs, product constraints, and opportunity areas."),
        ("interface_design", "Interface Design", "Create accessible UI flows, components, prototypes, and design specs."),
        ("design_systems", "Design Systems", "Maintain components, tokens, patterns, and consistency."),
    ],
    "game": [
        ("game_systems_design", "Game Systems Design", "Design mechanics, progression, economies, rules, and player loops."),
        ("level_experience_design", "Level / Experience Design", "Shape levels, pacing, challenge, feedback, and playtesting."),
        ("interactive_prototyping", "Interactive Prototyping", "Prototype gameplay systems and iterate from player feedback."),
    ],
    "paralegal": [
        ("legal_research", "Legal Research", "Research statutes, cases, regulations, and supporting documents."),
        ("case_file_management", "Case File Management", "Organize pleadings, discovery, timelines, evidence, and filings."),
        ("litigation_support", "Litigation Support", "Support deposition prep, discovery, exhibits, and attorney workflows."),
    ],
    "legal assistant": [
        ("legal_administration", "Legal Administration", "Coordinate calendars, filings, correspondence, and client records."),
        ("document_preparation", "Document Preparation", "Prepare forms, letters, contracts, and case documents accurately."),
        ("client_communication", "Client Communication", "Support intake, updates, scheduling, and service professionalism."),
    ],
    "compliance": [
        ("regulatory_compliance", "Regulatory Compliance", "Interpret requirements, maintain controls, and document evidence."),
        ("compliance_monitoring", "Compliance Monitoring", "Track adherence, exceptions, remediation, and reporting."),
        ("audit_readiness", "Audit Readiness", "Prepare documentation, samples, controls, and corrective actions."),
    ],
    "privacy": [
        ("privacy_operations", "Privacy Operations", "Support privacy requests, records, policies, and data-handling workflows."),
        ("data_governance", "Data Governance", "Maintain data inventories, controls, retention, and accountability."),
        ("privacy_risk_assessment", "Privacy Risk Assessment", "Assess data use, vendors, risks, and mitigation plans."),
    ],
    "contract": [
        ("contract_lifecycle", "Contract Lifecycle", "Track drafting, review, approvals, obligations, renewals, and records."),
        ("vendor_contracts", "Vendor Contracts", "Coordinate vendor terms, compliance, documentation, and stakeholder reviews."),
        ("contract_data_management", "Contract Data Management", "Maintain clause data, obligations, metadata, and reporting."),
    ],
    "risk": [
        ("risk_assessment", "Risk Assessment", "Identify risks, controls, impact, likelihood, and mitigation options."),
        ("control_testing", "Control Testing", "Test controls, document evidence, and track remediation."),
        ("risk_reporting", "Risk Reporting", "Summarize risk posture, trends, actions, and decision points."),
    ],
    "regulatory": [
        ("regulatory_submissions", "Regulatory Submissions", "Prepare filings, evidence, documentation, and response packages."),
        ("regulatory_research", "Regulatory Research", "Monitor requirements, guidance, changes, and implications."),
        ("quality_compliance", "Quality Compliance", "Maintain procedures, records, audits, and corrective actions."),
    ],
    "audit": [
        ("audit_testing", "Audit Testing", "Test controls, samples, transactions, and documentation."),
        ("audit_documentation", "Audit Documentation", "Prepare workpapers, findings, evidence, and issue tracking."),
        ("process_controls", "Process Controls", "Evaluate risks, controls, gaps, and improvement opportunities."),
    ],
    "trust and safety": [
        ("policy_enforcement", "Policy Enforcement", "Review cases, apply policies, document decisions, and escalate risk."),
        ("safety_operations", "Safety Operations", "Improve queues, workflows, metrics, and response quality."),
        ("abuse_investigation", "Abuse Investigation", "Investigate harmful behavior, patterns, evidence, and mitigation steps."),
    ],
    "sales": [
        ("prospecting_pipeline", "Prospecting / Pipeline", "Identify leads, qualify accounts, manage outreach, and track pipeline."),
        ("discovery_consulting", "Discovery / Consulting", "Understand customer needs, objections, urgency, and fit."),
        ("crm_sales_operations", "CRM / Sales Operations", "Maintain CRM hygiene, follow-ups, forecasting, and sales metrics."),
    ],
    "account manager": [
        ("account_growth", "Account Growth", "Grow relationships, identify opportunities, and coordinate renewals."),
        ("client_relationships", "Client Relationships", "Manage stakeholder communication, expectations, and service quality."),
        ("retention_strategy", "Retention Strategy", "Track health, risks, outcomes, and renewal readiness."),
    ],
    "customer success": [
        ("customer_onboarding", "Customer Onboarding", "Guide implementation, setup, training, and early success milestones."),
        ("customer_health", "Customer Health", "Track usage, risks, adoption, feedback, and retention signals."),
        ("renewal_expansion", "Renewal / Expansion", "Support renewals, value reviews, expansion opportunities, and escalations."),
    ],
    "marketing coordinator": [
        ("campaign_operations", "Campaign Operations", "Coordinate timelines, assets, channels, approvals, and launches."),
        ("content_calendar", "Content Calendar", "Manage editorial planning, publishing workflows, and channel consistency."),
        ("marketing_reporting", "Marketing Reporting", "Track campaign performance, engagement, leads, and lessons learned."),
    ],
    "growth": [
        ("growth_experimentation", "Growth Experimentation", "Design tests, track funnels, analyze results, and iterate channels."),
        ("acquisition_analytics", "Acquisition Analytics", "Measure traffic, conversion, attribution, and channel quality."),
        ("conversion_optimization", "Conversion Optimization", "Improve landing pages, onboarding, offers, and funnel drop-off."),
    ],
    "product marketing": [
        ("positioning_messaging", "Positioning / Messaging", "Define audience, use cases, differentiation, and launch narratives."),
        ("go_to_market", "Go-to-Market", "Plan launches, sales enablement, channels, and adoption metrics."),
        ("competitive_research", "Competitive Research", "Analyze competitors, market needs, objections, and positioning gaps."),
    ],
    "business development": [
        ("partnership_development", "Partnership Development", "Identify partners, build outreach, qualify fit, and coordinate next steps."),
        ("market_expansion", "Market Expansion", "Research segments, opportunities, channels, and new revenue paths."),
        ("deal_coordination", "Deal Coordination", "Support proposals, meetings, stakeholders, and pipeline movement."),
    ],
    "customer support": [
        ("support_operations", "Support Operations", "Resolve tickets, improve workflows, document issues, and track SLAs."),
        ("knowledge_base", "Knowledge Base", "Create help articles, macros, troubleshooting guides, and support content."),
        ("voice_of_customer", "Voice of Customer", "Synthesize feedback, issues, trends, and product/service improvements."),
    ],
    "market research": [
        ("market_analysis", "Market Analysis", "Research customers, competitors, pricing, channels, and market trends."),
        ("survey_research", "Survey Research", "Design surveys, interviews, analysis, and insight reports."),
        ("insight_reporting", "Insight Reporting", "Translate findings into clear recommendations and decision briefs."),
    ],
    "community manager": [
        ("community_engagement", "Community Engagement", "Build participation, moderation, events, and member communication."),
        ("community_programs", "Community Programs", "Coordinate ambassador, events, support, and education programs."),
        ("community_insights", "Community Insights", "Track sentiment, feedback, growth, retention, and content needs."),
    ],
    "financial": [
        ("financial_modeling", "Financial Modeling", "Build forecasts, scenarios, valuations, budgets, and decision models."),
        ("performance_reporting", "Performance Reporting", "Analyze financial performance, variance, KPIs, and business drivers."),
        ("investment_analysis", "Investment Analysis", "Evaluate opportunities, risk, returns, and supporting assumptions."),
    ],
    "accountant": [
        ("general_ledger", "General Ledger", "Support entries, reconciliations, close, and account accuracy."),
        ("financial_reporting", "Financial Reporting", "Prepare reports, statements, schedules, and variance explanations."),
        ("accounting_controls", "Accounting Controls", "Maintain procedures, documentation, approvals, and audit readiness."),
    ],
    "bookkeeper": [
        ("transaction_recording", "Transaction Recording", "Maintain accurate income, expense, invoice, and payment records."),
        ("reconciliations", "Reconciliations", "Reconcile accounts, resolve discrepancies, and maintain clean books."),
        ("small_business_reporting", "Small Business Reporting", "Prepare simple reports, cash-flow views, and owner updates."),
    ],
    "loan": [
        ("loan_origination", "Loan Origination", "Support applications, documentation, eligibility, and borrower communication."),
        ("credit_review", "Credit Review", "Analyze borrower information, risk, debt, income, and collateral."),
        ("lending_compliance", "Lending Compliance", "Maintain records, disclosures, policies, and regulatory requirements."),
    ],
    "insurance": [
        ("claims_review", "Claims Review", "Review claims, documentation, coverage, liability, and payment recommendations."),
        ("case_investigation", "Case Investigation", "Gather evidence, communicate with parties, and document findings."),
        ("insurance_operations", "Insurance Operations", "Track workflows, compliance, service levels, and claim quality."),
    ],
    "real estate": [
        ("market_valuation", "Market / Valuation", "Analyze comps, rents, locations, cash flow, and valuation assumptions."),
        ("property_analysis", "Property Analysis", "Evaluate property performance, risks, costs, and investment fit."),
        ("real_estate_reporting", "Real Estate Reporting", "Create investment memos, dashboards, summaries, and portfolio updates."),
    ],
    "portfolio": [
        ("portfolio_reporting", "Portfolio Reporting", "Track holdings, performance, risk, allocation, and investment metrics."),
        ("investment_operations", "Investment Operations", "Support trades, records, reconciliations, and client reporting."),
        ("risk_return_analysis", "Risk / Return Analysis", "Analyze exposure, volatility, scenarios, and portfolio decisions."),
    ],
    "tax": [
        ("tax_preparation", "Tax Preparation", "Prepare returns, workpapers, schedules, and supporting documentation."),
        ("tax_research", "Tax Research", "Research rules, deductions, compliance issues, and filing requirements."),
        ("tax_client_service", "Tax Client Service", "Gather documents, answer questions, and communicate filing status."),
    ],
    "budget": [
        ("budget_planning", "Budget Planning", "Build budgets, forecasts, scenarios, and resource plans."),
        ("variance_analysis", "Variance Analysis", "Analyze actuals versus plan and explain drivers."),
        ("public_or_org_reporting", "Organizational Reporting", "Prepare budget summaries, dashboards, and decision memos."),
    ],
    "procurement": [
        ("supplier_sourcing", "Supplier Sourcing", "Research vendors, compare bids, and support purchasing decisions."),
        ("purchase_operations", "Purchase Operations", "Manage requisitions, POs, approvals, records, and delivery tracking."),
        ("spend_analysis", "Spend Analysis", "Analyze spend categories, savings opportunities, compliance, and vendor performance."),
    ],
    "research assistant": [
        ("experimental_support", "Experimental Support", "Support study design, data collection, lab/research workflows, and records."),
        ("literature_review", "Literature Review", "Summarize research, methods, evidence, and knowledge gaps."),
        ("research_data_management", "Research Data Management", "Organize datasets, notes, protocols, and reproducible analysis."),
    ],
    "lab": [
        ("lab_operations", "Lab Operations", "Support equipment, samples, protocols, documentation, and safety."),
        ("sample_testing", "Sample Testing", "Run procedures, record results, and maintain quality controls."),
        ("scientific_documentation", "Scientific Documentation", "Maintain lab notes, reports, SOPs, and reproducible records."),
    ],
    "environmental": [
        ("environmental_monitoring", "Environmental Monitoring", "Collect and analyze environmental data, samples, and observations."),
        ("sustainability_reporting", "Sustainability Reporting", "Track emissions, waste, compliance, and improvement metrics."),
        ("field_research", "Field Research", "Support inspections, site assessments, data collection, and documentation."),
    ],
    "mechanical": [
        ("mechanical_design", "Mechanical Design", "Design parts, assemblies, calculations, drawings, and test plans."),
        ("controls_systems", "Controls Systems", "Work with sensors, actuators, control logic, and system behavior."),
        ("product_testing", "Product Testing", "Plan tests, collect data, analyze failures, and improve reliability."),
    ],
    "civil": [
        ("civil_design_support", "Civil Design Support", "Support drawings, estimates, site data, and infrastructure documentation."),
        ("construction_inspection", "Construction Inspection", "Inspect work, document progress, track issues, and support compliance."),
        ("permitting_documentation", "Permitting Documentation", "Prepare applications, records, plans, and agency communication."),
    ],
    "data analyst": [
        ("data_cleaning", "Data Cleaning", "Prepare datasets, resolve quality issues, and document assumptions."),
        ("dashboard_reporting", "Dashboard / Reporting", "Build reports, dashboards, KPIs, and decision summaries."),
        ("statistical_analysis", "Statistical Analysis", "Analyze patterns, tests, uncertainty, and practical recommendations."),
    ],
    "software engineer": [
        ("backend_development", "Backend Development", "Build APIs, services, data models, integrations, and reliable workflows."),
        ("frontend_development", "Frontend Development", "Build usable interfaces, state flows, forms, and responsive UI."),
        ("software_quality", "Software Quality", "Write tests, debug issues, improve reliability, and maintain code quality."),
    ],
    "quality engineer": [
        ("quality_systems", "Quality Systems", "Design quality processes, metrics, audits, and corrective actions."),
        ("test_engineering", "Test Engineering", "Build test plans, fixtures, automation, and validation workflows."),
        ("root_cause_analysis", "Root Cause Analysis", "Investigate defects, failures, trends, and corrective actions."),
    ],
    "robotics": [
        ("robot_perception", "Robot Perception", "Work with sensors, computer vision, environment understanding, and detection."),
        ("navigation_controls", "Navigation / Controls", "Develop control, localization, planning, and motion workflows."),
        ("robot_simulation", "Robot Simulation", "Prototype robots, environments, tests, and deployment assumptions in simulation."),
    ],
    "ai engineer": [
        ("applied_ai_systems", "Applied AI Systems", "Integrate models into usable products, APIs, and workflows."),
        ("model_evaluation", "Model Evaluation", "Measure model behavior, quality, limitations, and failure modes."),
        ("ai_infrastructure", "AI Infrastructure", "Serve, monitor, optimize, and maintain AI systems."),
        ("llm_application_development", "LLM Application Development", "Build chat, retrieval, tool-use, and workflow applications around foundation models."),
        ("rag_knowledge_systems", "RAG / Knowledge Systems", "Connect models to documents, databases, search, and grounded citation workflows."),
        ("ai_agent_workflows", "AI Agent Workflows", "Design multi-step agent behavior, tool calling, traces, fallbacks, and verification loops."),
        ("prompt_context_engineering", "Prompt / Context Engineering", "Structure prompts, examples, context windows, and task instructions for reliable outputs."),
        ("multimodal_ai", "Multimodal AI", "Work with text, image, document, audio, or sensor inputs in AI-powered systems."),
        ("model_fine_tuning", "Model Fine-Tuning", "Adapt open or hosted models using supervised tuning, LoRA/PEFT, and evaluation sets."),
        ("responsible_ai_safety", "Responsible AI / Safety", "Test unsupported claims, privacy risks, bias, failure cases, and user-facing guardrails."),
    ],
}


SECTOR_SPECIALIZATION_RULES: dict[str, list[SpecializationTemplate]] = {
    "business_operations": [
        ("process_improvement", "Process Improvement", "Improve workflows, handoffs, throughput, and operational consistency."),
        ("operations_metrics", "Operations Metrics", "Track KPIs, service levels, performance, and improvement opportunities."),
        ("stakeholder_operations", "Stakeholder Operations", "Coordinate teams, vendors, documentation, and execution."),
    ],
    "healthcare_wellness": [
        ("care_coordination", "Care Coordination", "Coordinate patient services, documentation, referrals, and care workflows."),
        ("health_records_quality", "Health Records / Quality", "Maintain accurate records, privacy, quality checks, and service data."),
        ("health_program_delivery", "Health Program Delivery", "Support programs, outreach, education, and participant outcomes."),
    ],
    "education_training": [
        ("instructional_delivery", "Instructional Delivery", "Teach, facilitate, coach, and support learner progress."),
        ("learning_design", "Learning Design", "Design curriculum, training, activities, assessments, and learning materials."),
        ("student_success", "Student Success", "Support advising, retention, progress, confidence, and access to resources."),
    ],
    "skilled_trades_construction": [
        ("field_operations", "Field Operations", "Support jobsite/service work, work orders, schedules, and documentation."),
        ("technical_troubleshooting", "Technical Troubleshooting", "Diagnose, repair, inspect, and validate systems or equipment."),
        ("safety_quality", "Safety / Quality", "Apply safety practices, inspections, standards, and corrective actions."),
    ],
    "public_service_government": [
        ("public_programs", "Public Programs", "Deliver services, coordinate stakeholders, and document program outcomes."),
        ("policy_research", "Policy Research", "Research public issues, regulations, evidence, and recommendations."),
        ("community_engagement", "Community Engagement", "Communicate with communities, partners, agencies, and service users."),
    ],
    "arts_media_design": [
        ("creative_production", "Creative Production", "Produce visual, written, video, or interactive creative assets."),
        ("audience_strategy", "Audience Strategy", "Understand audience needs, channels, messaging, and engagement."),
        ("portfolio_development", "Portfolio Development", "Build polished case studies and representative creative work."),
    ],
    "law_policy_compliance": [
        ("legal_documentation", "Legal Documentation", "Prepare, review, organize, and maintain sensitive legal or policy documents."),
        ("risk_compliance", "Risk / Compliance", "Monitor controls, regulations, exceptions, and audit readiness."),
        ("research_briefing", "Research / Briefing", "Research issues and write concise summaries, memos, and recommendations."),
    ],
    "sales_marketing_customer": [
        ("revenue_growth", "Revenue Growth", "Support pipeline, campaigns, acquisition, conversion, and expansion."),
        ("customer_relationships", "Customer Relationships", "Manage onboarding, communication, support, and retention."),
        ("market_insights", "Market Insights", "Analyze customers, competitors, segments, and messaging opportunities."),
    ],
    "finance_accounting_real_estate": [
        ("financial_reporting", "Financial Reporting", "Prepare reports, reconciliations, forecasts, and decision summaries."),
        ("risk_controls", "Risk / Controls", "Maintain accuracy, compliance, review controls, and audit readiness."),
        ("investment_analysis", "Investment Analysis", "Analyze assets, returns, markets, scenarios, and tradeoffs."),
    ],
    "science_engineering_environment": [
        ("technical_analysis", "Technical Analysis", "Analyze systems, experiments, data, defects, and technical tradeoffs."),
        ("research_testing", "Research / Testing", "Run studies, tests, experiments, validation, and documentation."),
        ("systems_engineering", "Systems Engineering", "Design, build, troubleshoot, and improve technical systems."),
    ],
}


def provider_options(settings: Settings) -> ProviderOptionsResponse:
    systems = [
        IntelligentSystemOption(
            value="hybrid-gemini-first",
            label="Google API first",
            description="Try Google Gemini first, then OpenAI if configured, then the offline demo.",
            provider_mode="hybrid-gemini-first",
            configured=True,
        ),
        IntelligentSystemOption(
            value="gemini",
            label="Gemini",
            description="Google Gemini via the OpenAI-compatible API.",
            provider_mode="gemini",
            configured=bool(settings.gemini_api_key),
        ),
        IntelligentSystemOption(
            value="openai",
            label="ChatGPT / OpenAI",
            description="OpenAI Responses API.",
            provider_mode="openai",
            configured=bool(settings.openai_api_key),
        ),
        IntelligentSystemOption(
            value="qwen",
            label="Qwen3 4B Instruct",
            description="Local Hugging Face Transformers model: Qwen/Qwen3-4B-Instruct-2507.",
            provider_mode="qwen",
            configured=_has_qwen_dependencies(),
        ),
        IntelligentSystemOption(
            value="local",
            label="Multimodal + LoRA Adapters",
            description="Future local multimodal/MoLE service over HTTP.",
            provider_mode="local",
            configured=True,
        ),
        IntelligentSystemOption(
            value="fake",
            label="Offline Demo",
            description="Deterministic fake provider for demos and tests.",
            provider_mode="fake",
            configured=True,
        ),
    ]
    return ProviderOptionsResponse(
        default_provider_mode=settings.provider_mode,
        intelligent_systems=systems,
        sectors=SECTORS,
        specializations=[],
    )


def _has_qwen_dependencies() -> bool:
    return find_spec("transformers") is not None and find_spec("torch") is not None


def generate_specializations(sector: str, target_role: str) -> list[SelectOption]:
    role_text = target_role.lower()
    chosen = _rank_templates(sector, role_text)
    role_prefix = _slugify(target_role)
    limit = 10 if role_text == "ai engineer" else 4
    return [
        SelectOption(
            value=f"{role_prefix}__{template_id}",
            label=label,
            description=f"{description} Tailored to {target_role}.",
        )
        for template_id, label, description in chosen[:limit]
    ]


def requirements_for_goal(sector: str | None, target_role: str, specialization: str | None) -> list[str]:
    role_text = target_role.lower()
    requirements = list(_specialization_requirements(specialization or ""))
    for keyword, keyword_requirements in ROLE_KEYWORD_REQUIREMENTS.items():
        if keyword in role_text:
            requirements.extend(keyword_requirements)
    requirements.extend(SECTOR_REQUIREMENTS.get(sector or "", []))
    requirements.append("portfolio or experience evidence aligned to the selected role")
    return _dedupe(requirements)[:12]


def _rank_templates(sector: str, role_text: str) -> list[tuple[str, str, str]]:
    ranked: list[tuple[str, str, str]] = []
    exact_templates = ROLE_SPECIALIZATION_RULES.get(role_text, [])
    ranked.extend(exact_templates)

    matches = [
        (keyword, templates)
        for keyword, templates in ROLE_SPECIALIZATION_RULES.items()
        if keyword != role_text and keyword in role_text
    ]
    domain_matches = [match for match in matches if match[0] not in GENERIC_ROLE_KEYS]
    family_matches = [match for match in matches if match[0] in GENERIC_ROLE_KEYS]

    # Prefer the work domain over a broad title family. For example, clinical
    # research is more informative than coordinator when both match a role.
    for _, templates in sorted(domain_matches, key=lambda match: len(match[0]), reverse=True):
        ranked.extend(templates)
    ranked.extend(SECTOR_SPECIALIZATION_RULES.get(sector, []))
    for _, templates in family_matches:
        ranked.extend(templates)
    ranked.extend(
        [
            ("career_transition_story", "Career Transition Story", "Package transferable experience into a clear role-specific narrative."),
            ("portfolio_experience_evidence", "Portfolio / Experience Evidence", "Build or document proof that matches the selected role."),
        ]
    )
    return _dedupe_templates(ranked)


def _specialization_requirements(specialization: str) -> list[str]:
    if specialization == "ai_data":
        return ["python", "machine learning", "model evaluation", "statistics", "data preprocessing", "experimentation"]
    if specialization == "applied_ai":
        return ["llm", "model integration", "fastapi", "prompting", "evaluation", "user-facing AI workflows"]
    if specialization == "mlops":
        return ["docker", "model serving", "latency profiling", "monitoring", "deployment automation", "api reliability"]
    if specialization == "software":
        return ["api design", "testing", "sql", "system design", "authentication", "backend services"]
    if "capacity_service_analysis" in specialization:
        return ["capacity analysis", "service-level analysis", "spreadsheet modeling"]
    if "operations_kpi_design" in specialization:
        return ["kpi definition", "dashboard design", "metric governance"]
    if "root_cause_recommendations" in specialization:
        return ["root-cause analysis", "recommendation writing", "benefit measurement"]
    if "service_delivery_management" in specialization:
        return ["service operations", "escalation management", "quality metrics"]
    if "capacity_resource_planning" in specialization:
        return ["capacity planning", "resource allocation", "demand forecasting"]
    if "operational_excellence" in specialization:
        return ["standard work", "performance reviews", "continuous improvement"]
    if "process_mapping" in specialization or "lean_continuous_improvement" in specialization or "change_adoption" in specialization:
        return ["process mapping", "lean improvement", "change adoption"]
    if "health_information_management" in specialization or "health_data_quality" in specialization or "privacy_release_records" in specialization:
        return ["health information systems", "data quality", "patient privacy"]
    if "learner_research" in specialization or "learning_journey_design" in specialization or "learning_prototyping" in specialization:
        return ["learner research", "instructional sequencing", "prototype testing"]
    if "facilitation_delivery" in specialization or "workplace_enablement" in specialization or "training_measurement" in specialization:
        return ["facilitation", "performance support", "training evaluation"]
    if "preventive_maintenance_strategy" in specialization or "work_planning_scheduling" in specialization or "reliability_asset_history" in specialization:
        return ["maintenance planning", "asset reliability", "work-order analysis"]
    if "government_program_analysis" in specialization or "public_budget_performance" in specialization or "administrative_policy_implementation" in specialization:
        return ["public program analysis", "performance budgeting", "policy implementation"]
    if "campaign_creative" in specialization or "conversion_design" in specialization or "creative_performance" in specialization:
        return ["campaign design", "conversion testing", "creative performance analysis"]
    if "data_analytics" in specialization:
        return ["data analysis", "dashboarding", "metrics interpretation"]
    if "analysis_reporting" in specialization or "data_decision_support" in specialization or "insight_communication" in specialization:
        return ["analysis", "reporting", "recommendation writing"]
    if "operations_improvement" in specialization:
        return ["process improvement", "workflow mapping", "operational metrics"]
    if "customer_client_success" in specialization:
        return ["customer communication", "service recovery", "relationship management"]
    if "project_program_delivery" in specialization:
        return ["timeline management", "risk tracking", "stakeholder updates"]
    if "research_evaluation" in specialization:
        return ["research methods", "evidence synthesis", "evaluation criteria"]
    if "compliance_quality" in specialization:
        return ["quality control", "compliance documentation", "audit readiness"]
    if "technical_systems" in specialization:
        return ["technical troubleshooting", "systems thinking", "implementation testing"]
    if "technical_implementation" in specialization or "systems_design" in specialization or "validation_testing" in specialization:
        return ["technical implementation", "systems design", "validation testing"]
    if "creative_product" in specialization:
        return ["portfolio storytelling", "user feedback", "iteration"]
    if "design_execution" in specialization or "user_audience_research" in specialization or "portfolio_case_studies" in specialization:
        return ["design execution", "user research", "portfolio case studies"]
    if "people_training" in specialization:
        return ["training design", "coaching", "progress assessment"]
    if "field_service" in specialization:
        return ["field procedures", "safety", "service documentation"]
    if "coordination_operations" in specialization or "service_delivery" in specialization or "communication_tracking" in specialization:
        return ["coordination", "service delivery", "communication tracking"]
    if "team_program_leadership" in specialization or "performance_management" in specialization or "operational_planning" in specialization:
        return ["team coordination", "performance metrics", "operational planning"]
    if "administrative_support" in specialization or "research_documentation" in specialization or "stakeholder_service" in specialization:
        return ["administrative accuracy", "research documentation", "stakeholder communication"]
    if "domain_operations" in specialization or "quality_compliance_support" in specialization or "case_problem_solving" in specialization:
        return ["domain knowledge", "quality checks", "case problem solving"]
    if "hands_on_service" in specialization or "technical_documentation" in specialization or "safety_procedures" in specialization:
        return ["hands-on troubleshooting", "technical documentation", "safety procedures"]
    if "workflow_optimization" in specialization or "process_improvement" in specialization:
        return ["process mapping", "workflow improvement", "operational metrics"]
    if "operations_reporting" in specialization or "operations_metrics" in specialization:
        return ["spreadsheet analysis", "dashboarding", "kpi reporting"]
    if "coordination" in specialization or "stakeholder" in specialization:
        return ["stakeholder communication", "follow-through", "documentation"]
    if "requirements_analysis" in specialization or "process_modeling" in specialization:
        return ["requirements gathering", "workflow diagrams", "acceptance criteria"]
    if "business_intelligence" in specialization:
        return ["business intelligence", "dashboarding", "data interpretation"]
    if "project_delivery" in specialization or "program_operations" in specialization:
        return ["project planning", "risk tracking", "status reporting"]
    if "portfolio_coordination" in specialization or "project_controls" in specialization:
        return ["dependency tracking", "schedule management", "portfolio reporting"]
    if "change_management" in specialization:
        return ["change communications", "training support", "adoption tracking"]
    if "inventory" in specialization or "logistics" in specialization or "supplier" in specialization:
        return ["inventory tracking", "vendor coordination", "service levels"]
    if "talent" in specialization or "employee" in specialization or "hr_compliance" in specialization:
        return ["employee records", "onboarding coordination", "policy compliance"]
    if "executive" in specialization or "administrative" in specialization:
        return ["calendar management", "confidential communication", "action tracking"]
    if "strategy_analysis" in specialization or "operating_model" in specialization or "client_delivery" in specialization:
        return ["structured analysis", "recommendation writing", "client-ready presentations"]
    if "clinical" in specialization or "care_" in specialization or "patient" in specialization:
        return ["patient privacy", "healthcare documentation", "service coordination"]
    if "regulatory" in specialization or "audit" in specialization or "compliance" in specialization:
        return ["regulatory research", "compliance documentation", "audit readiness"]
    if "health_" in specialization or "population_health" in specialization:
        return ["health analytics", "program evaluation", "clear health communication"]
    if "pharmacy" in specialization or "medication" in specialization:
        return ["medication workflow accuracy", "inventory documentation", "patient communication"]
    if "classroom" in specialization or "curriculum" in specialization or "instructional" in specialization:
        return ["lesson planning", "assessment design", "learner support"]
    if "student" in specialization or "academic" in specialization or "coaching" in specialization:
        return ["student advising", "progress tracking", "resource coordination"]
    if "training" in specialization or "enablement" in specialization:
        return ["training delivery", "learning materials", "outcome measurement"]
    if "electrical" in specialization or "hvac" in specialization or "machine_setup" in specialization:
        return ["technical troubleshooting", "safety procedures", "standard work documentation"]
    if "construction" in specialization or "site_" in specialization or "cost_schedule" in specialization:
        return ["site documentation", "schedule tracking", "safety awareness"]
    if "manufacturing" in specialization or "production" in specialization or "quality" in specialization:
        return ["quality checks", "root-cause analysis", "continuous improvement"]
    if "field_" in specialization or "service_documentation" in specialization:
        return ["field diagnostics", "customer communication", "service documentation"]
    if "policy" in specialization or "briefing" in specialization or "legislative" in specialization:
        return ["policy research", "brief writing", "stakeholder analysis"]
    if "community" in specialization or "nonprofit" in specialization or "grant" in specialization:
        return ["community outreach", "program reporting", "resource coordination"]
    if "visual" in specialization or "design" in specialization or "creative" in specialization:
        return ["portfolio evidence", "user or audience research", "iterative critique"]
    if "video" in specialization or "story" in specialization or "copy" in specialization or "brand" in specialization:
        return ["content production", "audience adaptation", "editorial quality"]
    if "game" in specialization or "interactive" in specialization:
        return ["prototyping", "playtesting", "systems design"]
    if "legal" in specialization or "contract" in specialization:
        return ["document review", "attention to detail", "confidential records"]
    if "risk" in specialization or "control" in specialization or "privacy" in specialization:
        return ["risk assessment", "controls testing", "documentation accuracy"]
    if "sales" in specialization or "prospecting" in specialization or "account" in specialization:
        return ["crm discipline", "customer discovery", "pipeline tracking"]
    if "customer" in specialization or "support" in specialization:
        return ["customer communication", "issue resolution", "service metrics"]
    if "marketing" in specialization or "campaign" in specialization or "growth" in specialization:
        return ["campaign execution", "market research", "performance metrics"]
    if "market_" in specialization or "insight" in specialization:
        return ["market analysis", "survey research", "insight reporting"]
    if "financial" in specialization or "budget" in specialization or "investment" in specialization:
        return ["financial modeling", "variance analysis", "reporting accuracy"]
    if "accounting" in specialization or "ledger" in specialization or "reconciliations" in specialization:
        return ["account reconciliation", "financial reporting", "controls"]
    if "loan" in specialization or "credit" in specialization or "lending" in specialization:
        return ["credit review", "document collection", "lending compliance"]
    if "insurance" in specialization or "claims" in specialization:
        return ["claims review", "case investigation", "coverage documentation"]
    if "real_estate" in specialization or "property" in specialization or "valuation" in specialization:
        return ["market comps", "property analysis", "investment memo writing"]
    if "tax" in specialization:
        return ["tax preparation", "tax research", "client documentation"]
    if "procurement" in specialization or "supplier_sourcing" in specialization or "spend" in specialization:
        return ["supplier analysis", "purchase operations", "spend reporting"]
    if "research" in specialization or "experimental" in specialization or "literature" in specialization:
        return ["research methods", "data collection", "technical documentation"]
    if "lab" in specialization or "sample" in specialization:
        return ["lab procedures", "sample testing", "scientific documentation"]
    if "environmental" in specialization or "sustainability" in specialization:
        return ["environmental data", "field documentation", "sustainability reporting"]
    if "mechanical" in specialization or "controls" in specialization or "product_testing" in specialization:
        return ["mechanical systems", "test planning", "failure analysis"]
    if "civil" in specialization or "permitting" in specialization:
        return ["civil documentation", "inspection support", "permit records"]
    if "data_cleaning" in specialization or "dashboard" in specialization or "statistical" in specialization:
        return ["sql", "data cleaning", "statistical analysis"]
    if "backend" in specialization or "frontend" in specialization or "software_quality" in specialization:
        return ["programming", "testing", "debugging"]
    if "robot" in specialization or "navigation" in specialization:
        return ["robotics", "sensor data", "simulation"]
    if "applied_ai" in specialization or "model_evaluation" in specialization or "ai_infrastructure" in specialization:
        return ["machine learning fundamentals", "model evaluation", "api integration"]
    if "llm_application_development" in specialization:
        return ["llm integration", "tool calling", "application workflows"]
    if "rag_knowledge_systems" in specialization:
        return ["retrieval augmented generation", "document processing", "citation grounding"]
    if "ai_agent_workflows" in specialization:
        return ["agent orchestration", "tool execution", "traceability"]
    if "prompt_context_engineering" in specialization:
        return ["prompt design", "context management", "structured outputs"]
    if "multimodal_ai" in specialization:
        return ["multimodal inputs", "artifact extraction", "model evaluation"]
    if "model_fine_tuning" in specialization:
        return ["fine-tuning", "lora peft", "evaluation datasets"]
    if "responsible_ai_safety" in specialization:
        return ["ai safety checks", "privacy", "unsupported claim detection"]
    if "career_transition_story" in specialization:
        return ["transferable skills narrative", "resume targeting", "interview storytelling"]
    if "portfolio_experience_evidence" in specialization:
        return ["portfolio evidence", "work samples", "role-aligned accomplishments"]
    return []


def _slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return normalized or "role"


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        key = value.lower()
        if key not in seen:
            seen.add(key)
            output.append(value)
    return output


def _dedupe_templates(values: list[SpecializationTemplate]) -> list[SpecializationTemplate]:
    seen: set[str] = set()
    output: list[SpecializationTemplate] = []
    for template in values:
        if template[0] not in seen:
            seen.add(template[0])
            output.append(template)
    return output
