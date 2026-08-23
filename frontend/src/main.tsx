import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { ArrowRight, BrainCircuit, CheckCircle2, ChevronLeft, ChevronRight, ClipboardCheck, FileText, FileUp, Globe2, Loader2, Route, Search, ShieldCheck, Sparkles, UserRound, X } from "lucide-react";
import {
  createBackgroundPrompt,
  createCareerPlan,
  extractProfile,
  getGoalSpecializations,
  getProviderOptions
} from "./api/pathforge";
import type {
  BackgroundPromptResponse,
  CareerGoal,
  CareerPlanResponse,
  CareerProfile,
  ProviderMode,
  ProviderOptionsResponse,
  RoleOption,
  SectorOption,
  SelectOption
} from "./types/pathforge";
import "./styles.css";

const sampleBackground =
  "";

const backgroundPlaceholder =
  "Attach documents and click Build Background Prompt, or paste your background here. Include education, experience, projects, skills, constraints, and target interests.";

const backgroundQuestions = [
  {
    id: "current",
    label: "Current situation",
    prompt: "What are you doing now?",
    placeholder: "Example: working retail, finishing school, freelancing, caring for family, job searching, changing careers..."
  },
  {
    id: "education",
    label: "Education and training",
    prompt: "What school, training, courses, certifications, or self-study have you completed?",
    placeholder: "Include degrees, bootcamps, online courses, workshops, certificates, or topics learned on your own."
  },
  {
    id: "experience",
    label: "Work and responsibilities",
    prompt: "What jobs, volunteer work, internships, or responsibilities have you had?",
    placeholder: "Include titles if you know them, daily tasks, tools used, customers served, teams supported, or operations handled."
  },
  {
    id: "skills",
    label: "Skills and tools",
    prompt: "What skills, tools, software, languages, or strengths do you have?",
    placeholder: "Example: Excel, Python, writing, customer support, scheduling, troubleshooting, design, analysis, leadership..."
  },
  {
    id: "projects",
    label: "Projects and accomplishments",
    prompt: "What have you built, improved, organized, solved, or helped complete?",
    placeholder: "Include personal projects, class projects, work wins, process improvements, dashboards, automations, events, or portfolios."
  },
  {
    id: "interests",
    label: "Interests",
    prompt: "What kind of work, industries, or problems are you interested in?",
    placeholder: "Example: AI tools, healthcare, games, finance, operations, helping people, automation, research, creative work..."
  },
  {
    id: "constraints",
    label: "Constraints and preferences",
    prompt: "What should the plan account for?",
    placeholder: "Include time per week, location, remote/hybrid, budget, family needs, accessibility, schedule, timeline, or dealbreakers."
  },
  {
    id: "extra",
    label: "Anything else",
    prompt: "What else should the agent know about you?",
    placeholder: "Add context that does not fit above, or write unsure if you do not know."
  }
];

const emptyGuidedAnswers = Object.fromEntries(backgroundQuestions.map((question) => [question.id, ""]));

const fallbackOptions: ProviderOptionsResponse = {
  default_provider_mode: "hybrid-gemini-first",
  intelligent_systems: [
    { value: "hybrid-gemini-first", label: "Google API first", description: "Try Google Gemini first, then OpenAI if configured, then the offline demo.", provider_mode: "hybrid-gemini-first", configured: true },
    { value: "gemini", label: "Gemini", provider_mode: "gemini", configured: true },
    { value: "openai", label: "ChatGPT / OpenAI", provider_mode: "openai", configured: true },
    { value: "qwen", label: "Qwen3 4B Instruct", provider_mode: "qwen", configured: true },
    { value: "local", label: "Multimodal + LoRA Adapters", provider_mode: "local", configured: true },
    { value: "fake", label: "Offline Demo", provider_mode: "fake", configured: true }
  ],
  sectors: [
    {
      value: "business_operations",
      label: "Business / Operations",
      roles: [
        { value: "Operations Analyst", label: "Operations Analyst", specializations: [] },
        { value: "Business Analyst", label: "Business Analyst", specializations: [] },
        { value: "Project Coordinator", label: "Project Coordinator", specializations: [] }
      ]
    }
  ],
  specializations: [
    { value: "applied_ai", label: "Applied AI" },
    { value: "ai_data", label: "AI / Data" },
    { value: "mlops", label: "MLOps / Model Serving" },
    { value: "software", label: "Software Engineering" }
  ]
};

