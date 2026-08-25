const sectorCatalog = [
  {
    value: "business_operations",
    label: "Business / Operations",
    description: "Operations, project and program delivery, human resources, supply chain, administration, and consulting.",
    fallback: ["Process Improvement", "Operations Metrics", "Stakeholder Operations", "Business Decision Support"],
    roles: {
      "Operations Analyst": ["Capacity / Service Analysis", "Operations KPI Design", "Root-Cause Recommendations", "Workflow Optimization"],
      "Business Analyst": ["Requirements Analysis", "Business Intelligence", "Process Modeling", "Process Improvement"],
      "Project Coordinator": ["Project Delivery", "Stakeholder Coordination", "Project Controls", "Process Improvement"],
      "Program Manager": ["Program Operations", "Portfolio Coordination", "Change Management", "Process Improvement"],
      "Operations Manager": ["Service Delivery Management", "Capacity / Resource Planning", "Operational Excellence", "Workflow Optimization"],
      "Supply Chain Coordinator": ["Inventory Planning", "Logistics Coordination", "Supplier Performance", "Process Improvement"],
      "Human Resources Coordinator": ["Talent Operations", "Employee Programs", "HR Compliance", "Process Improvement"],
      "Executive Assistant": ["Executive Operations", "Meeting / Communications Support", "Administrative Coordination", "Process Improvement"],
      "Process Improvement Specialist": ["Process Mapping", "Lean / Continuous Improvement", "Change Adoption", "Process Improvement"],
      "Management Consultant": ["Strategy Analysis", "Operating Model Design", "Client Delivery", "Process Improvement"],
    },
  },
  {
    value: "healthcare_wellness",
    label: "Healthcare / Wellness",
    description: "Clinical support, patient services, health administration, wellness, and public health.",
    fallback: ["Care Coordination", "Health Records / Quality", "Health Program Delivery", "Patient Experience"],
    roles: {
      "Clinical Research Coordinator": ["Study Coordination", "Clinical Data Quality", "Regulatory Documentation", "Care Coordination"],
      "Healthcare Administrator": ["Clinic Operations", "Healthcare Reporting", "Healthcare Compliance", "Care Coordination"],
      "Patient Care Coordinator": ["Patient Navigation", "Care Coordination", "Patient Experience", "Health Records / Quality"],
      "Medical Assistant": ["Clinical Support", "Medical Records", "Patient Service", "Care Coordination"],
      "Public Health Analyst": ["Population Health Analysis", "Community Health Programs", "Health Policy / Evaluation", "Care Coordination"],
      "Health Educator": ["Health Curriculum", "Community Outreach", "Behavior Change Support", "Care Coordination"],
      "Behavioral Health Technician": ["Behavioral Support", "Case Documentation", "Care Team Coordination", "Care Coordination"],
      "Pharmacy Technician": ["Medication Operations", "Pharmacy Records", "Patient Medication Support", "Care Coordination"],
      "Wellness Program Coordinator": ["Wellness Program Design", "Participant Engagement", "Wellness Metrics", "Program Operations"],
      "Health Information Specialist": ["Health Information Management", "Health Data Quality", "Privacy / Release of Records", "Care Coordination"],
    },
  },
  {
    value: "education_training",
    label: "Education / Training",
    description: "Teaching, tutoring, learning design, student support, and workforce training.",
    fallback: ["Instructional Delivery", "Learning Design", "Student Success", "Training Evaluation"],
    roles: {
      Teacher: ["Classroom Instruction", "Curriculum Planning", "Student Support", "Instructional Delivery"],
      Tutor: ["One-on-One Instruction", "Study Plan Design", "Academic Coaching", "Instructional Delivery"],
      "Instructional Designer": ["Learning Experience Design", "E-Learning Development", "Training Evaluation", "Instructional Delivery"],
      "Academic Advisor": ["Student Advising", "Case Management", "Academic Success Programs", "Instructional Delivery"],
      "Training Coordinator": ["Training Delivery", "Training Operations", "Enablement Content", "Instructional Delivery"],
      "Curriculum Developer": ["Curriculum Development", "Assessment Alignment", "Instructional Materials", "Instructional Delivery"],
      "Student Success Coach": ["Coaching Programs", "Success Planning", "Learner Engagement", "Instructional Delivery"],
      "Education Program Manager": ["Program Operations", "Portfolio Coordination", "Change Management", "Instructional Delivery"],
      "Learning Experience Designer": ["Learner Research", "Learning Journey Design", "Learning Prototyping", "Instructional Delivery"],
      "Corporate Trainer": ["Facilitation / Delivery", "Workplace Enablement", "Training Measurement", "Instructional Delivery"],
    },
  },
  {
    value: "skilled_trades_construction",
    label: "Skilled Trades / Construction / Manufacturing",
    description: "Construction, maintenance, field service, manufacturing, safety, facilities, and technical operations.",
    fallback: ["Field Operations", "Technical Troubleshooting", "Safety / Quality", "Preventive Maintenance"],
    roles: {
      "Electrician Apprentice": ["Electrical Installation", "Electrical Troubleshooting", "Jobsite Safety", "Field Operations"],
      "HVAC Technician": ["HVAC Diagnostics", "Preventive Maintenance", "Customer Field Service", "Field Operations"],
      "Construction Project Coordinator": ["Construction Coordination", "Site Documentation", "Cost / Schedule Tracking", "Project Delivery"],
      "Manufacturing Technician": ["Production Operations", "Manufacturing Quality", "Continuous Improvement", "Field Operations"],
      "Quality Control Inspector": ["Inspection / Testing", "Defect Analysis", "Quality Systems", "Field Operations"],
      "Field Service Technician": ["Field Diagnostics", "Service Documentation", "Customer Technical Support", "Field Operations"],
      "Facilities Coordinator": ["Facilities Operations", "Preventive Maintenance Planning", "Safety / Compliance", "Field Operations"],
      "CNC Operator": ["Machine Setup", "Precision Quality", "Production Troubleshooting", "Field Operations"],
      "Safety Coordinator": ["Safety Programs", "Incident Documentation", "Risk Assessment", "Field Operations"],
      "Maintenance Planner": ["Preventive Maintenance Strategy", "Work Planning / Scheduling", "Reliability / Asset History", "Field Operations"],
    },
  },
  {
    value: "public_service_government",
    label: "Public Service / Government / Nonprofit",
    description: "Government operations, civic programs, emergency management, policy, community services, and nonprofits.",
    fallback: ["Public Programs", "Policy Research", "Community Engagement", "Program Evaluation"],
    roles: {
      "Policy Analyst": ["Policy Research", "Policy Evaluation", "Briefing Writing", "Public Programs"],
      "City Planner": ["Urban Planning", "Community Engagement", "Planning Analysis", "Public Programs"],
      "Public Administration Analyst": ["Government Program Analysis", "Public Budget / Performance", "Administrative Policy Implementation", "Public Programs"],
      "Emergency Management Specialist": ["Emergency Planning", "Incident Coordination", "Risk / Resilience", "Public Programs"],
      "Community Outreach Coordinator": ["Community Partnerships", "Public Communications", "Program Engagement", "Public Programs"],
      "Nonprofit Program Coordinator": ["Nonprofit Programs", "Funding / Reporting", "Community Services", "Program Operations"],
      "Case Manager": ["Client Assessment", "Service Coordination", "Case Documentation", "Public Programs"],
      "Grant Writer": ["Grant Research", "Proposal Writing", "Grant Reporting", "Public Programs"],
      "Compliance Specialist": ["Regulatory Compliance", "Compliance Monitoring", "Audit Readiness", "Public Programs"],
      "Legislative Aide": ["Constituent Services", "Legislative Research", "Office Operations", "Public Programs"],
    },
  },
  {
    value: "arts_media_design",
    label: "Arts / Media / Design",
    description: "Design, content, communications, production, UX, and creative operations.",
    fallback: ["Creative Production", "Audience Strategy", "Portfolio Development", "Content Operations"],
    roles: {
      "Graphic Designer": ["Visual Identity", "Marketing Design", "Portfolio Production", "Creative Production"],
      "UX Designer": ["User Research", "Interaction Design", "Usability Testing", "Creative Production"],
      "Content Strategist": ["Content Strategy", "Content Operations", "Editorial Analytics", "Creative Production"],
      "Video Producer": ["Video Production", "Post-Production", "Story Development", "Creative Production"],
      "Social Media Manager": ["Social Strategy", "Community Engagement", "Social Analytics", "Creative Production"],
      Copywriter: ["Conversion Copy", "Brand Voice", "Content Research", "Creative Production"],
      "Brand Strategist": ["Brand Positioning", "Campaign Strategy", "Market Insight", "Creative Production"],
      "Product Designer": ["Product Discovery", "Interface Design", "Design Systems", "Creative Production"],
      "Digital Marketing Designer": ["Campaign Creative", "Conversion Design", "Creative Performance", "Creative Production"],
      "Game Designer": ["Game Systems Design", "Level / Experience Design", "Interactive Prototyping", "Creative Production"],
    },
  },
  {
    value: "law_policy_compliance",
    label: "Law / Policy / Compliance",
    description: "Legal support, governance, privacy, regulatory operations, and risk controls.",
    fallback: ["Legal Documentation", "Risk / Compliance", "Research / Briefing", "Control Testing"],
    roles: {
      Paralegal: ["Legal Research", "Case File Management", "Litigation Support", "Legal Documentation"],
      "Legal Assistant": ["Legal Administration", "Document Preparation", "Client Communication", "Legal Documentation"],
      "Compliance Analyst": ["Regulatory Compliance", "Compliance Monitoring", "Audit Readiness", "Legal Documentation"],
      "Privacy Analyst": ["Privacy Operations", "Data Governance", "Privacy Risk Assessment", "Legal Documentation"],
      "Contract Administrator": ["Contract Lifecycle", "Vendor Contracts", "Contract Data Management", "Legal Documentation"],
      "Risk Analyst": ["Risk Assessment", "Control Testing", "Risk Reporting", "Legal Documentation"],
      "Regulatory Affairs Specialist": ["Regulatory Submissions", "Regulatory Research", "Quality Compliance", "Legal Documentation"],
      "Policy Research Assistant": ["Experimental Support", "Literature Review", "Research Data Management", "Policy Research"],
      "Audit Associate": ["Audit Testing", "Audit Documentation", "Process Controls", "Legal Documentation"],
      "Trust and Safety Analyst": ["Policy Enforcement", "Safety Operations", "Abuse Investigation", "Safety Programs"],
    },
  },
  {
    value: "sales_marketing_customer",
    label: "Sales / Marketing / Customer Success",
    description: "Sales, partnerships, growth, customer success, support, community, and market communication.",
    fallback: ["Revenue Growth", "Customer Relationships", "Market Insights", "Sales Operations"],
    roles: {
      "Sales Development Representative": ["Prospecting / Pipeline", "Discovery / Consulting", "CRM / Sales Operations", "Revenue Growth"],
      "Account Manager": ["Account Growth", "Client Relationships", "Retention Strategy", "Revenue Growth"],
      "Customer Success Manager": ["Customer Onboarding", "Customer Health", "Renewal / Expansion", "Revenue Growth"],
      "Marketing Coordinator": ["Campaign Operations", "Content Calendar", "Marketing Reporting", "Revenue Growth"],
      "Growth Marketing Analyst": ["Growth Experimentation", "Acquisition Analytics", "Conversion Optimization", "Revenue Growth"],
      "Product Marketing Associate": ["Positioning / Messaging", "Go-to-Market", "Competitive Research", "Revenue Growth"],
      "Business Development Representative": ["Partnership Development", "Market Expansion", "Deal Coordination", "Revenue Growth"],
      "Customer Support Specialist": ["Support Operations", "Knowledge Base", "Voice of Customer", "Revenue Growth"],
      "Market Research Analyst": ["Market Analysis", "Survey Research", "Insight Reporting", "Revenue Growth"],
      "Community Manager": ["Community Engagement", "Community Programs", "Community Insights", "Revenue Growth"],
    },
  },
  {
    value: "finance_accounting_real_estate",
    label: "Finance / Accounting / Real Estate",
    description: "Accounting, financial planning, banking, insurance, real estate, and investment support.",
    fallback: ["Financial Reporting", "Risk / Controls", "Investment Analysis", "Decision Support"],
    roles: {
      "Financial Analyst": ["Financial Modeling", "Performance Reporting", "Investment Analysis", "Financial Reporting"],
      Accountant: ["General Ledger", "Financial Reporting", "Accounting Controls", "Risk / Controls"],
      Bookkeeper: ["Transaction Recording", "Reconciliations", "Small Business Reporting", "Financial Reporting"],
      "Loan Officer": ["Loan Origination", "Credit Review", "Lending Compliance", "Financial Reporting"],
      "Insurance Claims Analyst": ["Claims Review", "Case Investigation", "Insurance Operations", "Financial Reporting"],
      "Real Estate Analyst": ["Market / Valuation", "Property Analysis", "Real Estate Reporting", "Financial Reporting"],
      "Portfolio Analyst": ["Portfolio Reporting", "Investment Operations", "Risk / Return Analysis", "Financial Reporting"],
      "Tax Associate": ["Tax Preparation", "Tax Research", "Tax Client Service", "Financial Reporting"],
      "Budget Analyst": ["Budget Planning", "Variance Analysis", "Organizational Reporting", "Financial Reporting"],
      "Procurement Analyst": ["Supplier Sourcing", "Purchase Operations", "Spend Analysis", "Financial Reporting"],
    },
  },
  {
    value: "science_engineering_environment",
    label: "Science / Engineering / Technology",
    description: "Scientific research, engineering, environmental analysis, data, software, robotics, and AI systems.",
    fallback: ["Technical Analysis", "Research / Testing", "Systems Engineering", "Technical Documentation"],
    roles: {
      "Research Assistant": ["Experimental Support", "Literature Review", "Research Data Management", "Technical Analysis"],
      "Lab Technician": ["Lab Operations", "Sample Testing", "Scientific Documentation", "Technical Analysis"],
      "Environmental Analyst": ["Environmental Monitoring", "Sustainability Reporting", "Field Research", "Technical Analysis"],
      "Mechanical Engineer": ["Mechanical Design", "Controls Systems", "Product Testing", "Technical Analysis"],
      "Civil Engineering Technician": ["Civil Design Support", "Construction Inspection", "Permitting Documentation", "Technical Analysis"],
      "Data Analyst": ["Data Cleaning", "Dashboard / Reporting", "Statistical Analysis", "Technical Analysis"],
      "Software Engineer": ["Backend Development", "Frontend Development", "Software Quality", "Technical Analysis"],
      "Quality Engineer": ["Quality Systems", "Test Engineering", "Root Cause Analysis", "Technical Analysis"],
      "Robotics Engineer": ["Robot Perception", "Navigation / Controls", "Robot Simulation", "Technical Analysis"],
      "AI Engineer": ["Applied AI Systems", "Model Evaluation", "AI Infrastructure", "LLM Application Development", "RAG / Knowledge Systems", "AI Agent Workflows", "Prompt / Context Engineering", "Multimodal AI", "Model Fine-Tuning", "Responsible AI / Safety"],
    },
  },
];

