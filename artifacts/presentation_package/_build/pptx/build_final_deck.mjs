import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "C:/Users/marcu/PathForge-Agent-Part";
const BUILD = path.join(ROOT, "artifacts/presentation_package/_build/pptx");
const OUT = path.join(ROOT, "artifacts/presentation_package/Path_Forger_Final_Presentation.pptx");
const HERO = path.join(ROOT, "artifacts/presentation_package/assets/pathforge_evidence_path_hero.png");
const PREVIEW = path.join(BUILD, "preview");
const SCREENSHOTS = {
  background: "C:/Users/marcu/Screenshots/Path Forger (AGS.Tech)/Resume uploaded and parse to description.png",
  profile: "C:/Users/marcu/Screenshots/Path Forger (AGS.Tech)/parse to json.png",
  results: "C:/Users/marcu/Screenshots/Path Forger (AGS.Tech)/Agent output.png",
};

const C = {
  ink: "#111111",
  muted: "#565D66",
  panel: "#F2F2F2",
  panelBlue: "#EAF5FB",
  rule: "#B8BCC4",
  accent: "#3D8DFF",
  teal: "#0F766E",
  tealSoft: "#E9F7F4",
  white: "#FFFFFF",
};

function addText(slide, name, text, position, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    name,
    position,
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontSize: style.fontSize ?? 22,
    typeface: "Arial",
    color: style.color ?? C.ink,
    bold: style.bold ?? false,
    alignment: style.alignment ?? "left",
    verticalAlignment: style.verticalAlignment ?? "top",
    wrap: "square",
    ...style,
  };
  return shape;
}

function addPanel(slide, name, position, fill = C.panel, line = C.rule) {
  return slide.shapes.add({
    geometry: "roundRect",
    name,
    position,
    fill,
    line: { style: "solid", fill: line, width: 1 },
  });
}

function addRule(slide, name, left, top, width, color = C.rule, thickness = 1.5) {
  slide.shapes.add({
    geometry: "rect",
    name,
    position: { left, top, width, height: thickness },
    fill: color,
    line: { style: "solid", fill: color, width: 0 },
  });
}

function addFooter(slide, n) {
  addText(slide, `footer-${n}`, String(n).padStart(2, "0"), { left: 1184, top: 659, width: 55, height: 26 }, {
    fontSize: 13,
    alignment: "right",
    verticalAlignment: "bottom",
  });
}

function setNotes(slide, script, sources) {
  const notes = [
    script.trim(),
    "",
    "[Sources]",
    ...sources.map((source) => `- ${source}`),
    "[/Sources]",
  ].join("\n");
  slide.speakerNotes.textFrame.setText(notes);
  slide.speakerNotes.setVisible(true);
}

function addCardCopy(slide, prefix, left, title, lines, options = {}) {
  const top = options.top ?? 350;
  const width = options.width ?? 581;
  addPanel(slide, `${prefix}-panel`, { left, top, width, height: options.height ?? 138 }, options.fill ?? C.panel);
  addText(slide, `${prefix}-title`, title, { left: left + 31, top: top + 24, width: width - 62, height: 44 }, {
    fontSize: options.titleSize ?? 30,
    bold: true,
    color: options.titleColor ?? C.ink,
  });
  addText(slide, `${prefix}-body`, lines.join("\n"), { left: left + 31, top: top + 152, width: width - 62, height: 118 }, {
    fontSize: options.bodySize ?? 20,
    color: C.ink,
  });
}

async function addCover(presentation) {
  const slide = presentation.slides.add();
  slide.background.fill = C.white;

  addText(slide, "cover-kicker", "PATHFORGE CAPSTONE  /  AI SUMMER SHOWDOWN", { left: 41, top: 38, width: 570, height: 32 }, {
    fontSize: 16,
    bold: true,
    color: C.teal,
  });
  addText(slide, "cover-title", "Path Forger", { left: 41, top: 104, width: 570, height: 86 }, {
    fontSize: 62,
    bold: true,
  });
  addText(slide, "cover-body", "Turns messy resumes, transcripts, and goals into an evidence-grounded career plan.", { left: 41, top: 226, width: 560, height: 182 }, {
    fontSize: 31,
  });
  addRule(slide, "cover-rule", 41, 438, 430, C.rule, 1.5);
  addText(slide, "cover-flow", "evidence  ->  gaps  ->  projects  ->  next actions", { left: 41, top: 466, width: 560, height: 60 }, {
    fontSize: 21,
    color: C.muted,
  });

  addPanel(slide, "cover-image-frame", { left: 658, top: 42, width: 582, height: 588 }, C.panelBlue);
  const bytes = await fs.readFile(HERO);
  slide.images.add({
    blob: bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength),
    contentType: "image/png",
    alt: "Abstract documents and evidence converging into a clear blue career path",
    fit: "cover",
    geometry: "roundRect",
    position: { left: 658, top: 42, width: 582, height: 588 },
  });
  addFooter(slide, 1);
  setNotes(slide, `0:00-0:25

Opening script:
"Career advice is everywhere, but most of it starts with assumptions. Path Forger starts with evidence. It turns resumes, transcripts, project notes, or guided answers into a career plan people can inspect and act on."

Delivery cue: Pause after "starts with evidence." Do not explain the architecture yet.`, [
    "Updated demo instructions - seven minutes total, approximately five minutes for the live demo, remaining time for Q&A",
    "frontend/src/main.tsx - current Path Forger product positioning",
    "Generated cover visual: original AI-generated asset created for this deck",
  ]);
}

