import { generateSpecializations, requirementsForGoal, sectors } from "./career-taxonomy.js";

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
        warnings: extraction.warnings.concat(documents.map((document) => document.warning).filter(Boolean)),
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

async function readUploadedDocument(file) {
  const filename = file.name || "uploaded-document";
  const artifactType = artifactTypeFromFilename(filename);
  const document = await extractHostedDocumentText(file, filename);
  return {
    filename,
    content_type: file.type || "application/octet-stream",
    artifact_type: artifactType,
    text: document.text,
    warning: document.warning,
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
  const warnings = extraction.warnings.concat(documents.map((document) => document.warning).filter(Boolean));
  if (warnings.length) {
    lines.push("", "Review Notes", ...warnings.map((warning) => `- ${warning}`));
  }
  return lines.filter(Boolean).join("\n").trim();
}

function normalizePlan(value, evidence, gaps, projects, nextActions) {
  const fallback = fakePlan({ skills: [] }, { target_role: "Target Role" }, evidence, gaps, projects, nextActions);
  const source = value && typeof value === "object" ? value : {};
  const normalizedEvidence = listOr(source.evidence, evidence).map(normalizeEvidenceItem).filter((item) => item.claim);
  return {
    schema_version: "1.0",
    recommended_paths: listOr(source.recommended_paths, fallback.recommended_paths).map(normalizeRecommendedPath),
    strengths: stringList(source.strengths),
    gaps: listOr(source.gaps, gaps).map(normalizeGap).filter((gap) => gap.skill),
    next_actions: listOr(source.next_actions, nextActions).map(normalizeNextAction).filter((action) => action.title),
    project_recommendations: listOr(source.project_recommendations, projects).map(normalizeProject).filter((project) => project.title),
    evidence: normalizedEvidence.length ? normalizedEvidence : evidence.map(normalizeEvidenceItem),
    caveats: stringList(source.caveats),
    overall_confidence: boundedNumber(source.overall_confidence, 0.68, 0, 1),
  };
}

function listOr(value, fallback) {
  return Array.isArray(value) && value.length ? value : fallback;
}

function stringValue(value, fallback = "") {
  if (typeof value === "string") return value.trim();
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  if (value && typeof value === "object") {
    if (typeof value.title === "string") return value.title.trim();
    if (typeof value.name === "string") return value.name.trim();
    if (typeof value.skill === "string") return value.skill.trim();
    if (typeof value.claim === "string") return value.claim.trim();
    if (typeof value.description === "string") return value.description.trim();
  }
  return fallback;
}

function stringList(value) {
  if (!Array.isArray(value)) return [];
  return dedupe(value.map((item) => stringValue(item)).filter(Boolean));
}

function boundedNumber(value, fallback, min = Number.NEGATIVE_INFINITY, max = Number.POSITIVE_INFINITY) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.min(max, Math.max(min, parsed));
}

function normalizeRecommendedPath(value) {
  const item = value && typeof value === "object" ? value : {};
  const title = stringValue(item.title || value, "Recommended path");
  return {
    title,
    rationale: stringValue(item.rationale, "This path aligns with the available profile evidence and target role."),
    fit_summary: stringValue(item.fit_summary || item.summary || item.description, title),
    confidence: boundedNumber(item.confidence, 0.62, 0, 1),
  };
}

function normalizeGap(value) {
  const item = value && typeof value === "object" ? value : {};
  const skill = stringValue(item.skill || value, "target-role evidence");
  return {
    skill,
    reason: stringValue(item.reason || item.rationale, `Build clearer evidence for ${skill}.`),
    relevance: boundedNumber(item.relevance, 0.6, 0, 1),
    evidence_count: Math.max(0, Math.round(boundedNumber(item.evidence_count, 1, 0))),
    supporting_evidence_ids: stringList(item.supporting_evidence_ids),
  };
}

function normalizeNextAction(value) {
  const item = value && typeof value === "object" ? value : {};
  const title = stringValue(item.title || value, "Clarify target-role evidence");
  return {
    title,
    rationale: stringValue(item.rationale || item.reason || item.description, "Make the next step concrete, visible, and easy to verify."),
    impact: Math.round(boundedNumber(item.impact, 3, 1, 5)),
    effort: Math.round(boundedNumber(item.effort, 3, 1, 5)),
    priority: Math.max(1, Math.round(boundedNumber(item.priority, 1, 1))),
    constraint_notes: stringList(item.constraint_notes),
  };
}

function normalizeProject(value) {
  const item = value && typeof value === "object" ? value : {};
  const title = stringValue(item.title || item.name || value, "Target-role proof project");
  return {
    title,
    description: stringValue(item.description || item.rationale, "Create a portfolio artifact that demonstrates readiness for the target role."),
    addressed_gaps: stringList(item.addressed_gaps).length ? stringList(item.addressed_gaps) : ["target-role readiness"],
    expected_artifacts: stringList(item.expected_artifacts),
    estimated_weeks: Math.max(1, Math.round(boundedNumber(item.estimated_weeks, 4, 1))),
  };
}

