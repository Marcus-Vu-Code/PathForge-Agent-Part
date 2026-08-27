from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas


ROOT = Path(r"C:\Users\marcu\PathForge-Agent-Part")
OUT = ROOT / "artifacts" / "presentation_package" / "Career_GPS_AI_Printable_Note_Cards.pdf"

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
        "time": "0:00-0:35",
        "title": "Open with evidence",
        "say": "Career advice is everywhere, but most of it starts with assumptions. Career GPS AI starts with evidence. It turns resumes, transcripts, project notes, or guided answers into a career plan users can inspect and act on.",
        "cues": ["Pause after: starts with evidence.", "Do not explain architecture yet."],
    },
    {
        "slide": "2",
        "time": "0:35-1:10",
        "title": "Define the difference",
        "say": "The problem is not a lack of AI advice. The problem is trust. Users need to see what the system learned, what is missing for a target role, and what they can build next to prove readiness.",
        "cues": ["Point: problem -> product.", "Transition: Let me show you the loop."],
    },
    {
        "slide": "3",
        "time": "1:10-2:40",
        "title": "Run the 90-second demo",
        "say": "Use a synthetic background. Extract the editable profile, choose a direction, run the agent, then show exactly one recommended path, one top gap, one project, and one trace or warning.",
        "cues": ["Do not narrate loading.", "Stop the demo at 2:40.", "Bridge: Why is this dependable?"],
    },
    {
        "slide": "4",
        "time": "2:40-3:30",
        "title": "Explain reliability",
        "say": "First, typed extraction creates a reviewable profile. Second, five deterministic tools calculate evidence, gaps, projects, and actions. Third, the reasoner and verifier preserve warnings, caveats, latency, fallback events, and routing trace.",
        "cues": ["Use the three columns as rhythm.", "Provider-neutral: Gemini, OpenAI, Qwen, local, offline."],
    },
    {
        "slide": "5",
        "time": "3:30-4:25",
        "title": "Prove AI and technical depth",
        "say": "Claude Code supported architecture and review. OpenAI Codex supported implementation, debugging, tests, and documentation. Runtime models return the same schema-bound structures behind provider protocols. Human decisions controlled what shipped.",
        "cues": ["Name both agents clearly.", "Verify this matches your real workflow."],
    },
    {
        "slide": "6",
        "time": "4:25-5:00",
        "title": "Close on the thesis",
        "say": "Career GPS AI shows the profile, evidence, gaps, projects, actions, and warnings behind a plan. A good career plan should show its evidence, not just its advice. That is the difference between a chatbot response and a plan someone can critique, improve, and follow.",
        "cues": ["Slow down on the thesis.", "Stop. Look up. Invite questions."],
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
    c.setTitle("Career GPS AI Printable Note Cards")
    c.setAuthor("Career GPS AI presentation package")
    for page_index, card in enumerate(CARDS):
        draw_card(c, card, MARGIN_X, MARGIN_Y, CARD_W, CARD_H, TEAL if page_index % 2 == 0 else BLUE)
        c.showPage()
    c.save()
    print(OUT)


if __name__ == "__main__":
    main()