function addProblemSolution(presentation) {
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  addText(slide, "title", "Career advice is easy to generate. Evidence is harder.", { left: 41, top: 36, width: 1197, height: 70 }, {
    fontSize: 43,
    bold: true,
  });
  addText(slide, "lead", "Most tools stop at generic suggestions. Path Forger keeps the user's facts, the reasoning trail, and the next proof-building steps visible.", { left: 42, top: 126, width: 1160, height: 126 }, {
    fontSize: 23,
    color: C.muted,
  });

  addPanel(slide, "problem-panel", { left: 42, top: 326, width: 581, height: 150 }, C.panel);
  addText(slide, "problem-title", "The problem", { left: 73, top: 354, width: 520, height: 42 }, { fontSize: 30, bold: true });
  addText(slide, "problem-body", "Scattered background\nVague career goals\nAdvice with no visible proof", { left: 73, top: 506, width: 520, height: 114 }, { fontSize: 21 });

  addPanel(slide, "solution-panel", { left: 657, top: 326, width: 581, height: 150 }, C.tealSoft, "#C8EBE3");
  addText(slide, "solution-title", "The product", { left: 688, top: 354, width: 520, height: 42 }, { fontSize: 30, bold: true, color: C.teal });
  addText(slide, "solution-body", "Inspectable profile\nRanked skill gaps\nProjects, actions, evidence, and warnings", { left: 688, top: 506, width: 520, height: 114 }, { fontSize: 21 });
  addFooter(slide, 2);
  setNotes(slide, `0:25-0:45

"The problem is not a lack of AI-generated advice. The problem is trust. During the demo, watch for three things: an editable profile, role-specific gaps and projects, and the evidence or warning behind the plan."

Scoring emphasis: originality and usefulness.`, [
    "Intern_Capstone_Scoring_Sheet.pdf - originality and usefulness criteria",
    "README.md - product purpose and architecture",
    "frontend/src/main.tsx - profile review, gaps, projects, evidence, warnings, and trace UI",
  ]);
}

async function addDemo(presentation) {
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  addText(slide, "title", "The live demo follows one user from background to an inspectable plan.", { left: 41, top: 36, width: 1197, height: 86 }, {
    fontSize: 42,
    bold: true,
  });
  const cards = [
    {
      left: 41,
      title: "1. Add evidence",
      body: "Upload or guided context becomes a readable background prompt.",
      label: "BACKGROUND",
      screenshot: SCREENSHOTS.background,
    },
    {
      left: 452,
      title: "2. Review facts",
      body: "The extracted JSON stays editable before the plan is generated.",
      label: "PROFILE",
      screenshot: SCREENSHOTS.profile,
    },
    {
      left: 865,
      title: "3. Inspect the plan",
      body: "Results connect requirements, recommended paths, evidence, and trace.",
      label: "RESULTS",
      screenshot: SCREENSHOTS.results,
    },
  ];
  for (const [i, card] of cards.entries()) {
    addPanel(slide, `demo-frame-${i}`, { left: card.left, top: 157, width: 375, height: 226 }, i === 2 ? C.panelBlue : C.panel);
    const bytes = await fs.readFile(card.screenshot);
    slide.images.add({
      blob: bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength),
      contentType: "image/png",
      alt: `${card.title}: Path Forger application screenshot`,
      fit: "cover",
      geometry: "roundRect",
      position: { left: card.left + 8, top: 165, width: 359, height: 210 },
    });
    addText(slide, `demo-label-${i}`, card.label, { left: card.left, top: 409, width: 220, height: 30 }, { fontSize: 17, bold: true, color: i === 2 ? C.accent : C.teal });
    addText(slide, `demo-title-${i}`, card.title, { left: card.left, top: 448, width: 375, height: 46 }, { fontSize: 27, bold: true, color: C.ink });
    addText(slide, `demo-body-${i}`, card.body, { left: card.left, top: 511, width: 375, height: 88 }, { fontSize: 18, color: C.muted });
  }
  addFooter(slide, 3);
  setNotes(slide, `0:45-5:45 - LIVE DEMO

Use a short synthetic background, not a real resume.

1. Start on Overview and point out the focused page navigation: Student, Background, Profile, Goal, Results, and Review.
2. Open Student and show how a K-12 learner can create usable context without a resume.
3. In Background, paste: "High school senior. Built a Python budgeting app and a robotics team website. Enjoys data, design, and helping classmates. Wants a remote-friendly technology career."
4. Click Extract Profile. Say: "The profile is editable before the agent reasons from it."
5. Choose Technology -> Data Analyst (or another configured role), a specialization, and a realistic timeline.
6. Click Run Agent. The app routes directly to the dedicated Results page.
7. Show exactly five things: recommended path, top gap, one project, evidence or warning, and provider trace.
8. Open Review briefly to show the feedback loop, then return to slide 4.

Bridge: "That is the complete loop: context, reviewed facts, a goal, an evidence-grounded plan, and a feedback path."

Fallback if the live API is slow: switch to the configured offline demo provider and repeat the same flow.`, [
    "frontend/src/main.tsx - page-based workflow, K-12 builder, input, goal, results, review, provider, and trace controls",
    "README.md - fake/offline provider mode and supported provider modes",
    "intern_capstone_project_final.pdf - presentation requires a working-app demo",
    "User-provided Path Forger screenshots - Background, Profile, and Results pages",
  ]);
}

