from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(r"C:\Users\marcu\PathForge-Agent-Part")
OUT = ROOT / "artifacts" / "presentation_package" / "Career_GPS_AI_Presentation_Prep_Guide.docx"

INK = RGBColor(17, 17, 17)
MUTED = RGBColor(86, 93, 102)
TEAL = RGBColor(15, 118, 110)
BLUE = RGBColor(61, 141, 255)
LIGHT_BLUE = "EAF5FB"
LIGHT_TEAL = "E9F7F4"
LIGHT_GRAY = "F2F4F7"
RULE = "B8BCC4"


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=100, start=120, bottom=100, end=120):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{side}"))
        if node is None:
            node = OxmlElement(f"w:{side}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_geometry(table, widths_dxa, indent_dxa=120):
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(sum(widths_dxa)))
    tbl_w.set(qn("w:type"), "dxa")
    tbl_ind = tbl_pr.find(qn("w:tblInd"))
    if tbl_ind is None:
        tbl_ind = OxmlElement("w:tblInd")
        tbl_pr.append(tbl_ind)
    tbl_ind.set(qn("w:w"), str(indent_dxa))
    tbl_ind.set(qn("w:type"), "dxa")
    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in widths_dxa:
        col = OxmlElement("w:gridCol")
        col.set(qn("w:w"), str(width))
        grid.append(col)
    for row in table.rows:
        for index, cell in enumerate(row.cells):
            width = widths_dxa[index]
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(width))
            tc_w.set(qn("w:type"), "dxa")
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def set_run_font(run, size=None, bold=None, color=None, italic=None, name="Calibri"):
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run("Page ")
    set_run_font(run, size=9, color=MUTED)
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    paragraph._p.append(fld)


def add_heading(doc, text, level=1):
    p = doc.add_paragraph(text, style=f"Heading {level}")
    return p


def add_bullet(doc, text, bold_lead=None):
    p = doc.add_paragraph(style="List Bullet")
    if bold_lead and text.startswith(bold_lead):
        lead = p.add_run(bold_lead)
        set_run_font(lead, bold=True)
        rest = p.add_run(text[len(bold_lead):])
        set_run_font(rest)
    else:
        run = p.add_run(text)
        set_run_font(run)
    return p


def add_number(doc, text):
    p = doc.add_paragraph(style="List Number")
    run = p.add_run(text)
    set_run_font(run)
    return p


def add_callout(doc, label, text, fill=LIGHT_TEAL, accent=TEAL):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.08)
    p.paragraph_format.right_indent = Inches(0.08)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(10)
    p_pr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    p_pr.append(shd)
    p_bdr = OxmlElement("w:pBdr")
    for edge in ("top", "left", "bottom", "right"):
        node = OxmlElement(f"w:{edge}")
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), "6")
        node.set(qn("w:color"), RULE)
        node.set(qn("w:space"), "5")
        p_bdr.append(node)
    p_pr.append(p_bdr)
    lead = p.add_run(f"{label}: ")
    set_run_font(lead, bold=True, color=accent)
    body = p.add_run(text)
    set_run_font(body)


def format_table(table, header_fill=LIGHT_BLUE, font_size=9.5):
    header_tr_pr = table.rows[0]._tr.get_or_add_trPr()
    header_flag = OxmlElement("w:tblHeader")
    header_flag.set(qn("w:val"), "true")
    header_tr_pr.append(header_flag)
    for row_index, row in enumerate(table.rows):
        for cell in row.cells:
            if row_index == 0:
                set_cell_shading(cell, header_fill)
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.05
                for run in p.runs:
                    set_run_font(run, size=font_size, bold=(row_index == 0), color=INK)


