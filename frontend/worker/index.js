const PROVIDER_DEFAULT = "hybrid-gemini-first";
const GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/";

const knownSkills = [
  "python",
  "sql",
  "fastapi",
  "react",
  "typescript",
  "machine learning",
  "ml",
  "pytorch",
  "tensorflow",
  "docker",
  "kubernetes",
  "aws",
  "azure",
  "gcp",
  "data analysis",
  "statistics",
  "control systems",
  "robotics",
  "biology",
  "health analytics",
  "nlp",
  "llm",
  "excel",
  "project management",
  "customer support",
  "operations",
];

const sectors = [
  sector("business_operations", "Business / Operations", ["Operations Analyst", "Business Analyst", "Project Coordinator", "Program Manager", "Operations Manager"]),
  sector("healthcare_wellness", "Healthcare / Wellness", ["Clinical Research Coordinator", "Healthcare Administrator", "Patient Care Coordinator", "Public Health Analyst", "Health Educator"]),
  sector("education_training", "Education / Training", ["Teacher", "Tutor", "Instructional Designer", "Academic Advisor", "Training Coordinator"]),
  sector("skilled_trades_construction", "Skilled Trades / Construction", ["Electrician Apprentice", "HVAC Technician", "Construction Project Coordinator", "Manufacturing Technician", "Quality Control Inspector"]),
  sector("public_service_government", "Public Service / Government", ["Policy Analyst", "City Planner", "Public Administration Analyst", "Emergency Management Specialist", "Community Outreach Coordinator"]),
  sector("arts_media_design", "Arts / Media / Design", ["Graphic Designer", "UX Designer", "Content Strategist", "Video Producer", "Product Designer"]),
  sector("law_policy_compliance", "Law / Policy / Compliance", ["Paralegal", "Legal Assistant", "Compliance Analyst", "Privacy Analyst", "Risk Analyst"]),
  sector("sales_marketing_customer", "Sales / Marketing / Customer", ["Sales Development Representative", "Account Manager", "Customer Success Manager", "Marketing Coordinator", "Growth Marketing Analyst"]),
  sector("finance_accounting_real_estate", "Finance / Accounting / Real Estate", ["Financial Analyst", "Accountant", "Bookkeeper", "Loan Officer", "Budget Analyst"]),
  sector("science_engineering_environment", "Science / Engineering / Environment", ["Research Assistant", "Lab Technician", "Environmental Analyst", "Data Analyst", "Software Engineer", "AI Engineer"]),
];

const worker = {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    if (url.pathname.startsWith("/api/")) {
      return handleApi(request, env, url);
    }

    const assetResponse = await env.ASSETS.fetch(request);
    if (assetResponse.status !== 404) {
      return assetResponse;
    }

    if (request.method === "GET" && (request.headers.get("accept") || "").includes("text/html")) {
      return env.ASSETS.fetch(new Request(new URL("/index.html", request.url)));
    }
    return assetResponse;
  },
};

export default worker;

async function handleApi(request, env, url) {
  try {
    if (request.method === "GET" && url.pathname === "/api/health") {
      return json({ status: "ok", provider_mode: env.PATHFORGE_PROVIDER_MODE || PROVIDER_DEFAULT });
    }
    if (request.method === "GET" && url.pathname === "/api/provider-options") {
      return json(providerOptions(env));
    }
    if (request.method === "GET" && url.pathname === "/api/goal-specializations") {
      return json(generateSpecializations(url.searchParams.get("sector") || "", url.searchParams.get("target_role") || "Target Role"));
    }
    if (request.method === "POST" && url.pathname === "/api/profiles/extract") {
      const form = await request.formData();
      const text = String(form.get("background_text") || "");
      if (!text.trim()) return json({ detail: "Provide background_text or upload a supported document." }, 400);
      const extraction = await extractBackground(text, String(form.get("provider_mode") || PROVIDER_DEFAULT), env, "resume");
      return json({ extraction, profile: extraction.entities });
    }
    if (request.method === "POST" && url.pathname === "/api/background-prompt") {
      const form = await request.formData();
      const files = form.getAll("files").filter((item) => typeof item !== "string");
      if (!files.length) return json({ detail: "Attach at least one resume, transcript, datasheet, or notes document." }, 400);
      const documents = await Promise.all(files.map(readUploadedDocument));
      const combined = documents.map((doc) => `Source document: ${doc.filename}\nArtifact type: ${doc.artifact_type}\n\n${doc.text}`).join("\n\n").slice(0, 120000);
      const extraction = await extractBackground(combined, String(form.get("provider_mode") || PROVIDER_DEFAULT), env, "other");
      return json({
        background_prompt: backgroundPromptFromProfile(extraction, documents),
        profile: extraction.entities,
        extraction,
        sources: documents.map((document) => ({
          filename: document.filename,
          artifact_type: document.artifact_type,
          content_type: document.content_type,
          character_count: document.text.length,
        })),
        warnings: extraction.warnings,
      });
    }
    if (request.method === "POST" && url.pathname === "/api/profiles") {
      const profile = await request.json();
      return json({ id: crypto.randomUUID(), profile });
    }
    if (request.method === "POST" && url.pathname === "/api/career-plan") {
      const payload = await request.json();
      if (!payload.profile) return json({ detail: "Provide profile." }, 400);
      const response = await createCareerPlan(payload.profile, payload.goal, String(payload.provider_mode || PROVIDER_DEFAULT), env);
      return json(response);
    }
    return json({ detail: "Not found" }, 404);
  } catch (error) {
    return json({ detail: error instanceof Error ? error.message : "Request failed" }, 500);
  }
}