const sectorRequirements = {
  business_operations: ["process mapping", "spreadsheet modeling", "stakeholder communication", "project tracking"],
  healthcare_wellness: ["patient privacy", "healthcare workflows", "documentation accuracy", "service coordination"],
  education_training: ["instructional planning", "learner support", "assessment design", "clear communication"],
  skilled_trades_construction: ["safety practices", "technical documentation", "field coordination", "quality checks"],
  public_service_government: ["policy research", "public communication", "compliance awareness", "program documentation"],
  arts_media_design: ["portfolio quality", "audience understanding", "visual communication", "creative production"],
  law_policy_compliance: ["document review", "risk controls", "regulatory research", "attention to detail"],
  sales_marketing_customer: ["customer discovery", "crm discipline", "communication", "metrics tracking"],
  finance_accounting_real_estate: ["financial analysis", "data accuracy", "reporting", "regulatory awareness"],
  science_engineering_environment: ["technical analysis", "experimentation", "documentation", "problem solving"],
};

const specializationRequirementRules = [
  [/ai_|llm|rag|model_|prompt_|multimodal/, ["model evaluation", "AI system integration", "responsible AI testing"]],
  [/software|backend|frontend/, ["programming", "testing", "debugging"]],
  [/robot|navigation|controls_systems/, ["systems integration", "sensor data", "simulation and testing"]],
  [/data|analytics|analysis|reporting|metrics|kpi|statistical/, ["data interpretation", "measurement design", "recommendation writing"]],
  [/financial|accounting|ledger|loan|credit|lending|claims|valuation|portfolio|tax|budget|procurement|spend/, ["quantitative analysis", "accuracy controls", "decision-ready reporting"]],
  [/sales|pipeline|account_|customer|marketing|campaign|growth|market_|community/, ["audience or customer research", "performance metrics", "clear communication"]],
  [/legal|compliance|privacy|contract|risk|regulatory|audit|policy/, ["structured research", "controls and documentation", "concise briefing"]],
  [/design|creative|content|video|social|copy|brand|game|interaction|usability/, ["audience research", "iterative production", "reviewable work samples"]],
  [/public|government|nonprofit|grant|legislative|constituent|outreach/, ["stakeholder analysis", "program documentation", "public communication"]],
  [/maintenance|electrical|hvac|construction|manufacturing|field|facilities|machine|safety|quality|inspection/, ["safety and standards", "technical troubleshooting", "work documentation"]],
  [/learning|instruction|curriculum|training|student|academic|coaching|facilitation/, ["learner needs", "practice and assessment", "outcome measurement"]],
  [/clinical|patient|health|care_|pharmacy|medication|wellness|behavioral/, ["privacy-aware documentation", "service coordination", "quality procedures"]],
  [/project|program|coordination|planning|operations|workflow|process|capacity|service_delivery/, ["planning and prioritization", "stakeholder coordination", "outcome tracking"]],
  [/research|experimental|lab|environmental|mechanical|civil|technical/, ["research or test design", "technical documentation", "evidence-based conclusions"]],
];

