from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

from build_prep_guide import (
    BLUE,
    INK,
    LIGHT_BLUE,
    MUTED,
    TEAL,
    add_bullet,
    add_callout,
    add_heading,
    configure_document,
    set_run_font,
)


ROOT = Path(r"C:\Users\marcu\PathForge-Agent-Part")
OUT = ROOT / "artifacts" / "presentation_package" / "Path_Forger_Project_Introduction.docx"


def add_labeled_paragraph(doc, label, text):
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(6)
    lead = paragraph.add_run(f"{label}: ")
    set_run_font(lead, bold=True, color=TEAL)
    body = paragraph.add_run(text)
    set_run_font(body, color=INK)


def build_page_one(doc):
    title = doc.add_paragraph()
    title.paragraph_format.space_before = Pt(18)
    title.paragraph_format.space_after = Pt(4)
    run = title.add_run("Path Forger")
    set_run_font(run, size=28, bold=True, color=INK)

    subtitle = doc.add_paragraph()
    subtitle.paragraph_format.space_after = Pt(14)
    run = subtitle.add_run("Project Introduction and Overview")
    set_run_font(run, size=15, color=MUTED)

    meta = doc.add_paragraph()
    meta.paragraph_format.space_after = Pt(14)
    run = meta.add_run("Marcus Vu  |  Duhvuz  |  Final demo: Friday, August 28, 2026, 1:00 PM Pacific / 4:00 PM Eastern")
    set_run_font(run, size=9.5, bold=True, color=BLUE)

    add_callout(
        doc,
        "In one sentence",
        "Path Forger turns resumes, transcripts, project notes, or guided student answers into an evidence-grounded career plan that users can inspect, edit, and act on.",
        LIGHT_BLUE,
        BLUE,
    )

    add_heading(doc, "The problem", 1)
    doc.add_paragraph(
        "Career guidance is easy to generate but difficult to trust. Background information is often scattered, goals are vague, and generic AI advice rarely shows which facts support a recommendation or what evidence a user should build next. Students, especially K-12 learners, may not have a traditional resume at all."
    )

    add_heading(doc, "The solution", 1)
    doc.add_paragraph(
        "Path Forger creates a structured, reviewable profile before it recommends anything. The user confirms a career goal, the application gathers role evidence and calculates gaps, projects, and next actions, and a reasoner synthesizes the final plan. Warnings, evidence, provider details, latency, fallback events, and routing metadata remain visible instead of being hidden behind a single answer."
    )

    add_heading(doc, "Who it serves", 1)
    for item in (
        "Students and early-career users who need help turning scattered experiences into a practical direction.",
        "K-12 learners, parents, counselors, and teachers who need school-friendly exploration without requiring a resume.",
        "Career changers who want role-specific skill gaps, portfolio projects, and prioritized next actions.",
    ):
        add_bullet(doc, item)

    add_heading(doc, "What the current application demonstrates", 1)
    for item in (
        "A focused page-based workflow: Overview, Student, Background, Profile, Goal, Results, and Review.",
        "Document or guided intake, editable profile extraction, sector/role/specialization selection, and a dedicated results page.",
        "Recommended paths, strengths, ranked gaps, projects, next actions, supporting evidence, caveats, warnings, and trace details.",
        "Hosted Gemini/OpenAI modes, local Qwen and HTTP-service contracts, hybrid fallbacks, and a deterministic offline demo mode.",
    ):
        add_bullet(doc, item)


def build_page_two(doc):
    doc.add_page_break()
    add_heading(doc, "How it works", 1)
    for label, text in (
        ("1. Intake and extraction", "A BackgroundExtractor converts documents, pasted notes, guided answers, or K-12 context into a typed profile with evidence spans, confidence, and warnings."),
        ("2. Deterministic analysis", "Local tools gather role evidence, analyze fit and skill gaps, recommend portfolio projects, and rank next actions."),
        ("3. Reasoning and verification", "A CareerReasoner produces schema-bound plan data, while verification keeps unsupported claims, caveats, warnings, and trace fields visible."),
        ("4. Review and feedback", "The user inspects the plan on a dedicated Results page and can leave a browser-saved review for product improvement."),
    ):
        add_labeled_paragraph(doc, label, text)

    add_heading(doc, "Technical design and AI usage", 1)
    doc.add_paragraph(
        "The React/Vite frontend calls a FastAPI backend with SQLite persistence. The agent orchestration depends on the BackgroundExtractor and CareerReasoner protocols rather than model-specific internals. Gemini, OpenAI, Qwen, a partner local HTTP model service, and the fake provider return compatible Pydantic structures, which keeps the core workflow testable and provider-neutral."
    )
    for item in (
        "Claude Code supported architecture planning and design/code review.",
        "OpenAI Codex supported focused implementation, debugging, tests, and documentation.",
        "Human review controlled product decisions, accepted changes, and determined what shipped.",
    ):
        add_bullet(doc, item)

    add_heading(doc, "Validation and responsible use", 1)
    doc.add_paragraph(
        "Backend tests cover schemas, deterministic tools, provider boundaries, fallbacks, verifier behavior, and API flow. The committed fake-provider evaluation uses five synthetic personas; each recorded run is schema-valid and includes six evidence citations, while the ambiguous case intentionally produces a verifier warning. These results validate the workflow and trace behavior, not real-world model accuracy."
    )

    add_heading(doc, "Current limitations and next steps", 1)
    for item in (
        "The deterministic demo is designed for repeatability, not production-quality reasoning.",
        "Hosted evidence grounding and local-model performance depend on provider configuration and hardware.",
        "Next steps include user accounts and consent controls, saved plan versions, stronger labor-market evidence, privacy hardening, and outcome-based user studies.",
    ):
        add_bullet(doc, item)

    add_callout(
        doc,
        "Demo focus",
        "In about five minutes, the demo will show the complete journey from student/background context to an editable profile, a selected goal, an evidence-grounded plan, visible trace information, and a feedback path.",
    )


def main():
    doc = Document()
    configure_document(doc)
    normal = doc.styles["Normal"]
    normal.font.size = Pt(9.5)
    normal.paragraph_format.line_spacing = 1.08
    normal.paragraph_format.space_after = Pt(4)
    for style_name in ("List Bullet", "List Number"):
        doc.styles[style_name].font.size = Pt(9.5)
        doc.styles[style_name].paragraph_format.line_spacing = 1.08
        doc.styles[style_name].paragraph_format.space_after = Pt(2)
    header = doc.sections[0].header.paragraphs[0]
    header.text = "PATH FORGER  |  PROJECT INTRODUCTION"
    header.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in header.runs:
        set_run_font(run, size=8.5, bold=True, color=MUTED)
    build_page_one(doc)
    build_page_two(doc)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