export { handleApi };

function providerOptions(env) {
  return {
    default_provider_mode: env.PATHFORGE_PROVIDER_MODE || PROVIDER_DEFAULT,
    intelligent_systems: [
      { value: "hybrid-gemini-first", label: "Google API first", description: "Try Google Gemini first, then OpenAI if configured, then the offline demo.", provider_mode: "hybrid-gemini-first", configured: true },
      { value: "gemini", label: "Gemini", description: "Google Gemini via the OpenAI-compatible API.", provider_mode: "gemini", configured: Boolean(env.GEMINI_API_KEY) },
      { value: "openai", label: "ChatGPT / OpenAI", description: "OpenAI fallback when configured.", provider_mode: "openai", configured: Boolean(env.OPENAI_API_KEY) },
      { value: "qwen", label: "Qwen3 4B Instruct", description: "Local-only provider, unavailable on hosted Sites.", provider_mode: "qwen", configured: false },
      { value: "local", label: "Multimodal + LoRA Adapters", description: "Local model service, unavailable on hosted Sites.", provider_mode: "local", configured: false },
      { value: "fake", label: "Offline Demo", description: "Deterministic hosted demo fallback.", provider_mode: "fake", configured: true },
    ],
    sectors,
    specializations: [],
  };
}

function sector(value, label, roles) {
  return {
    value,
    label,
    description: label,
    roles: roles.map((role) => ({ value: role, label: role, specializations: [] })),
  };
}

function generateSpecializations(sectorValue, targetRole) {
  const role = targetRole.toLowerCase();
  const templates = [];
  if (role.includes("ai")) {
    templates.push(["llm_application_development", "LLM Application Development"], ["rag_knowledge_systems", "RAG / Knowledge Systems"], ["ai_agent_workflows", "AI Agent Workflows"], ["model_evaluation", "Model Evaluation"]);
  }
  if (role.includes("analyst") || sectorValue.includes("finance") || sectorValue.includes("operations")) {
    templates.push(["analysis_reporting", "Analysis / Reporting"], ["data_decision_support", "Data-Driven Decision Support"], ["insight_communication", "Insight Communication"]);
  }
  if (role.includes("engineer") || role.includes("software")) {
    templates.push(["technical_implementation", "Technical Implementation"], ["systems_design", "Systems Design"], ["validation_testing", "Validation / Testing"]);
  }
  if (role.includes("designer")) {
    templates.push(["design_execution", "Design Execution"], ["user_audience_research", "User / Audience Research"], ["portfolio_case_studies", "Portfolio Case Studies"]);
  }
  templates.push(["career_transition_story", "Career Transition Story"], ["portfolio_experience_evidence", "Portfolio / Experience Evidence"]);
  return dedupeBy(templates, (item) => item[0]).slice(0, 8).map(([id, label]) => ({
    value: `${slugify(targetRole)}__${id}`,
    label,
    description: `${label} tailored to ${targetRole}.`,
  }));
}

async function readUploadedDocument(file) {
  const text = await file.text();
  return {
    filename: file.name || "uploaded-document",
    content_type: file.type || "application/octet-stream",
    artifact_type: artifactTypeFromFilename(file.name || ""),
    text: text.trim(),
  };
}