def configure_document(doc):
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.right_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    normal.font.size = Pt(11)
    normal.font.color.rgb = INK
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.25

    heading_tokens = {
        "Heading 1": (16, TEAL, 18, 10),
        "Heading 2": (13, TEAL, 14, 7),
        "Heading 3": (12, RGBColor(31, 77, 120), 10, 5),
    }
    for style_name, (size, color, before, after) in heading_tokens.items():
        style = doc.styles[style_name]
        style.font.name = "Calibri"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = color
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True

    for style_name in ("List Bullet", "List Number"):
        style = doc.styles[style_name]
        style.font.name = "Calibri"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
        style.font.size = Pt(11)
        style.paragraph_format.left_indent = Inches(0.375)
        style.paragraph_format.first_line_indent = Inches(-0.188)
        style.paragraph_format.space_after = Pt(4)
        style.paragraph_format.line_spacing = 1.25

    header = section.header
    hp = header.paragraphs[0]
    hp.text = "CAREER GPS AI  |  PRESENTATION PREP"
    hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in hp.runs:
        set_run_font(run, size=8.5, bold=True, color=MUTED)

    footer = section.footer
    fp = footer.paragraphs[0]
    add_page_number(fp)


def build_cover(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(82)
    p.paragraph_format.space_after = Pt(16)
    r = p.add_run("PRESENTATION PREP GUIDE")
    set_run_font(r, size=11, bold=True, color=TEAL)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run("Career GPS AI")
    set_run_font(r, size=30, bold=True, color=INK)

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(28)
    r = p.add_run("PathForge capstone - AI Summer Showdown")
    set_run_font(r, size=15, color=MUTED)

    add_callout(doc, "Five-minute thesis", "A career plan should show its evidence, not just its advice.", LIGHT_BLUE, BLUE)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(28)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("This packet includes")
    set_run_font(r, size=13, bold=True, color=INK)
    for item in (
        "A rubric-aligned presentation strategy",
        "A slide-by-slide run of show and full speaking script",
        "A live-demo checklist with offline fallback",
        "Likely evaluator questions and concise answers",
        "A final rehearsal and submission checklist",
    ):
        add_bullet(doc, item)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(48)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("Prepared from the capstone guidelines, scoring sheet, current repository, committed evaluation results, and final presentation deck.")
    set_run_font(r, size=9.5, italic=True, color=MUTED)
    doc.add_page_break()


def build_strategy(doc):
    add_heading(doc, "1. What the presentation must accomplish", 1)
    p = doc.add_paragraph("By the end of five minutes, peer and mentor evaluators should believe that Career GPS AI is useful, technically thoughtful, and meaningfully different because it makes career recommendations evidence-grounded and inspectable.")
    p.paragraph_format.space_after = Pt(8)
    add_callout(doc, "Presentation rule", "Do not spend the demo proving every feature. Prove one complete user journey and one trustworthy recommendation.")

    add_heading(doc, "Rubric strategy", 2)
    table = doc.add_table(rows=1, cols=4)
    headers = ["Criterion", "Weight", "A 5 requires", "Proof to show"]
    for i, value in enumerate(headers):
        table.cell(0, i).text = value
    rows = [
        ("Originality", "25%", "A novel problem or unexpected approach", "Evidence-first career planning; editable profile; visible trace"),
        ("AI & Tech Prowess", "30%", "Strategic 2+ agent workflow, direct LLM integration, clean architecture", "Claude Code + Codex roles; provider protocols; schemas; verifier; fallbacks"),
        ("Usefulness", "25%", "A genuine, high-impact, production-oriented solution", "Real inputs; role-specific gaps; projects and actions; safe offline demo"),
        ("Presentation", "20%", "Clear, engaging, well-paced, flawless live demo", "Six-slide arc; 90-second demo; rehearsed fallback; memorable close"),
    ]
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = value
    set_table_geometry(table, [1800, 900, 3600, 3060])
    format_table(table, LIGHT_BLUE, 9.2)

    add_heading(doc, "The three sentences to memorize", 2)
    for line in (
        "Career advice is easy to generate; evidence is harder.",
        "Career GPS AI shows the profile, gaps, projects, actions, evidence, and warnings behind a plan.",
        "A good career plan should show its evidence, not just its advice.",
    ):
        add_number(doc, line)


def build_run_of_show(doc):
    add_heading(doc, "2. Five-minute run of show", 1)
    table = doc.add_table(rows=1, cols=4)
    for i, value in enumerate(("Slide", "Time", "Job", "Proof point")):
        table.cell(0, i).text = value
    rows = [
        ("1", "0:00-0:35", "Open with the trust problem", "Messy evidence becomes an inspectable plan"),
        ("2", "0:35-1:10", "Define the product difference", "Facts, evidence, gaps, projects, warnings"),
        ("3", "1:10-2:40", "Run the live demo", "Input -> goal -> inspect output and trace"),
        ("4", "2:40-3:30", "Explain the architecture", "Extraction -> tools -> reasoner/verifier"),
        ("5", "3:30-4:25", "Prove AI and technical depth", "Claude + Codex; Gemini/OpenAI/Qwen; schemas"),
        ("6", "4:25-5:00", "Resolve the opening", "Evidence, not just advice"),
    ]
    for row in rows:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cells[i].text = value
    set_table_geometry(table, [720, 1320, 2760, 4560])
    format_table(table, LIGHT_TEAL, 9.3)

    add_heading(doc, "Pacing checkpoints", 2)
    add_bullet(doc, "At 1:10, you should begin clicking in the app.")
    add_bullet(doc, "At 2:40, stop the demo even if you could show more.")
    add_bullet(doc, "At 3:30, explicitly name both development agents.")
    add_bullet(doc, "At 4:25, start the final slide and slow down.")
    add_bullet(doc, "At 4:55, finish the final sentence and stop speaking.")


def add_script_section(doc, slide_no, title, timing, script, cues):
    add_heading(doc, f"Slide {slide_no} - {title}", 2)
    p = doc.add_paragraph()
    r = p.add_run(f"Timing: {timing}")
    set_run_font(r, bold=True, color=TEAL)
    quote = doc.add_paragraph()
    quote.paragraph_format.left_indent = Inches(0.25)
    quote.paragraph_format.right_indent = Inches(0.2)
    quote.paragraph_format.space_after = Pt(8)
    r = quote.add_run(f'"{script}"')
    set_run_font(r, italic=True, color=INK)
    for cue in cues:
        add_bullet(doc, cue)


def build_script(doc):
    add_heading(doc, "3. Full speaking script", 1)
    add_script_section(
        doc, 1, "Career GPS AI", "0:00-0:35",
        "Career advice is everywhere, but most of it starts with assumptions. Career GPS AI starts with evidence. It takes the messy material people already have - resumes, transcripts, project notes, or guided answers - and turns it into a career plan they can inspect and act on.",
        ["Pause after 'starts with evidence.'", "Do not explain the architecture yet."],
    )
    add_script_section(
        doc, 2, "Evidence is harder", "0:35-1:10",
        "The problem is not a lack of AI-generated advice. The problem is trust. Users need to see what the system learned from their background, what is missing for a target role, and what they can build next to prove readiness. Career GPS AI makes that chain inspectable instead of hiding it behind one answer.",
        ["Point once to the problem side and once to the product side.", "Transition directly into the app: 'Let me show you the loop.'"],
    )
    add_script_section(
        doc, 3, "Live demo", "1:10-2:40",
        "I will use a short synthetic background so no private resume data is exposed. First I add evidence. The system extracts a profile that I can review and edit. Then I choose a target direction and run the agent. The output gives me a recommended path, the most important gap, a project that can prove readiness, and the evidence or warning behind that recommendation.",
        ["Click while speaking; do not narrate loading indicators.", "Show four outputs only: path, top gap, project, trace/warning.", "End with: 'Now here is why this is more dependable than a single prompt.'"],
    )
    add_script_section(
        doc, 4, "Architecture", "2:40-3:30",
        "The application does not ask one model to do everything. First, an extractor creates a typed profile. Second, five deterministic tools calculate evidence, gaps, projects, and actions. Third, a reasoner synthesizes the plan, and a verifier preserves warnings, caveats, latency, fallback events, and routing trace. Because extraction and reasoning are protocols, the app can use Gemini, OpenAI, local Qwen, a partner HTTP model service, or the offline demo without changing its core logic.",
        ["Use the three columns as your speaking rhythm.", "Do not list every API route or test file."],
    )
    add_script_section(
        doc, 5, "Two kinds of AI", "3:30-4:25",
        "The capstone required two development agents, so I separated their jobs. Claude Code supported architecture and review. OpenAI Codex supported focused implementation, debugging, tests, and documentation. I stayed responsible for product decisions and what shipped. Inside the app, the direct LLM integration is provider-neutral. Gemini, OpenAI, and Qwen all have to return the same typed structures, which lets the app validate outputs and preserve trace fields instead of trusting free-form text.",
        ["Name both agents clearly.", "Before presenting, change this wording if your actual agent split was different."],
    )
    add_script_section(
        doc, 6, "What to remember", "4:25-5:00",
        "Career GPS AI is useful because it does more than produce an answer. It shows the profile it extracted, the evidence it used, the gaps it found, and the projects and actions that can close those gaps. A good career plan should show its evidence, not just its advice. That is the difference between a chatbot response and a plan someone can actually critique, improve, and follow.",
        ["Slow down on the thesis sentence.", "Stop after the final sentence, look at the evaluators, and invite questions."],
    )


def build_demo_runbook(doc):
    add_heading(doc, "4. Live-demo runbook", 1)
    add_heading(doc, "Before entering the room", 2)
    checks = [
        "Open the final PPTX and confirm speaker notes are visible on the presenter display.",
        "Open Career GPS AI in a second window and set browser zoom to a readable level.",
        "Select a configured hosted provider. Confirm the offline/fake provider is available as fallback.",
        "Clear old results and scroll to the Background section.",
        "Copy the synthetic demo background below to the clipboard.",
        "Close notifications, chat apps, unrelated tabs, and anything containing private information.",
        "Keep the laptop plugged in and disable sleep for the presentation window.",
    ]
    for item in checks:
        add_bullet(doc, f"[ ] {item}")

    add_heading(doc, "Synthetic demo background", 2)
    add_callout(doc, "Paste this", "High school senior. Built a Python budgeting app and a robotics team website. Enjoys data, design, and helping classmates. Wants a remote-friendly technology career.", LIGHT_BLUE, BLUE)

    add_heading(doc, "Exact click path", 2)
    steps = [
        "Paste the synthetic background into Background.",
        "Click Extract Profile; point out that the JSON/profile is reviewable and editable.",
        "Choose Technology, then Data Analyst or another currently configured role.",
        "Select a specialization and realistic time horizon.",
        "Click Run Agent.",
        "Show one recommended path, the top-ranked gap, one project recommendation, and Trace or Warnings.",
        "Return to the deck immediately; do not keep scrolling through every result.",
    ]
    for step in steps:
        add_number(doc, step)

    add_heading(doc, "Fallback ladder", 2)
    add_bullet(doc, "Level 1 - Hosted provider is slow: switch to the offline/fake provider and rerun the same input.", "Level 1")
    add_bullet(doc, "Level 2 - App cannot rerun: use a pre-generated result already loaded in the browser and say it is the deterministic demo path.", "Level 2")
    add_bullet(doc, "Level 3 - Browser fails: stay on slide 3 and verbally walk through the three steps in 35 seconds, then continue to architecture.", "Level 3")
    add_callout(doc, "Never apologize at length", "State the fallback once, continue confidently, and preserve the five-minute pacing.", LIGHT_TEAL, TEAL)


def build_qa(doc):
    add_heading(doc, "5. Likely evaluator questions", 1)
    add_heading(doc, "Concise answer bank", 2)
    questions = [
        ("What makes this different from asking ChatGPT for career advice?", "The user can inspect and edit the extracted profile, see role evidence and ranked gaps, and review warnings and trace metadata. The architecture also separates deterministic checks from LLM synthesis."),
        ("Where is the direct LLM API integration?", "The BackgroundExtractor and CareerReasoner provider implementations call Gemini/OpenAI-compatible or OpenAI APIs and return schema-bound JSON. Qwen and a local HTTP contract are supported behind the same interfaces."),
        ("How did you use two AI agents?", "Claude Code supported architecture and review; OpenAI Codex supported implementation, debugging, tests, and documentation. Human review controlled product decisions and acceptance."),
        ("How do you prevent hallucinated skills?", "The extraction prompt requires facts from the submitted artifact only. Deterministic evidence checks and the verifier surface unsupported claims as warnings or caveats."),
        ("Why separate extraction from reasoning?", "It lets the user review the facts before recommendations are generated and allows each stage to be tested or swapped independently."),
        ("What happens if an API is unavailable?", "Hybrid modes preserve fallback events, and the deterministic fake provider provides a safe offline demo and CI path."),
        ("How did you test it?", "Backend tests cover schemas, tools, providers, fallbacks, verifier checks, and API behavior. The committed evaluation uses five synthetic personas and records evidence coverage and verifier outcomes."),
        ("Is this production-ready?", "It is a strong MVP with provider abstraction, schemas, tests, traces, and a deployment path. Remaining work includes stronger document/privacy controls, production market data, and user studies."),
        ("Why support K-12 users?", "Guided questions let students create evidence even when they do not have a conventional resume. That expands usefulness without changing the underlying profile and plan contracts."),
        ("What would you build next?", "User accounts with consent controls, saved plan versions, stronger grounded labor-market evidence, and outcome-based evaluation with real users."),
    ]
    for question, answer in questions:
        add_heading(doc, question, 3)
        doc.add_paragraph(answer)


def build_final_checklist(doc):
    add_heading(doc, "6. Final readiness checklist", 1)
    sections = {
        "Content and honesty": [
            "Confirm the project title you will submit: Career GPS AI or PathForge AI; use one name consistently.",
            "Confirm the development-agent roles on slide 5 match what you actually did.",
            "Do not imply that fake-provider evaluation measures real model accuracy.",
            "Use only synthetic or permitted documents in the demo.",
        ],
        "Required deliverables": [
            "GitHub repository is accessible to evaluators.",
            "README.md has setup, architecture, provider modes, tests, evaluation, and known limitations.",
            "AI_PROMPTS.md is committed and contains no secrets or private data.",
            "Working application or executable build is available.",
            "Final PPTX opens correctly and includes speaker notes.",
        ],
        "Rehearsal": [
            "Run the entire talk twice with a timer.",
            "Run the demo once on the exact network and machine you will use.",
            "Practice the offline fallback once so it feels normal.",
            "Record one rehearsal and remove filler words or repeated explanations.",
            "Finish between 4:45 and 5:00 without rushing the close.",
        ],
        "Technical preflight": [
            "Run `python -m pytest backend/tests -q`.",
            "Run the deterministic evaluation if results changed.",
            "Verify the provider health endpoint and configured key without exposing the key.",
            "Check that the synthetic demo input produces a clear path, gap, project, and trace.",
            "Keep a local copy of the deck and the printable note cards.",
        ],
    }
    for title, items in sections.items():
        add_heading(doc, title, 2)
        for item in items:
            add_bullet(doc, f"[ ] {item}")

    add_heading(doc, "24-hour rehearsal plan", 2)
    schedule = [
        ("Day before", "Content pass: verify claims, names, demo input, and required files."),
        ("Evening", "Two timed rehearsals; make only small wording changes afterward."),
        ("Morning", "Run tests, open the app, verify hosted and offline provider paths."),
        ("30 minutes before", "Load deck and app, paste demo text to clipboard, silence notifications."),
        ("5 minutes before", "Breathe, stand still, and repeat the opening and closing thesis once."),
    ]
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "When"
    table.cell(0, 1).text = "Action"
    for when, action in schedule:
        cells = table.add_row().cells
        cells[0].text = when
        cells[1].text = action
    set_table_geometry(table, [1800, 7560])
    format_table(table, LIGHT_BLUE, 9.5)

    add_callout(doc, "Final mindset", "The demo is not a tour of every feature. It is proof that one user can move from messy evidence to a transparent, actionable career plan.", LIGHT_TEAL, TEAL)


def main():
    doc = Document()
    configure_document(doc)
    build_cover(doc)
    build_strategy(doc)
    build_run_of_show(doc)
    build_script(doc)
    build_demo_runbook(doc)
    build_qa(doc)
    build_final_checklist(doc)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
