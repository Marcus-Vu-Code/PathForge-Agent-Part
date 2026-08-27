from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Spacer


ROOT = Path(r"C:\Users\marcu\PathForge-Agent-Part")
OUT = ROOT / "artifacts" / "presentation_package" / "Path_Forger_Project_Introduction.pdf"

INK = colors.HexColor("#111111")
MUTED = colors.HexColor("#565D66")
TEAL = colors.HexColor("#0F766E")
BLUE = colors.HexColor("#3D8DFF")
PALE_BLUE = colors.HexColor("#EAF5FB")
RULE = colors.HexColor("#B8BCC4")


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.75 * inch, 10.55 * inch, "PATH FORGER  |  PROJECT INTRODUCTION")
    canvas.setStrokeColor(RULE)
    canvas.line(0.75 * inch, 10.42 * inch, 7.75 * inch, 10.42 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(7.75 * inch, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("TitlePF", parent=base["Title"], fontName="Helvetica-Bold", fontSize=25, leading=28, textColor=INK, alignment=TA_LEFT, spaceAfter=4),
        "subtitle": ParagraphStyle("SubPF", parent=base["Normal"], fontName="Helvetica", fontSize=14, leading=17, textColor=MUTED, spaceAfter=10),
        "meta": ParagraphStyle("MetaPF", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=BLUE, spaceAfter=10),
        "h1": ParagraphStyle("H1PF", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=13.5, leading=16, textColor=TEAL, spaceBefore=6, spaceAfter=4),
        "body": ParagraphStyle("BodyPF", parent=base["BodyText"], fontName="Helvetica", fontSize=9.2, leading=11.7, textColor=INK, spaceAfter=4),
        "bullet": ParagraphStyle("BulletPF", parent=base["BodyText"], fontName="Helvetica", fontSize=9, leading=11.4, textColor=INK, leftIndent=16, firstLineIndent=-8, bulletIndent=6, spaceAfter=2),
        "callout": ParagraphStyle("CalloutPF", parent=base["BodyText"], fontName="Helvetica", fontSize=9.5, leading=12, textColor=INK, borderColor=RULE, borderWidth=0.7, borderPadding=7, backColor=PALE_BLUE, spaceBefore=3, spaceAfter=5),
    }


def bullet(flow, style, text):
    flow.append(Paragraph(text, style, bulletText="•"))


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(OUT), pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch, topMargin=0.72 * inch, bottomMargin=0.65 * inch, title="Path Forger Project Introduction", author="Marcus Vu")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="intro", frames=frame, onPage=header_footer)])
    s = styles()
    flow = []

    flow.append(Spacer(1, 10))
    flow.append(Paragraph("Path Forger", s["title"]))
    flow.append(Paragraph("Project Introduction and Overview", s["subtitle"]))
    flow.append(Paragraph("Marcus Vu &nbsp;|&nbsp; Duhvuz &nbsp;|&nbsp; Final demo: Friday, August 28, 2026, 1:00 PM Pacific / 4:00 PM Eastern", s["meta"]))
    flow.append(Paragraph("<b><font color='#3D8DFF'>In one sentence:</font></b> Path Forger turns resumes, transcripts, project notes, or guided student answers into an evidence-grounded career plan that users can inspect, edit, and act on.", s["callout"]))

    flow.append(Paragraph("The problem", s["h1"]))
    flow.append(Paragraph("Career guidance is easy to generate but difficult to trust. Background information is often scattered, goals are vague, and generic AI advice rarely shows which facts support a recommendation or what evidence a user should build next. Students, especially K-12 learners, may not have a traditional resume at all.", s["body"]))
    flow.append(Paragraph("The solution", s["h1"]))
    flow.append(Paragraph("Path Forger creates a structured, reviewable profile before it recommends anything. The user confirms a career goal, the application gathers role evidence and calculates gaps, projects, and next actions, and a reasoner synthesizes the final plan. Warnings, evidence, provider details, latency, fallback events, and routing metadata remain visible.", s["body"]))
    flow.append(Paragraph("Who it serves", s["h1"]))
    bullet(flow, s["bullet"], "Students and early-career users turning scattered experiences into a practical direction.")
    bullet(flow, s["bullet"], "K-12 learners, parents, counselors, and teachers who need school-friendly exploration without requiring a resume.")
    bullet(flow, s["bullet"], "Career changers who want role-specific skill gaps, portfolio projects, and prioritized next actions.")
    flow.append(Paragraph("What the current application demonstrates", s["h1"]))
    bullet(flow, s["bullet"], "A focused page-based workflow: Overview, Student, Background, Profile, Goal, Results, and Review.")
    bullet(flow, s["bullet"], "Document or guided intake, editable extraction, sector/role/specialization selection, and dedicated results.")
    bullet(flow, s["bullet"], "Paths, strengths, ranked gaps, projects, next actions, evidence, caveats, warnings, and trace details.")
    bullet(flow, s["bullet"], "Gemini/OpenAI modes, local Qwen and HTTP-service contracts, hybrid fallbacks, and an offline demo mode.")

    flow.append(PageBreak())
    flow.append(Paragraph("How it works", s["h1"]))
    flow.append(Paragraph("<b>1. Intake and extraction:</b> A BackgroundExtractor converts documents, pasted notes, guided answers, or K-12 context into a typed profile with evidence spans, confidence, and warnings.", s["body"]))
    flow.append(Paragraph("<b>2. Deterministic analysis:</b> Local tools gather role evidence, analyze fit and skill gaps, recommend portfolio projects, and rank next actions.", s["body"]))
    flow.append(Paragraph("<b>3. Reasoning and verification:</b> A CareerReasoner produces schema-bound plan data, while verification keeps unsupported claims, caveats, warnings, and trace fields visible.", s["body"]))
    flow.append(Paragraph("<b>4. Review and feedback:</b> The user inspects the plan on a dedicated Results page and can leave a browser-saved review for product improvement.", s["body"]))

    flow.append(Paragraph("Technical design and AI usage", s["h1"]))
    flow.append(Paragraph("The React/Vite frontend calls a FastAPI backend with SQLite persistence. Agent orchestration depends on the BackgroundExtractor and CareerReasoner protocols. Gemini, OpenAI, Qwen, a local HTTP service, and the fake provider return compatible Pydantic structures, keeping the workflow testable and provider-neutral.", s["body"]))
    bullet(flow, s["bullet"], "Claude Code supported architecture planning and design/code review.")
    bullet(flow, s["bullet"], "OpenAI Codex supported focused implementation, debugging, tests, and documentation.")
    bullet(flow, s["bullet"], "Human review controlled product decisions, accepted changes, and determined what shipped.")

    flow.append(Paragraph("Validation and responsible use", s["h1"]))
    flow.append(Paragraph("Backend tests cover schemas, tools, provider boundaries, fallbacks, verifier behavior, and API flow. The fake-provider evaluation uses five synthetic personas; each run is schema-valid with six evidence citations, while the ambiguous case produces a verifier warning. This validates workflow and trace behavior, not real-world model accuracy.", s["body"]))

    flow.append(Paragraph("Demo focus", s["h1"]))
    flow.append(Paragraph("In about five minutes, the demo will show the journey from student/background context to an editable profile, a selected goal, an evidence-grounded plan, visible trace information, and a feedback path.", s["body"]))

    doc.build(flow)
    print(OUT)


if __name__ == "__main__":
    main()
