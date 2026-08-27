from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas


ROOT = Path(r"C:\Users\marcu\PathForge-Agent-Part")
OUT = ROOT / "artifacts" / "presentation_package" / "Path_Forger_Printable_Note_Cards.pdf"

PAGE_W, PAGE_H = 5 * inch, 3 * inch
MARGIN_X = 0.10 * inch
MARGIN_Y = 0.10 * inch
CARD_W = PAGE_W - 2 * MARGIN_X
CARD_H = PAGE_H - 2 * MARGIN_Y

INK = colors.HexColor("#111111")
MUTED = colors.HexColor("#565D66")
TEAL = colors.HexColor("#0F766E")
BLUE = colors.HexColor("#3D8DFF")
PALE = colors.HexColor("#F2F4F7")
PALE_BLUE = colors.HexColor("#EAF5FB")
RULE = colors.HexColor("#B8BCC4")


CARDS = [
    {
        "slide": "1",
        "time": "0:00-0:25",
        "title": "Open with evidence",
        "say": "Career advice is everywhere, but most of it starts with assumptions. Path Forger starts with evidence. It turns resumes, transcripts, project notes, or guided answers into a career plan people can inspect and act on.",
        "cues": ["Pause after: starts with evidence.", "Do not explain architecture yet."],
    },
    {
        "slide": "2",
        "time": "0:25-0:45",
        "title": "Tell them what to watch",
        "say": "The problem is trust. During the demo, watch for three things: an editable profile, role-specific gaps and projects, and the evidence or warning behind the plan.",
        "cues": ["Keep this to 20 seconds.", "Transition: Let me show you the loop."],
    },
    {
        "slide": "3",
        "time": "0:45-3:15",
        "title": "Demo: context to run",
        "say": "Show Overview and Student briefly. Apply the synthetic student context, review the Background page, extract the editable Profile, then choose Technology, Data Analyst, a specialization, and a realistic timeline. Run the agent.",
        "cues": ["Narrate decisions, not clicks.", "Profile visible by 2:15.", "Agent running by 3:15."],
    },
    {
        "slide": "3",
        "time": "3:15-5:45",
        "title": "Demo: inspect the proof",
        "say": "On Results, show one recommended path, the top ranked gap, one portfolio project, supporting evidence or warning, and the provider trace. Open Review briefly, then return to slide 4.",
        "cues": ["Do not read every result.", "Trace visible by 5:15.", "Return to deck at 5:45."],
    },
    {
        "slide": "4",
        "time": "5:45-7:00",
        "title": "Close and take questions",
        "say": "Path Forger shows the profile, evidence, gaps, projects, actions, warnings, and trace behind a plan. A good career plan should show its evidence, not just its advice. I am happy to answer questions.",
        "cues": ["Slow down on the thesis.", "Use backup slides only if asked."],
    },
    {
        "slide": "5-6",
        "time": "Q&A BACKUP",
        "title": "Technical answer bank",
        "say": "Architecture: typed extraction, deterministic tools, then reasoner and verifier. Provider-neutral protocols support Gemini, OpenAI, Qwen, local HTTP, and offline demo. AI workflow: Claude Code for architecture/review; Codex for implementation/tests/docs; human approval for what shipped.",
        "cues": ["Answer the question first.", "Then open only the relevant backup slide."],
    },
]


def draw_wrapped_paragraph(c, text, x, y_top, width, style):
    para = Paragraph(text, style)
    _, height = para.wrap(width, 1000)
    para.drawOn(c, x, y_top - height)
    return y_top - height


def draw_card(c, card, x, y, w, h, accent):
    c.setFillColor(colors.white)
    c.setStrokeColor(RULE)
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, 10, fill=1, stroke=1)

    c.setFillColor(PALE_BLUE if accent == BLUE else PALE)
    c.roundRect(x, y + h - 0.64 * inch, w, 0.64 * inch, 10, fill=1, stroke=0)
    c.rect(x, y + h - 0.64 * inch, w, 0.18 * inch, fill=1, stroke=0)

    c.setFillColor(accent)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(x + 0.22 * inch, y + h - 0.23 * inch, f"SLIDE {card['slide']}  |  {card['time']}")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(x + 0.22 * inch, y + h - 0.50 * inch, card["title"])

    say_style = ParagraphStyle(
        "say",
        fontName="Helvetica",
        fontSize=8.7,
        leading=10.8,
        textColor=INK,
        spaceAfter=0,
    )
    cue_style = ParagraphStyle(
        "cue",
        fontName="Helvetica-Bold",
        fontSize=7.7,
        leading=9.2,
        textColor=MUTED,
    )

    body_x = x + 0.22 * inch
    body_w = w - 0.44 * inch
    cursor = y + h - 0.83 * inch
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(body_x, cursor, "SAY")
    cursor -= 0.10 * inch
    cursor = draw_wrapped_paragraph(c, card["say"], body_x, cursor, body_w, say_style)
    cursor -= 0.11 * inch
    c.setStrokeColor(RULE)
    c.line(body_x, cursor, body_x + body_w, cursor)
    cursor -= 0.12 * inch
    c.setFillColor(MUTED)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(body_x, cursor, "CUES")
    cursor -= 0.10 * inch
    cue_text = "<br/>".join([f"- {cue}" for cue in card["cues"]])
    draw_wrapped_paragraph(c, cue_text, body_x, cursor, body_w, cue_style)


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=(PAGE_W, PAGE_H))
    c.setTitle("Path Forger Printable Note Cards")
    c.setAuthor("Path Forger presentation package")
    for page_index, card in enumerate(CARDS):
        draw_card(c, card, MARGIN_X, MARGIN_Y, CARD_W, CARD_H, TEAL if page_index % 2 == 0 else BLUE)
        c.showPage()
    c.save()
    print(OUT)


if __name__ == "__main__":
    main()