async function extractBackground(text, providerMode, env, artifactType) {
  const fallbackEvents = [];
  if (providerMode !== "fake") {
    try {
      const live = await liveJson(providerMode, env, extractionPrompt(), text, env.GEMINI_MODEL || "gemini-3.6-flash");
      const profile = normalizeProfile(live.profile || live.entities || live);
      return {
        artifact_id: crypto.randomUUID(),
        artifact_type: artifactType,
        raw_text: text.slice(0, 10000),
        entities: profile,
        evidence_spans: [],
        extraction_confidence: Number(live.extraction_confidence || 0.78),
        warnings: live.warnings || [],
      };
    } catch (error) {
      fallbackEvents.push(error instanceof Error ? error.message : "Live extraction failed");
    }
  }
  const extraction = fakeExtraction(text, artifactType);
  extraction.warnings.push(...fallbackEvents.map((event) => `Provider fallback: ${event}`));
  return extraction;
}

async function createCareerPlan(profile, goal, providerMode, env) {
  const started = Date.now();
  const evidence = gatherEvidence(goal);
  const gaps = analyzeGaps(profile, evidence);
  const projects = recommendProjects(goal, gaps, profile);
  const nextActions = rankActions(goal, gaps, profile.constraints || {});
  const fallbackEvents = [];
  let plan = fakePlan(profile, goal, evidence, gaps, projects, nextActions);
  let provider = "fake";
  let modelVersion = "hosted-fake-career-reasoner-v1";

  if (providerMode !== "fake") {
    try {
      const live = await liveJson(providerMode, env, reasoningPrompt(), JSON.stringify({ profile, goal, evidence, gaps, projects, next_actions: nextActions }), env.GEMINI_MODEL || "gemini-3.6-flash");
      plan = normalizePlan(live.plan || live, evidence, gaps, projects, nextActions);
      provider = live.provider || (env.GEMINI_API_KEY ? "gemini" : "openai");
      modelVersion = live.model_version || (provider === "gemini" ? env.GEMINI_MODEL || "gemini-3.6-flash" : env.OPENAI_MODEL || "gpt-4.1-mini");
    } catch (error) {
      fallbackEvents.push(error instanceof Error ? error.message : "Live reasoning failed");
    }
  }

  return {
    run_id: crypto.randomUUID(),
    profile_id: null,
    created_at: new Date().toISOString(),
    plan,
    trace: {
      provider,
      model_version: modelVersion,
      tools_called: ["gather_market_evidence", "analyze_skill_gaps", "recommend_projects", "rank_next_actions", "verify_plan"],
      evidence_ids: evidence.map((item) => item.id).concat((plan.evidence || []).map((item) => item.id).filter(Boolean)),
      latency_ms: Date.now() - started,
      fallback_events: fallbackEvents,
      routing_trace: null,
      warnings: plan.caveats || [],
    },
  };
}

async function liveJson(providerMode, env, systemPrompt, userContent, model) {
  const candidates = [];
  if (providerMode.includes("gemini") || providerMode === "hybrid-gemini-first") {
    candidates.push({
      provider: "gemini",
      url: `${env.GEMINI_BASE_URL || GEMINI_BASE_URL}`.replace(/\/?$/, "/") + "chat/completions",
      key: env.GEMINI_API_KEY,
      model: env.GEMINI_MODEL || model,
    });
  }
  if (providerMode.includes("openai") || providerMode === "hybrid-gemini-first") {
    candidates.push({
      provider: "openai",
      url: "https://api.openai.com/v1/chat/completions",
      key: env.OPENAI_API_KEY,
      model: env.OPENAI_MODEL || "gpt-4.1-mini",
    });
  }

  let lastError = "No hosted provider key is configured";
  for (const candidate of candidates) {
    if (!candidate.key) continue;
    const response = await fetch(candidate.url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${candidate.key}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: candidate.model,
        messages: [
          { role: "system", content: `${systemPrompt}\nReturn only valid JSON.` },
          { role: "user", content: userContent },
        ],
        response_format: { type: "json_object" },
      }),
    });
    if (!response.ok) {
      lastError = `${candidate.provider} returned ${response.status}`;
      continue;
    }
    const payload = await response.json();
    const content = payload.choices?.[0]?.message?.content;
    if (!content) throw new Error(`${candidate.provider} returned no content`);
    return JSON.parse(content);
  }
  throw new Error(lastError);
}