function addArchitecture(presentation) {
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  addText(slide, "title", "Reliability comes from separating facts, tools, reasoning, and verification.", { left: 41, top: 36, width: 1197, height: 100 }, {
    fontSize: 40,
    bold: true,
  });
  const stages = [
    {
      left: 41,
      title: "Typed extraction",
      body: "A provider turns documents or guided answers into a reviewable profile with evidence spans, confidence, and warnings.",
      label: "FACTS",
    },
    {
      left: 452,
      title: "Deterministic tools",
      body: "Five local tools calculate role evidence, skill gaps, project ideas, next actions, and supporting evidence before synthesis.",
      label: "CHECKS",
    },
    {
      left: 865,
      title: "Reasoner + verifier",
      body: "The LLM produces typed JSON; verification preserves caveats, warnings, latency, fallback events, and routing trace.",
      label: "TRUST",
    },
  ];
  stages.forEach((stage, i) => {
    addPanel(slide, `arch-card-${i}`, { left: stage.left, top: 147, width: 375, height: 398 }, i === 1 ? C.tealSoft : C.panel);
    addText(slide, `arch-title-${i}`, stage.title, { left: stage.left + 32, top: 188, width: 311, height: 76 }, { fontSize: 28, bold: true, color: i === 1 ? C.teal : C.ink });
    addText(slide, `arch-body-${i}`, stage.body, { left: stage.left + 32, top: 290, width: 311, height: 190 }, { fontSize: 20, color: C.muted });
  });
  addText(slide, "provider-band", "Provider-neutral by design: Gemini  /  OpenAI  /  Qwen  /  local HTTP  /  offline demo", { left: 41, top: 584, width: 1120, height: 44 }, {
    fontSize: 22,
    bold: true,
    color: C.teal,
  });
  addFooter(slide, 5);
  setNotes(slide, `Q&A BACKUP - open only if asked about architecture or reliability.

"The application does not ask one model to do everything. First, an extractor creates a typed profile. Second, deterministic tools calculate evidence, gaps, projects, and actions. Third, a reasoner synthesizes the plan, and a verifier checks what should be shown as a warning or caveat."

"Because extraction and reasoning are protocols, I can use Gemini, OpenAI, local Qwen, a partner HTTP model service, or the offline demo without changing the app's core logic."

Keep this explanation high-level; do not read every provider name slowly.`, [
    "README.md - architecture, provider modes, and local MoLE HTTP contract",
    "backend/app/agent/orchestrator.py - tool orchestration and trace preservation",
    "backend/app/providers/base.py - BackgroundExtractor and CareerReasoner protocols",
    "backend/app/agent/verifier.py - verifier behavior",
  ]);
}