function normalizeEvidenceItem(value) {
  const item = value && typeof value === "object" ? value : {};
  const requirement = stringValue(item.extracted_requirement || item.requirement || item.claim || value, "target-role readiness");
  const claim = stringValue(item.claim || item.description, `${requirement} matters for the target role.`);
  return {
    id: stringValue(item.id, crypto.randomUUID()),
    claim,
    source_type: stringValue(item.source_type, "hosted"),
    source_title: stringValue(item.source_title, "PathForge hosted evidence"),
    source_url: typeof item.source_url === "string" ? item.source_url : null,
    extracted_requirement: requirement,
    confidence: boundedNumber(item.confidence, 0.6, 0, 1),
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
  if (/\.(docx|pdf|txt|md)$/i.test(lowered)) return "resume";
  return "other";
}

async function extractHostedDocumentText(file, filename) {
  const lowered = filename.toLowerCase();
  if (typeof file.arrayBuffer === "function") {
    const bytes = new Uint8Array(await file.arrayBuffer());
    if (lowered.endsWith(".docx")) {
      const text = await extractDocxText(bytes);
      if (text) return { text, warning: null };
      return unreadableDocument(filename, "Hosted extraction could not find readable Word document text.");
    }
    if (lowered.endsWith(".pdf")) {
      const text = await extractPdfText(bytes);
      if (text) return { text, warning: null };
      return unreadableDocument(filename, "Hosted extraction could not find selectable PDF text.");
    }
    const decoded = new TextDecoder("utf-8", { fatal: false }).decode(bytes);
    return readableDocumentText(decoded, filename);
  }
  if (typeof file.text === "function") {
    return readableDocumentText(await file.text(), filename);
  }
  return unreadableDocument(filename, "Hosted extraction could not read this upload.");
}

function readableDocumentText(text, filename) {
  const trimmed = String(text || "").replace(/\u0000/g, " ").trim();
  const readableCharacters = (trimmed.match(/[A-Za-z0-9.,;:!?@#$%&()[\]\-_/\\\s]/g) || []).length;
  const readability = trimmed.length ? readableCharacters / trimmed.length : 0;
  if (trimmed.length >= 20 && readability >= 0.55) {
    return { text: trimmed.slice(0, 120000), warning: null };
  }
  return unreadableDocument(filename, "Hosted extraction could not read usable plain text from this file.");
}

function unreadableDocument(filename, warning) {
  return {
    text: `Uploaded document: ${filename}. ${warning}`,
    warning: `${filename} could not be fully read in the hosted version. Paste the document text for a richer extraction.`,
  };
}

async function extractPdfText(bytes) {
  try {
    const module = await import("pdf-parse");
    const pdfParse = module.default ?? module;
    const parsed = await pdfParse(Buffer.from(bytes));
    return String(parsed.text || "")
      .replace(/\r/g, "\n")
      .replace(/\n{3,}/g, "\n\n")
      .trim()
      .slice(0, 120000);
  } catch {
    return "";
  }
}

async function extractDocxText(bytes) {
  try {
    const files = await unzipDocxParts(bytes);
    const docxParts = files
      .filter(([name]) => name === "word/document.xml" || name.startsWith("word/header") || name.startsWith("word/footer"))
      .sort(([left], [right]) => Number(left !== "word/document.xml") - Number(right !== "word/document.xml"));
    const decoder = new TextDecoder("utf-8", { fatal: false });
    const text = docxParts
      .map(([, data]) => xmlText(decoder.decode(data)))
      .filter(Boolean)
      .join("\n")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
    return text.slice(0, 120000);
  } catch {
    return "";
  }
}

async function unzipDocxParts(bytes) {
  const { inflateRawSync } = await import("node:zlib");
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const endOffset = findZipEnd(view);
  if (endOffset < 0) return [];
  const entryCount = view.getUint16(endOffset + 10, true);
  let centralOffset = view.getUint32(endOffset + 16, true);
  const files = [];

  for (let index = 0; index < entryCount; index += 1) {
    if (view.getUint32(centralOffset, true) !== 0x02014b50) break;
    const method = view.getUint16(centralOffset + 10, true);
    const compressedSize = view.getUint32(centralOffset + 20, true);
    const filenameLength = view.getUint16(centralOffset + 28, true);
    const extraLength = view.getUint16(centralOffset + 30, true);
    const commentLength = view.getUint16(centralOffset + 32, true);
    const localOffset = view.getUint32(centralOffset + 42, true);
    const filenameBytes = bytes.slice(centralOffset + 46, centralOffset + 46 + filenameLength);
    const filename = new TextDecoder("utf-8", { fatal: false }).decode(filenameBytes);

    if (view.getUint32(localOffset, true) === 0x04034b50) {
      const localFilenameLength = view.getUint16(localOffset + 26, true);
      const localExtraLength = view.getUint16(localOffset + 28, true);
      const dataStart = localOffset + 30 + localFilenameLength + localExtraLength;
      const compressed = bytes.slice(dataStart, dataStart + compressedSize);
      if (method === 0) {
        files.push([filename, compressed]);
      } else if (method === 8) {
        files.push([filename, new Uint8Array(inflateRawSync(compressed))]);
      }
    }
    centralOffset += 46 + filenameLength + extraLength + commentLength;
  }
  return files;
}

function findZipEnd(view) {
  for (let offset = view.byteLength - 22; offset >= 0; offset -= 1) {
    if (view.getUint32(offset, true) === 0x06054b50) return offset;
  }
  return -1;
}

function xmlText(xml) {
  return xml
    .replace(/<w:tab\/>/g, "\t")
    .replace(/<w:br\/>/g, "\n")
    .replace(/<\/w:p>/g, "\n")
    .replace(/<[^>]+>/g, "")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .split(/\n/)
    .map((line) => line.replace(/\s+/g, " ").trim())
    .filter(Boolean)
    .join("\n");
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

function titleCase(value) {
  return value.replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function dedupe(values) {
  return [...new Set(values.map((value) => String(value).trim()).filter(Boolean))];
}

function json(payload, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8" },
  });
}