function fakeExtraction(text, artifactType) {
  const lowered = text.toLowerCase();
  const skills = knownSkills.filter((skill) => lowered.includes(skill));
  if (skills.includes("ml") && !skills.includes("machine learning")) skills.push("machine learning");
  const titleMatch = lowered.match(/(software engineer|data scientist|mechanical engineer|ai engineer|student|graduate|operations analyst|business analyst)/);
  const title = titleMatch ? titleCase(titleMatch[1]) : "Candidate";
  const education = /\b(ms|m\.s\.|master|graduate)\b/.test(lowered)
    ? [{ degree: "MS", field: "AI or related field", institution: null, dates: null, highlights: [] }]
    : /\b(bs|b\.s\.|bachelor)\b/.test(lowered)
      ? [{ degree: "BS", field: "STEM or related field", institution: null, dates: null, highlights: [] }]
      : [];
  const projects = text.split(/\n+/).filter((line) => line.toLowerCase().includes("project")).slice(0, 4).map((line) => ({
    name: line.slice(0, 80),
    description: line,
    skills: skills.slice(0, 5),
    url: null,
  }));
  return {
    artifact_id: crypto.randomUUID(),
    artifact_type: artifactType,
    raw_text: text.slice(0, 10000),
    entities: normalizeProfile({
      education,
      experience: [{ title, organization: null, dates: null, description: "Extracted from submitted background.", skills: skills.slice(0, 8) }],
      skills,
      projects,
      certifications: [],
      interests: lowered.includes("ai") || lowered.includes("machine learning") ? ["AI"] : [],
      constraints: {},
      source_artifacts: [{ artifact_id: crypto.randomUUID(), artifact_type: artifactType, filename: null, confidence: skills.length ? 0.72 : 0.45 }],
    }),
    evidence_spans: skills.length ? [{ label: "skills", text: skills.join(", "), confidence: 0.78 }] : [],
    extraction_confidence: skills.length ? 0.78 : 0.45,
    warnings: skills.length ? [] : ["Low-confidence extraction: no known skills were detected."],
  };
}

function fakePlan(profile, goal, evidence, gaps, projects, nextActions) {
  const strengths = (profile.skills || []).slice(0, 6);
  const visibleStrengths = strengths.length ? strengths : ["Existing domain experience"];
  return {
    schema_version: "1.0",
    recommended_paths: [{
      title: `${goal.target_role} transition path`,
      rationale: "Build from demonstrated strengths while closing the highest-evidence gaps first.",
      fit_summary: `Current strengths include ${visibleStrengths.slice(0, 3).join(", ")}.`,
      confidence: evidence.length ? 0.72 : 0.62,
    }],
    strengths: visibleStrengths.slice(0, 5).map((skill) => `Demonstrated ${skill}`),
    gaps,
    next_actions: nextActions,
    project_recommendations: projects,
    evidence,
    caveats: ["Hosted demo fallback used when Google/OpenAI keys are not configured or a live provider fails."],
    overall_confidence: evidence.length ? 0.7 : 0.6,
  };
}

function gatherEvidence(goal) {
  return requirementsForGoal(goal).map((requirement) => ({
    id: crypto.randomUUID(),
    claim: `${goal.target_role} roles commonly require ${requirement}.`,
    source_type: "fixture",
    source_title: "PathForge deterministic role evidence fixture",
    source_url: null,
    extracted_requirement: requirement,
    confidence: 0.64,
  }));
}

function requirementsForGoal(goal) {
  const role = String(goal.target_role || "").toLowerCase();
  const requirements = ["portfolio or experience evidence aligned to the selected role"];
  if (role.includes("ai")) requirements.push("python", "llm", "machine learning", "model evaluation", "prompting");
  if (role.includes("analyst")) requirements.push("analysis", "reporting", "data interpretation", "recommendation writing");
  if (role.includes("engineer")) requirements.push("technical problem solving", "system design", "testing", "implementation");
  if (role.includes("designer")) requirements.push("user needs", "prototyping", "portfolio evidence", "design critique");
  if (String(goal.target_sector || "").includes("operations")) requirements.push("process mapping", "spreadsheet modeling", "stakeholder communication", "project tracking");
  if (String(goal.target_function || "").includes("data")) requirements.push("data analysis", "dashboarding", "metrics interpretation");
  return dedupe(requirements).slice(0, 8);
}