export const sectors = sectorCatalog.map(({ value, label, description, roles }) => ({
  value,
  label,
  description,
  roles: Object.keys(roles).map((role) => ({ value: role, label: role, specializations: [] })),
}));

export function generateSpecializations(sectorValue, targetRole) {
  const sector = sectorCatalog.find((item) => item.value === sectorValue);
  const roleEntry = sector
    ? Object.entries(sector.roles).find(([role]) => role.toLowerCase() === targetRole.toLowerCase())
    : undefined;
  const labels = roleEntry?.[1] || sector?.fallback || ["Role Fundamentals", "Applied Practice", "Domain Knowledge", "Performance Evidence"];

  return labels.map((label) => ({
    value: `${slugify(targetRole)}__${slugify(label)}`,
    label,
    description: `Develop ${label.toLowerCase()} capability for ${targetRole}.`,
  }));
}

export function requirementsForGoal(goal) {
  const specialization = String(goal.target_function || "");
  const specializationId = specialization.includes("__") ? specialization.split("__").pop() : specialization;
  const requirements = [];

  if (specializationId) {
    requirements.push(humanize(specializationId));
    for (const [pattern, matches] of specializationRequirementRules) {
      if (pattern.test(specializationId)) requirements.push(...matches);
    }
  }

  requirements.push(...(sectorRequirements[String(goal.target_sector || "")] || []));
  requirements.push("portfolio or experience evidence aligned to the selected role");
  return dedupe(requirements).slice(0, 12);
}

function slugify(value) {
  return String(value).toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "") || "role";
}

function humanize(value) {
  return String(value).replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function dedupe(values) {
  return [...new Map(values.filter(Boolean).map((value) => [String(value).toLowerCase(), value])).values()];
}