function App() {
  const [background, setBackground] = useState(sampleBackground);
  const [guidedOpen, setGuidedOpen] = useState(false);
  const [guidedStep, setGuidedStep] = useState(0);
  const [guidedAnswers, setGuidedAnswers] = useState<Record<string, string>>(emptyGuidedAnswers);
  const [profile, setProfile] = useState<CareerProfile | null>(null);
  const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
  const [documentSources, setDocumentSources] = useState<BackgroundPromptResponse["sources"]>([]);
  const [documentWarnings, setDocumentWarnings] = useState<string[]>([]);
  const [providerOptions, setProviderOptions] = useState<ProviderOptionsResponse>(fallbackOptions);
  const [specializationOptions, setSpecializationOptions] = useState<SelectOption[]>(fallbackOptions.specializations);
  const [selectedProvider, setSelectedProvider] = useState<ProviderMode>("hybrid-gemini-first");
  const [goal, setGoal] = useState<CareerGoal>({
    target_role: "Operations Analyst",
    target_sector: "business_operations",
    target_function: "operations_analyst__data_analytics",
    horizon_months: 12,
    priorities: ["portfolio", "practical projects"]
  });
  const [result, setResult] = useState<CareerPlanResponse | null>(null);
  const [loadingAction, setLoadingAction] = useState<"documents" | "extract" | "plan" | null>(null);
  const [traceOpen, setTraceOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const loading = loadingAction !== null;
  const guidedAnsweredCount = backgroundQuestions.filter((question) => guidedAnswers[question.id]?.trim()).length;
  const guidedQuestion = backgroundQuestions[guidedStep];

  useEffect(() => {
    getProviderOptions()
      .then((options) => {
        setProviderOptions(options);
        setSelectedProvider(pickDefaultProvider(options));
        const sector = findSector(options, goal.target_sector) ?? options.sectors[0];
        const role = findRole(sector, goal.target_role) ?? sector.roles[0];
        setGoal((current) => ({
          ...current,
          target_sector: sector.value,
          target_role: role.value,
        }));
      })
      .catch(() => setProviderOptions(fallbackOptions));
  }, []);

  const selectedSector = useMemo(
    () => findSector(providerOptions, goal.target_sector) ?? providerOptions.sectors[0],
    [providerOptions, goal.target_sector]
  );
  const selectedRole = useMemo(
    () => findRole(selectedSector, goal.target_role) ?? selectedSector.roles[0],
    [selectedSector, goal.target_role]
  );
  const selectedSystem = useMemo(
    () => providerOptions.intelligent_systems.find((system) => system.provider_mode === selectedProvider),
    [providerOptions, selectedProvider]
  );
  useEffect(() => {
    let active = true;
    getGoalSpecializations(selectedSector.value, selectedRole.value)
      .then((options) => {
        if (!active) return;
        setSpecializationOptions(options);
        setGoal((current) => ({
          ...current,
          target_function: options.some((option) => option.value === current.target_function)
            ? current.target_function
            : options[0]?.value ?? null
        }));
      })
      .catch(() => {
        if (!active) return;
        setSpecializationOptions(fallbackOptions.specializations);
      });
    return () => {
      active = false;
    };
  }, [selectedSector.value, selectedRole.value]);

  async function handleBuildBackgroundPrompt() {
    if (!attachedFiles.length) return;
    setLoadingAction("documents");
    setError(null);
    setDocumentWarnings([]);
    try {
      const response = await createBackgroundPrompt(attachedFiles, selectedProvider);
      setBackground(response.background_prompt);
      setProfile(response.profile);
      setDocumentSources(response.sources);
      setDocumentWarnings(response.warnings);
      setResult(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Document conversion failed");
    } finally {
      setLoadingAction(null);
    }
  }

  async function handleExtract() {
    setLoadingAction("extract");
    setError(null);
    try {
      const response = await extractProfile(background, selectedProvider);
      setProfile(response.profile);
      setResult(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Profile extraction failed");
    } finally {
      setLoadingAction(null);
    }
  }

  async function handleRun() {
    if (!profile) return;
    setLoadingAction("plan");
    setError(null);
    try {
      const response = await createCareerPlan(profile, goal, selectedProvider);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Career-plan run failed");
    } finally {
      setLoadingAction(null);
    }
  }

  function handleSectorChange(value: string) {
    const nextSector = findSector(providerOptions, value) ?? providerOptions.sectors[0];
    const nextRole = nextSector.roles[0];
    setGoal({
      ...goal,
      target_sector: nextSector.value,
      target_role: nextRole.value,
      target_function: null
    });
  }

  function handleRoleChange(value: string) {
    const nextRole = findRole(selectedSector, value) ?? selectedSector.roles[0];
    setGoal({
      ...goal,
      target_role: nextRole.value,
      target_function: null
    });
  }

  function handleGuidedAnswer(value: string) {
    setGuidedAnswers((current) => ({ ...current, [guidedQuestion.id]: value }));
  }

  function handleUseGuidedBackground() {
    const sections = backgroundQuestions
      .map((question) => {
        const answer = guidedAnswers[question.id]?.trim();
        return answer ? `${question.label}: ${answer}` : null;
      })
      .filter(Boolean);

    if (!sections.length) return;
    setBackground(sections.join("\n\n"));
    setProfile(null);
    setResult(null);
    setError(null);
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brandLockup">
          <span className="brandMark"><Route size={20} /></span>
          <div>
            <h1>PathForge AI</h1>
            <p>Career-navigation website</p>
          </div>
        </div>
        <nav className="topLinks" aria-label="Primary">
          <a href="#workspace">Workspace</a>
          <a href="#results">Results</a>
        </nav>
      </header>

      <section className="hero">
        <div className="heroCopy">
          <span className="eyebrow"><Sparkles size={15} /> Google API first</span>
          <h2>Build a practical career plan from messy background notes.</h2>
          <p>PathForge turns resumes, transcripts, project notes, and goals into an evidence-grounded plan with skills to prove, projects to build, and next actions to take.</p>
          <div className="heroActions">
            <a className="buttonLink" href="#workspace">
              Start planning
              <ArrowRight size={16} />
            </a>
            <span className="inlineStatus"><ShieldCheck size={16} /> Provider trace preserved</span>
          </div>
        </div>
        <aside className="systemCard" aria-label="Intelligent system">
          <label className="systemPicker">
            <span><BrainCircuit size={16} /> Intelligent system</span>
            <select value={selectedProvider} onChange={(event) => setSelectedProvider(event.target.value as ProviderMode)}>
              {providerOptions.intelligent_systems.map((system) => (
                <option key={system.provider_mode} value={system.provider_mode} disabled={!system.configured}>
                  {system.label}{system.configured ? "" : " (needs key)"}
                </option>
              ))}
            </select>
          </label>
          <p>{selectedSystem?.description ?? "Select a provider for extraction and reasoning."}</p>
          <div className="systemSignals">
            <span><Globe2 size={14} /> Google first</span>
            <span><CheckCircle2 size={14} /> Offline fallback</span>
          </div>
        </aside>
      </section>

      <section className="workflow" id="workspace">
        <Panel icon={<FileText size={18} />} title="Background">
          <div className="documentIntake">
            <label className="filePicker">
              <FileUp size={18} />
              <span>Attach resume, transcripts, datasheet, or notes</span>
              <input
                type="file"
                multiple
                accept=".txt,.md,.csv,.tsv,.json,.docx,.pdf,.xlsx"
                onChange={(event) => setAttachedFiles(Array.from(event.target.files ?? []))}
              />
            </label>
            {attachedFiles.length ? (
              <ul className="fileList">
                {attachedFiles.map((file) => (
                  <li key={`${file.name}-${file.size}-${file.lastModified}`}>
                    <span>{file.name}</span>
                    <small>{formatBytes(file.size)}</small>
                    <button
                      className="tinyIconButton"
                      title={`Remove ${file.name}`}
                      onClick={() => setAttachedFiles(attachedFiles.filter((candidate) => candidate !== file))}
                    >
                      <X size={14} />
                    </button>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="smallHint">Supported: TXT, MD, CSV, TSV, JSON, DOCX, XLSX, and PDF.</p>
            )}
            <button onClick={handleBuildBackgroundPrompt} disabled={!attachedFiles.length || loading}>
              {loadingAction === "documents" ? <Loader2 className="spin" size={16} /> : <FileUp size={16} />}
              Build Background Prompt
            </button>
          </div>
          <div className="guidedIntake">
            <button className="secondary" onClick={() => setGuidedOpen(!guidedOpen)}>
              <UserRound size={16} />
              Answer Background Questions
            </button>
            {guidedOpen ? (
              <div className="guidedBuilder">
                <div className="guidedMeta">
                  <strong>{guidedQuestion.label}</strong>
                  <span>{guidedStep + 1} of {backgroundQuestions.length} | {guidedAnsweredCount} answered</span>
                </div>
                <label>
                  {guidedQuestion.prompt}
                  <textarea
                    className="guidedAnswer"
                    value={guidedAnswers[guidedQuestion.id] ?? ""}
                    placeholder={guidedQuestion.placeholder}
                    onChange={(event) => handleGuidedAnswer(event.target.value)}
                  />
                </label>
                <div className="guidedControls">
                  <button
                    className="secondary"
                    onClick={() => setGuidedStep(Math.max(0, guidedStep - 1))}
                    disabled={guidedStep === 0}
                  >
                    <ChevronLeft size={16} />
                    Previous
                  </button>
                  <button
                    className="secondary"
                    onClick={() => setGuidedStep(Math.min(backgroundQuestions.length - 1, guidedStep + 1))}
                    disabled={guidedStep === backgroundQuestions.length - 1}
                  >
                    Next
                    <ChevronRight size={16} />
                  </button>
                </div>
                <button onClick={handleUseGuidedBackground} disabled={!guidedAnsweredCount || loading}>
                  <FileText size={16} />
                  Use Answers As Background
                </button>
              </div>
            ) : null}
          </div>
          <textarea
            value={background}
            placeholder={backgroundPlaceholder}
            onChange={(event) => setBackground(event.target.value)}
          />
          {documentSources.length ? <SourceSummary sources={documentSources} /> : null}
          {documentWarnings.length ? <NoticeList title="Document Review Notes" items={documentWarnings} /> : null}
          <button onClick={handleExtract} disabled={loading || !background.trim()}>
            {loadingAction === "extract" ? <Loader2 className="spin" size={16} /> : <Search size={16} />}
            Extract Profile
          </button>
        </Panel>

        <Panel icon={<ClipboardCheck size={18} />} title="Profile Review">
          {profile ? (
            <textarea
              className="jsonBox"
              value={JSON.stringify(profile, null, 2)}
              onChange={(event) => {
                try {
                  setProfile(JSON.parse(event.target.value));
                  setError(null);
                } catch {
                  setError("Profile JSON is not valid yet.");
                }
              }}
            />
          ) : (
            <div className="empty">Extract a profile to review and edit it.</div>
          )}
        </Panel>

        <Panel icon={<Route size={18} />} title="Career Goal">
          <div className="goalStack">
            <label>
              Sector
              <select value={goal.target_sector ?? ""} onChange={(event) => handleSectorChange(event.target.value)}>
                {providerOptions.sectors.map((sector) => (
                  <option key={sector.value} value={sector.value}>{sector.label}</option>
                ))}
              </select>
            </label>
            <label>
              Target role
              <select value={goal.target_role} onChange={(event) => handleRoleChange(event.target.value)}>
                {selectedSector.roles.map((role) => (
                  <option key={role.value} value={role.value}>{role.label}</option>
                ))}
              </select>
            </label>
            <label>
              Specialization
              <select value={goal.target_function ?? ""} onChange={(event) => setGoal({ ...goal, target_function: event.target.value })}>
                {specializationOptions.map((specialization) => (
                  <option key={specialization.value} value={specialization.value}>{specialization.label}</option>
                ))}
              </select>
            </label>
            <label>
              Months to reach target role
              <input
                type="number"
                min="1"
                max="120"
                value={goal.horizon_months}
                onChange={(event) => setGoal({ ...goal, horizon_months: Number(event.target.value) })}
              />
            </label>
          </div>
          <button onClick={handleRun} disabled={!profile || loading}>
            {loadingAction === "plan" ? <Loader2 className="spin" size={16} /> : <Route size={16} />}
            Run Agent
          </button>
        </Panel>
      </section>

      {error && <div className="error">{error}</div>}
      {result && (
        <section className="results" id="results">
          <FeedbackGuide />
          <SkillEvidenceCheck profile={profile} result={result} />
          <ResultList title="Recommended Paths" intro="Career directions the agent thinks fit your background and goal." items={result.plan.recommended_paths.map((path) => `${displayText(path.title, "Recommended path")}: ${displayText(path.fit_summary || path.rationale, "Review the supporting evidence and next steps.")}`)} />
          <ResultList title="Strengths" items={result.plan.strengths} />
          <GapResults gaps={result.plan.gaps} />
          <NextActionResults actions={result.plan.next_actions} />
          <ProjectResults projects={result.plan.project_recommendations} />
          <EvidenceResults evidence={result.plan.evidence} profile={profile} />
          <ResultList
            title="Warnings"
            items={result.trace.fallback_events
              .map((event) => `Provider fallback: ${event}`)
              .concat(result.trace.warnings, result.plan.caveats)}
          />
          <button className="secondary traceToggle" onClick={() => setTraceOpen(!traceOpen)}>Trace</button>
          {traceOpen && <pre className="trace">{JSON.stringify(result.trace, null, 2)}</pre>}
        </section>
      )}
    </main>
  );
}

function findSector(options: ProviderOptionsResponse, value?: string | null): SectorOption | undefined {
  return options.sectors.find((sector) => sector.value === value);
}

function pickDefaultProvider(options: ProviderOptionsResponse): ProviderMode {
  const configuredDefault = options.intelligent_systems.find(
    (system) => system.provider_mode === options.default_provider_mode && system.configured
  );
  return configuredDefault?.provider_mode
    ?? options.intelligent_systems.find((system) => system.configured)?.provider_mode
    ?? "fake";
}

function findRole(sector: SectorOption, value?: string | null): RoleOption | undefined {
  return sector.roles.find((role) => role.value === value);
}

function SourceSummary({ sources }: { sources: BackgroundPromptResponse["sources"] }) {
  return (
    <div className="sourceSummary">
      <strong>Converted documents</strong>
      <ul>
        {sources.map((source) => (
          <li key={`${source.filename}-${source.character_count}`}>
            {source.filename} <span>{source.artifact_type}, {source.character_count.toLocaleString()} characters</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function NoticeList({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="noticeList">
      <strong>{title}</strong>
      <ul>{items.map((item) => <li key={item}>{item}</li>)}</ul>
    </div>
  );
}

function FeedbackGuide() {
  return (
    <article className="resultBlock guideBlock">
      <h3>How To Read This Feedback</h3>
      <dl className="definitionGrid">
        <div>
          <dt>Portfolio evidence</dt>
          <dd>Proof that you can do the role: projects, demos, GitHub repos, case studies, metrics, screenshots, or shipped work.</dd>
        </div>
        <div>
          <dt>Interview storytelling</dt>
          <dd>Your explanation of a project: problem, tools, tradeoffs, success metric, what failed, and what you improved.</dd>
        </div>
        <div>
          <dt>Dashboard</dt>
          <dd>A screen or notebook that shows inputs, outputs, metrics, results, and decisions. For AI, it can show model output, confidence, latency, and failures.</dd>
        </div>
        <div>
          <dt>Workflow</dt>
          <dd>An end-to-end process. For AI: input, preprocessing, model call, validation, result, logs/trace, and error handling.</dd>
        </div>
        <div>
          <dt>Upgrade project</dt>
          <dd>Improve an existing project so a reviewer quickly sees role-relevant skills, setup steps, tests, metrics, and results.</dd>
        </div>
      </dl>
    </article>
  );
}

function SkillEvidenceCheck({ profile, result }: { profile: CareerProfile | null; result: CareerPlanResponse }) {
  const profileText = profile ? profileTextForMatching(profile) : "";
  const requirements = Array.from(
    new Set(result.plan.evidence.map((item) => item.extracted_requirement ?? "").filter(Boolean))
  ).slice(0, 10);

  return (
    <article className="resultBlock">
      <h3>Skill Evidence Check</h3>
      <p className="sectionIntro">This compares role requirements against words already found in your profile. It is a quick signal, not a final judgment.</p>
      {requirements.length ? (
        <div className="evidenceTable">
          <div className="tableHeader">Skill or requirement</div>
          <div className="tableHeader">Demonstrated?</div>
          <div className="tableHeader">What it means</div>
          {requirements.map((requirement) => {
            const demonstrated = profileText.includes(requirement.toLowerCase());
            return (
              <React.Fragment key={requirement}>
                <div>{humanize(requirement)}</div>
                <div><span className={demonstrated ? "status yes" : "status partial"}>{demonstrated ? "Clear" : "Needs clearer proof"}</span></div>
                <div>{skillMeaning(requirement, demonstrated)}</div>
              </React.Fragment>
            );
          })}
        </div>
      ) : (
        <p>No role requirements were returned for this run.</p>
      )}
    </article>
  );
}

function GapResults({ gaps }: { gaps: CareerPlanResponse["plan"]["gaps"] }) {
  return (
    <article className="resultBlock">
      <h3>Ranked Gaps</h3>
      <p className="sectionIntro">These are the most important pieces of proof or skill evidence to strengthen first.</p>
      {gaps.length ? (
        <ul className="richList">
          {gaps.map((gap, index) => {
            const skill = displayText(gap.skill, "Target-role evidence");
            const relevance = Number.isFinite(Number(gap.relevance)) ? Number(gap.relevance) : 0;
            const evidenceCount = Number.isFinite(Number(gap.evidence_count)) ? Number(gap.evidence_count) : 0;
            return (
            <li key={`${skill}-${index}`}>
              <strong>{humanize(skill)}</strong>
              <p>{displayText(gap.reason, `Build clearer evidence for ${skill}.`)}</p>
              <span className="metaLine">Priority signal: {Math.round(relevance * 100)}% relevance from {evidenceCount} evidence item(s)</span>
            </li>
            );
          })}
        </ul>
      ) : (
        <p>No major gaps were detected from the available evidence.</p>
      )}
    </article>
  );
}

function NextActionResults({ actions }: { actions: CareerPlanResponse["plan"]["next_actions"] }) {
  return (
    <article className="resultBlock">
      <h3>Next Actions</h3>
      <p className="sectionIntro">The number is the priority order. It is not an evidence citation.</p>
      <ul className="richList">
        {actions.map((action, index) => {
          const title = displayText(action.title, "Next action");
          const priority = Number.isFinite(Number(action.priority)) ? Number(action.priority) : index + 1;
          const impact = Number.isFinite(Number(action.impact)) ? Number(action.impact) : 3;
          const effort = Number.isFinite(Number(action.effort)) ? Number(action.effort) : 3;
          const notes = Array.isArray(action.constraint_notes) ? action.constraint_notes : [];
          return (
          <li key={`${priority}-${title}-${index}`}>
            <strong>{priority}. {title}</strong>
            <p>{displayText(action.rationale, "Make the next step concrete, visible, and easy to verify.")}</p>
            {title.toLowerCase().includes("informational interviews") && (
              <p className="plainHint">Yes: this means ask working professionals, recruiters, professors, mentors, or advanced students in the field to review your resume/portfolio.</p>
            )}
            <span className="metaLine">Impact {impact}/5, effort {effort}/5</span>
            {notes.map((note, noteIndex) => <span className="metaLine" key={`${displayText(note)}-${noteIndex}`}>{displayText(note)}</span>)}
          </li>
          );
        })}
      </ul>
    </article>
  );
}

function ProjectResults({ projects }: { projects: CareerPlanResponse["plan"]["project_recommendations"] }) {
  return (
    <article className="resultBlock">
      <h3>Projects</h3>
      <p className="sectionIntro">These are portfolio ideas. A good project should show what you built, why it matters, how you tested it, and what someone can inspect.</p>
      <ul className="richList">
        {projects.map((project, index) => {
          const title = displayText(project.title, "Target-role proof project");
          const addressedGaps = Array.isArray(project.addressed_gaps) ? project.addressed_gaps : [];
          const artifacts = Array.isArray(project.expected_artifacts) ? project.expected_artifacts : [];
          return (
          <li key={`${title}-${index}`}>
            <strong>{title}</strong>
            <p>{displayText(project.description, "Create a portfolio artifact that demonstrates target-role readiness.")}</p>
            <p><span className="labelText">Helps prove:</span> {addressedGaps.map(humanize).join(", ") || "target-role readiness"}</p>
            {artifacts.length ? (
              <p><span className="labelText">What to show:</span> {artifacts.map((artifact) => displayText(artifact)).join(", ")}</p>
            ) : null}
            {project.estimated_weeks ? <span className="metaLine">Estimated time: {project.estimated_weeks} week(s)</span> : null}
          </li>
          );
        })}
      </ul>
    </article>
  );
}

function EvidenceResults({ evidence, profile }: { evidence: CareerPlanResponse["plan"]["evidence"]; profile: CareerProfile | null }) {
  const profileText = profile ? profileTextForMatching(profile) : "";
  return (
    <article className="resultBlock">
      <h3>Evidence</h3>
      <p className="sectionIntro">Evidence means the requirement or signal the agent used when judging fit. The check below shows whether your profile already clearly mentions it.</p>
      <ul className="richList">
        {evidence.map((item, index) => {
          const requirement = displayText(item.extracted_requirement ?? item.claim, "target-role readiness");
          const claim = displayText(item.claim, `${requirement} matters for the target role.`);
          const demonstrated = profileText.includes(requirement.toLowerCase());
          return (
            <li key={`${displayText(item.source_title, "evidence")}-${claim}-${index}`}>
              <strong>{humanize(requirement)}</strong>
              <p>{claim}</p>
              <span className={demonstrated ? "status yes" : "status partial"}>{demonstrated ? "Already visible in profile" : "Make this clearer in a project/resume bullet"}</span>
            </li>
          );
        })}
      </ul>
    </article>
  );
}

function Panel({ icon, title, children }: { icon: React.ReactNode; title: string; children: React.ReactNode }) {
  return (
    <section className="panel">
      <h2>{icon}{title}</h2>
      {children}
    </section>
  );
}

function ResultList({ title, items, intro }: { title: string; items: unknown[]; intro?: string }) {
  return (
    <article className="resultBlock">
      <h3>{title}</h3>
      {intro && <p className="sectionIntro">{intro}</p>}
      {items.length ? <ul>{items.map((item, index) => <li key={`${displayText(item)}-${index}`}>{displayText(item)}</li>)}</ul> : <p>No items returned.</p>}
    </article>
  );
}

function profileTextForMatching(profile: CareerProfile): string {
  return JSON.stringify(profile).toLowerCase();
}

function humanize(value: unknown): string {
  return displayText(value).replace(/[_-]/g, " ").replace(/\s+/g, " ").trim();
}

function displayText(value: unknown, fallback = ""): string {
  if (typeof value === "string") return value.trim() || fallback;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  if (value && typeof value === "object") {
    const record = value as Record<string, unknown>;
    return displayText(record.title ?? record.name ?? record.skill ?? record.claim ?? record.description, fallback);
  }
  return fallback;
}

function skillMeaning(requirement: string, demonstrated: boolean): string {
  if (demonstrated) {
    return "Your profile already mentions this. Make sure a recruiter can see where you used it.";
  }
  return "Add or rewrite a project/resume bullet so this requirement is easy to verify.";
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 102.4) / 10} KB`;
  return `${Math.round(bytes / 1024 / 102.4) / 10} MB`;
}

createRoot(document.getElementById("root")!).render(<App />);