function analyzeGaps(profile, evidence) {
  const owned = new Set(profileTerms(profile));
  const counts = new Map();
  for (const item of evidence) {
    for (const skill of candidateSkills(item.extracted_requirement || item.claim)) {
      counts.set(skill, (counts.get(skill) || 0) + 1);
    }
  }
  const max = Math.max(...counts.values(), 1);
  return [...counts.entries()]
    .filter(([skill]) => !owned.has(skill) && !skill.split(" ").some((token) => owned.has(token)))
    .map(([skill, count]) => ({
      skill,
      relevance: Math.min(1, Math.round((0.45 + 0.55 * (count / max)) * 100) / 100),
      evidence_count: count,
      reason: `Appears in ${count} evidence item(s) for the target role and is not clearly present in the profile.`,
      supporting_evidence_ids: evidence.filter((item) => (item.extracted_requirement || item.claim).toLowerCase().includes(skill)).map((item) => item.id),
    }))
    .sort((a, b) => b.relevance - a.relevance || b.evidence_count - a.evidence_count || a.skill.localeCompare(b.skill))
    .slice(0, 10);
}

function recommendProjects(goal, gaps, profile) {
  const selected = gaps.slice(0, 6).map((gap) => gap.skill);
  const addressed = selected.length ? selected : ["clear proof you can do this role", "clear interview explanation of your projects"];
  const projects = [
    {
      title: `${goal.target_role} proof-of-skill project`,
      description: "Build a small app, notebook, or portfolio page that shows the inputs, your process, the result, and what decisions someone could make from it.",
      addressed_gaps: addressed.slice(0, 3),
      expected_artifacts: ["GitHub repository", "README explaining decisions", "screenshots or short demo recording"],
      estimated_weeks: 4,
    },
    {
      title: "End-to-end role workflow",
      description: "Show one complete process from start to finish, including input, processing, result, validation, and error handling.",
      addressed_gaps: addressed.slice(2, 5).length ? addressed.slice(2, 5) : addressed.slice(0, 2),
      expected_artifacts: ["deployed demo or local setup", "test report", "simple architecture diagram"],
      estimated_weeks: 5,
    },
  ];
  if ((profile.projects || []).length) {
    projects.push({
      title: "Upgrade an existing project",
      description: "Make target-role proof obvious: add tests, setup instructions, before/after notes, metrics, screenshots, and a README.",
      addressed_gaps: addressed.slice(0, 2),
      expected_artifacts: ["before/after README", "issue list", "merged improvements"],
      estimated_weeks: 2,
    });
  }
  return projects;
}

function rankActions(goal, gaps, constraints) {
  const topGap = gaps[0]?.skill || "target-role evidence";
  const shortTimeline = Number(goal.horizon_months || 12) <= 6;
  const actions = [
    {
      title: `Close the top gap: ${topGap}`,
      rationale: `Create clearer proof for ${topGap}. Build, improve, or document work that shows a reviewer you can already handle that part of a ${goal.target_role} role.`,
      impact: 5,
      effort: constraints.time_budget_hours_per_week && constraints.time_budget_hours_per_week < 6 ? 2 : 3,
      priority: 1,
      constraint_notes: constraints.time_budget_hours_per_week && constraints.time_budget_hours_per_week < 6 ? ["Low weekly time budget: prefer narrow, portfolio-visible work."] : [],
    },
    {
      title: "Rewrite profile narrative for the target role",
      rationale: "Describe real experience using target-role language: problem, tools, tradeoffs, metrics, failures, and outcome.",
      impact: 4,
      effort: 2,
      priority: 2,
      constraint_notes: [],
    },
    {
      title: "Run two informational interviews or portfolio reviews",
      rationale: "Ask people near the role to review your portfolio/resume and identify which proof is missing or unclear.",
      impact: 4,
      effort: 3,
      priority: 3,
      constraint_notes: constraints.location ? [`Location constraint: ${constraints.location}`] : [],
    },
  ];
  if (shortTimeline) {
    actions.push({
      title: "Choose applications that value adjacent experience",
      rationale: "The short horizon favors roles where existing strengths outweigh missing credentials.",
      impact: 4,
      effort: 2,
      priority: 4,
      constraint_notes: ["Short timeline: avoid long prerequisite chains."],
    });
  }
  return actions;
}

