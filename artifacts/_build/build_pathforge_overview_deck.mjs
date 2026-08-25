import fs from "node:fs/promises";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const OUT = "F:/Github/PathForge Agent Part/artifacts/pathforge_5_min_overview.pptx";
const PREVIEW_DIR = "F:/Github/PathForge Agent Part/artifacts/_build/deck_preview";

const C = {
  ink: "#111111",
  muted: "#565D66",
  panel: "#EFEFEF",
  rule: "#B8BCC4",
  accent: "#3D8DFF",
  accentSoft: "#D9EEFF",
  teal: "#10847A",
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
    fontSize: style.fontSize ?? 24,
    bold: style.bold ?? false,
    color: style.color ?? C.ink,
    alignment: style.alignment ?? "left",
    verticalAlignment: style.verticalAlignment ?? "top",
    wrap: "square",
    ...style,
  };
  return shape;
}

function addFooter(slide, n) {
  addText(slide, `footer-${n}`, String(n).padStart(2, "0"), { left: 1184, top: 659, width: 55, height: 26 }, {
    fontSize: 13,
    alignment: "right",
    verticalAlignment: "bottom",
  });
}

function addRule(slide, x, y, w) {
  slide.shapes.add({
    geometry: "rect",
    name: "thin-rule",
    position: { left: x, top: y, width: w, height: 1.5 },
    fill: C.rule,
    line: { style: "solid", fill: C.rule, width: 0 },
  });
}

function addPanel(slide, name, position, fill = C.panel) {
  return slide.shapes.add({
    geometry: "rect",
    name,
    position,
    fill,
    line: { style: "solid", fill: C.rule, width: 1 },
  });
}

function addBulletList(slide, name, items, position, fontSize = 24) {
  addText(slide, name, items.map((item) => `• ${item}`).join("\n"), position, {
    fontSize,
    color: C.ink,
  });
}

function setNotes(slide, lines) {
  slide.speakerNotes.textFrame.setText(lines);
  slide.speakerNotes.setVisible(true);
}

function slideCover(p) {
  const slide = p.slides.add();
  slide.background.fill = C.white;
  addText(slide, "title", "PathForge AI", { left: 41, top: 42, width: 610, height: 86 }, {
    fontSize: 60,
    bold: true,
  });
  addText(slide, "subtitle", "A career-navigation website that turns messy background notes into a practical career plan.", { left: 41, top: 176, width: 560, height: 190 }, {
    fontSize: 32,
    color: C.ink,
  });
  addRule(slide, 41, 392, 410);
  addText(slide, "frame", "Purpose -> Demo -> How it works", { left: 41, top: 424, width: 560, height: 60 }, {
    fontSize: 24,
    color: C.muted,
  });
  addPanel(slide, "hero-back", { left: 658, top: 42, width: 582, height: 588 }, C.accentSoft);
  addText(slide, "hero-word-1", "upload", { left: 716, top: 115, width: 420, height: 62 }, { fontSize: 42, bold: true });
  addText(slide, "hero-word-2", "extract", { left: 756, top: 245, width: 420, height: 62 }, { fontSize: 42, bold: true, color: C.teal });
  addText(slide, "hero-word-3", "plan", { left: 818, top: 375, width: 420, height: 62 }, { fontSize: 42, bold: true, color: C.accent });
  addRule(slide, 718, 205, 382);
  addRule(slide, 758, 335, 382);
  addFooter(slide, 1);
  setNotes(slide, [
    "0:00-0:45. Open with the problem: career planning usually starts with unstructured resumes, transcripts, notes, and vague goals.",
    "Position PathForge as a practical translator from background evidence to next actions.",
  ]);
}

function slidePurpose(p) {
  const slide = p.slides.add();
  slide.background.fill = C.white;
  addText(slide, "title", "The purpose is to make career planning evidence-grounded.", { left: 41, top: 36, width: 1120, height: 105 }, {
    fontSize: 40,
    bold: true,
  });
  addPanel(slide, "left-band", { left: 41, top: 206, width: 548, height: 334 });
  addText(slide, "left-title", "What users bring", { left: 74, top: 238, width: 470, height: 42 }, { fontSize: 28, bold: true });
  addBulletList(slide, "left-list", [
    "Background documents or guided answers",
    "Target sector, role, specialization, and timeline",
    "Constraints such as time, location, or budget",
  ], { left: 74, top: 304, width: 470, height: 170 }, 23);
  addPanel(slide, "right-band", { left: 658, top: 206, width: 548, height: 334 });
  addText(slide, "right-title", "What they get", { left: 690, top: 238, width: 470, height: 42 }, { fontSize: 28, bold: true });
  addBulletList(slide, "right-list", [
    "A structured profile they can inspect",
    "Ranked gaps tied to role evidence",
    "Projects and actions that prove readiness",
  ], { left: 690, top: 304, width: 470, height: 170 }, 23);
  addFooter(slide, 2);
  setNotes(slide, [
    "0:45-1:35. The key idea is not replacing judgment. It makes the reasoning visible and editable.",
    "Emphasize that low-information inputs still produce a starting plan, but better background evidence creates a better result.",
  ]);
}