function addAiProwess(presentation) {
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  addText(slide, "title", "Two kinds of AI made the project stronger.", { left: 41, top: 36, width: 1197, height: 70 }, {
    fontSize: 43,
    bold: true,
  });
  addText(slide, "lead", "Development agents helped plan, implement, review, and test the system. Runtime models power the user experience behind stable protocols and schemas.", { left: 42, top: 126, width: 1160, height: 126 }, {
    fontSize: 23,
    color: C.muted,
  });

  addPanel(slide, "dev-panel", { left: 42, top: 326, width: 581, height: 150 }, C.panel);
  addText(slide, "dev-title", "Development workflow", { left: 73, top: 354, width: 520, height: 42 }, { fontSize: 29, bold: true });
  addText(slide, "dev-body", "Claude Code: architecture + review\nOpenAI Codex: implementation + tests\nHuman: product decisions + acceptance", { left: 73, top: 506, width: 520, height: 114 }, { fontSize: 20 });

  addPanel(slide, "runtime-panel", { left: 657, top: 326, width: 581, height: 150 }, C.panelBlue, "#C7DFF2");
  addText(slide, "runtime-title", "Runtime intelligence", { left: 688, top: 354, width: 520, height: 42 }, { fontSize: 29, bold: true, color: C.accent });
  addText(slide, "runtime-body", "Gemini / OpenAI / Qwen behind protocols\nSchema-bound JSON\nEvidence, warnings, trace + fallback", { left: 688, top: 506, width: 520, height: 114 }, { fontSize: 20 });
  addFooter(slide, 6);
  setNotes(slide, `Q&A BACKUP - open only if asked about AI usage, testing, or provider choices.

"The capstone required two development agents, so I separated their jobs. Claude Code was used for architecture and review. OpenAI Codex was used for focused implementation, debugging, tests, and documentation. I stayed responsible for the product decisions and what actually shipped."

"Inside the app, the direct LLM integration is also provider-neutral. Gemini, OpenAI, and Qwen all have to return the same typed structures. That lets the app validate outputs and keep trace fields instead of trusting free-form text."

Optional proof point if asked: the committed fake-provider evaluation covers five synthetic personas, each with five tool calls and six evidence citations; the ambiguous case intentionally surfaces a verifier warning.

Important: If your actual agent split differed, update this slide and AI_PROMPTS.md before presenting.`, [
    "intern_capstone_project_final.pdf - two-agent development workflow and direct LLM API requirements",
    "AI_PROMPTS.md - development agent roles and runtime prompts",
    "backend/evaluation/results.json - committed deterministic evaluation snapshot",
    "backend/tests - schema, provider, fallback, verifier, tool, and API tests",
  ]);
}

function addClose(presentation) {
  const slide = presentation.slides.add();
  slide.background.fill = C.white;
  addText(slide, "close-kicker", "QUESTIONS", { left: 41, top: 42, width: 330, height: 48 }, {
    fontSize: 24,
    bold: true,
    color: C.teal,
  });
  addText(slide, "close-thesis", "A career plan should show its evidence, not just its advice.", { left: 41, top: 178, width: 1050, height: 270 }, {
    fontSize: 68,
    bold: true,
    verticalAlignment: "bottom",
  });
  addText(slide, "close-steps", "Upload.  Extract.  Choose.  Verify.", { left: 41, top: 520, width: 720, height: 58 }, {
    fontSize: 28,
    color: C.muted,
  });
  addText(slide, "close-brand", "Path Forger", { left: 840, top: 525, width: 398, height: 58 }, {
    fontSize: 30,
    bold: true,
    alignment: "right",
  });
  addFooter(slide, 4);
  setNotes(slide, `5:45-7:00 - CLOSE AND Q&A

Closing script:
"Path Forger is useful because it does more than produce an answer. It shows the profile it extracted, the evidence it used, the gaps it found, and the projects and actions that can close those gaps. A good career plan should show its evidence, not just its advice."

Final sentence: "That is the difference between a chatbot response and a plan someone can actually critique, improve, and follow."

Stop. Look at the evaluators. Invite questions.`, [
    "README.md - project purpose",
    "Intern_Capstone_Scoring_Sheet.pdf - usefulness and presentation criteria",
  ]);
}

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

async function main() {
  await fs.mkdir(PREVIEW, { recursive: true });
  const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
  await addCover(presentation);
  addProblemSolution(presentation);
  await addDemo(presentation);
  addClose(presentation);
  addArchitecture(presentation);
  addAiProwess(presentation);

  for (const [index, slide] of presentation.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    await writeBlob(path.join(PREVIEW, `${stem}.png`), await presentation.export({ slide, format: "png", scale: 1 }));
    await fs.writeFile(path.join(PREVIEW, `${stem}.layout.json`), await (await slide.export({ format: "layout" })).text());
  }
  await writeBlob(path.join(PREVIEW, "montage.webp"), await presentation.export({ format: "webp", montage: true, scale: 1 }));
  const inspect = await presentation.inspect({ kind: "slide,textbox,shape,image,notes", maxChars: 30000 });
  await fs.writeFile(path.join(BUILD, "final-inspect.ndjson"), inspect.ndjson);
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(OUT);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