function backgroundPromptFromProfile(extraction, documents) {
  const profile = extraction.entities;
  const lines = [
    "Use the background below to evaluate career fit, identify role-specific evidence, and recommend practical next steps.",
    "",
    "Candidate Background",
    section("Education", (profile.education || []).map((item) => [item.degree, item.field, item.institution, item.dates].filter(Boolean).join(", "))),
    section("Experience", (profile.experience || []).map((item) => `${item.title}${item.description ? `: ${item.description}` : ""}`)),
    section("Projects", (profile.projects || []).map((item) => `${item.name}${item.description ? `: ${item.description}` : ""}`)),
    section("Skills", profile.skills || []),
    section("Certifications", profile.certifications || []),
    section("Interests", profile.interests || []),
    "",
    "Source Documents",
    ...documents.map((document) => `- ${document.filename} (${document.artifact_type})`),
  ];
  return lines.filter(Boolean).join("\n").trim();
}

function normalizePlan(value, evidence, gaps, projects, nextActions) {
  return {
    schema_version: "1.0",
    recommended_paths: Array.isArray(value.recommended_paths) && value.recommended_paths.length ? value.recommended_paths : fakePlan({ skills: [] }, { target_role: "Target Role" }, evidence, gaps, projects, nextActions).recommended_paths,
    strengths: Array.isArray(value.strengths) ? value.strengths : [],
    gaps: Array.isArray(value.gaps) && value.gaps.length ? value.gaps : gaps,
    next_actions: Array.isArray(value.next_actions) && value.next_actions.length ? value.next_actions : nextActions,
    project_recommendations: Array.isArray(value.project_recommendations) && value.project_recommendations.length ? value.project_recommendations : projects,
    evidence: Array.isArray(value.evidence) && value.evidence.length ? value.evidence : evidence,
    caveats: Array.isArray(value.caveats) ? value.caveats : [],
    overall_confidence: typeof value.overall_confidence === "number" ? value.overall_confidence : 0.68,
  };
}

function normalizeProfile(value) {
  return {
    schema_version: "1.0",
    education: Array.isArray(value.education) ? value.education : [],
    experience: Array.isArray(value.experience) ? value.experience : [],
    skills: dedupe(Array.isArray(value.skills) ? value.skills.map(String) : []),
    projects: Array.isArray(value.projects) ? value.projects : [],
    certifications: Array.isArray(value.certifications) ? value.certifications : [],
    interests: Array.isArray(value.interests) ? value.interests : [],
    constraints: value.constraints && typeof value.constraints === "object" ? value.constraints : {},
    source_artifacts: Array.isArray(value.source_artifacts) ? value.source_artifacts : [],
  };
}

function extractionPrompt() {
  return "Extract a career profile JSON object with keys: education, experience, skills, projects, certifications, interests, constraints, source_artifacts, extraction_confidence, warnings.";
}

function reasoningPrompt() {
  return "Create a career plan JSON object with keys: recommended_paths, strengths, gaps, next_actions, project_recommendations, evidence, caveats, overall_confidence. Keep every recommendation practical and evidence-grounded.";
}

function section(title, items) {
  const filtered = (items || []).filter(Boolean);
  if (!filtered.length) return null;
  return [title, ...filtered.map((item) => `- ${item}`)].join("\n");
}

function artifactTypeFromFilename(filename) {
  const lowered = filename.toLowerCase();
  if (lowered.includes("transcript") || lowered.includes("grade")) return "transcript";
  if (lowered.includes("portfolio") || lowered.includes("project")) return "portfolio";
  if (lowered.includes("certificate")) return "certificate";
  if (lowered.includes("resume") || lowered.includes("cv")) return "resume";
  return "other";
}

function candidateSkills(text) {
  const lowered = String(text).toLowerCase();
  return knownSkills.filter((skill) => lowered.includes(skill)).concat(lowered.match(/\b[A-Za-z][A-Za-z0-9+#./-]{2,}\b/g) || []).map((skill) => skill.toLowerCase()).filter((skill) => !["experience", "required", "preferred", "candidate", "skills", "build", "using"].includes(skill));
}

function profileTerms(profile) {
  const parts = [
    ...(profile.skills || []),
    ...(profile.certifications || []),
    ...(profile.interests || []),
    ...(profile.experience || []).flatMap((item) => [item.title, item.description, ...(item.skills || [])]),
    ...(profile.projects || []).flatMap((item) => [item.name, item.description, ...(item.skills || [])]),
  ];
  return candidateSkills(parts.filter(Boolean).join(" "));
}

function slugify(value) {
  return String(value).toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "") || "role";
}

function titleCase(value) {
  return value.replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function dedupe(values) {
  return [...new Set(values.map((value) => String(value).trim()).filter(Boolean))];
}

function dedupeBy(values, getKey) {
  const seen = new Set();
  return values.filter((value) => {
    const key = getKey(value);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function json(payload, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
}