function slideDemo(p) {
  const slide = p.slides.add();
  slide.background.fill = C.white;
  addText(slide, "title", "The demo follows one user path from background to plan.", { left: 41, top: 36, width: 1120, height: 105 }, {
    fontSize: 40,
    bold: true,
  });
  const steps = [
    ["1", "Add background", "Upload a resume or answer guided questions."],
    ["2", "Extract profile", "Review education, experience, skills, projects, interests, and constraints."],
    ["3", "Choose a goal", "Pick sector, target role, specialization, and target timeline."],
    ["4", "Run agent", "Generate fit, gaps, projects, next actions, evidence, warnings, and trace."],
  ];
  for (const [i, title, body] of steps) {
    const idx = Number(i) - 1;
    const left = idx % 2 === 0 ? 41 : 658;
    const top = idx < 2 ? 196 : 420;
    addText(slide, `step-${i}-num`, i, { left, top, width: 52, height: 58 }, { fontSize: 46, bold: true, color: C.accent });
    addText(slide, `step-${i}-title`, title, { left: left + 76, top: top + 4, width: 465, height: 42 }, { fontSize: 28, bold: true });
    addText(slide, `step-${i}-body`, body, { left: left + 76, top: top + 58, width: 465, height: 86 }, { fontSize: 22, color: C.muted });
    addRule(slide, left, top + 160, 520);
  }
  addFooter(slide, 3);
  setNotes(slide, [
    "1:35-2:45. Live demo script: paste 'Harvard student interested in operations analyst roles' or upload a resume, then show the profile, goal controls, and results.",
    "Call out that results are inspectable: strengths, gaps, evidence, projects, warnings, and trace.",
  ]);
}

function slideHowItWorks(p) {
  const slide = p.slides.add();
  slide.background.fill = C.white;
  addText(slide, "title", "Under the hood, PathForge separates extraction, tools, reasoning, and verification.", { left: 41, top: 36, width: 1120, height: 105 }, {
    fontSize: 38,
    bold: true,
  });
  const blocks = [
    ["Intake", "File/text upload becomes readable background text."],
    ["Extractor", "The selected provider returns a typed profile."],
    ["Tools", "Local checks create evidence, gaps, projects, and actions."],
    ["Reasoner", "Provider synthesizes the final typed career plan."],
    ["Verifier", "Trace, caveats, warnings, latency, and fallback metadata stay visible."],
  ];
  blocks.forEach(([title, body], idx) => {
    const left = 48 + idx * 238;
    addPanel(slide, `block-${idx}`, { left, top: 224, width: 200, height: 210 }, idx === 2 ? C.accentSoft : C.panel);
    addText(slide, `block-${idx}-title`, title, { left: left + 18, top: 250, width: 164, height: 38 }, { fontSize: 25, bold: true });
    addText(slide, `block-${idx}-body`, body, { left: left + 18, top: 312, width: 164, height: 96 }, { fontSize: 17, color: C.muted });
    if (idx < blocks.length - 1) addText(slide, `arrow-${idx}`, ">", { left: left + 205, top: 306, width: 32, height: 40 }, { fontSize: 30, bold: true, color: C.accent });
  });
  addText(slide, "bottom", "Provider boundaries keep the app from depending on one model vendor, while typed schemas keep outputs renderable and testable.", { left: 92, top: 516, width: 1096, height: 72 }, { fontSize: 25, color: C.ink });
  addFooter(slide, 4);
  setNotes(slide, [
    "2:45-4:05. Explain the separation of concerns: document intake, provider-backed extraction, deterministic tools, provider-backed reasoning, and verification trace.",
    "Mention Google API first: hosted mode tries Gemini first, can fall back to OpenAI if configured, and then to the offline demo path.",
  ]);
}

function slideClose(p) {
  const slide = p.slides.add();
  slide.background.fill = C.white;
  addText(slide, "top-left", "What to remember", { left: 41, top: 42, width: 520, height: 60 }, { fontSize: 32, bold: true });
  addText(slide, "top-right", "PathForge AI", { left: 828, top: 42, width: 410, height: 60 }, { fontSize: 32, bold: true });
  addText(slide, "big", "A good career plan should show its evidence, not just its advice.", { left: 41, top: 272, width: 1030, height: 230 }, {
    fontSize: 64,
    bold: true,
    verticalAlignment: "bottom",
  });
  addText(slide, "close", "Close the demo by showing one recommended project, one ranked gap, and one trace/warning line.", { left: 41, top: 590, width: 980, height: 42 }, { fontSize: 22, color: C.muted });
  addFooter(slide, 5);
  setNotes(slide, [
    "4:05-5:00. Close by returning to purpose: the site is valuable because it turns scattered background evidence into a plan someone can critique and act on.",
    "Optional final sentence: The plan gets better as the user gives better evidence.",
  ]);
}

async function writeBlob(path, blob) {
  await fs.writeFile(path, new Uint8Array(await blob.arrayBuffer()));
}

async function main() {
  await fs.mkdir(PREVIEW_DIR, { recursive: true });
  const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
  slideCover(presentation);
  slidePurpose(presentation);
  slideDemo(presentation);
  slideHowItWorks(presentation);
  slideClose(presentation);

  for (const [index, slide] of presentation.slides.items.entries()) {
    const stem = `slide-${String(index + 1).padStart(2, "0")}`;
    await writeBlob(`${PREVIEW_DIR}/${stem}.png`, await presentation.export({ slide, format: "png", scale: 1 }));
    await fs.writeFile(`${PREVIEW_DIR}/${stem}.layout.json`, await (await slide.export({ format: "layout" })).text());
  }
  await writeBlob(`${PREVIEW_DIR}/montage.webp`, await presentation.export({ format: "webp", montage: true, scale: 1 }));
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(OUT);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
