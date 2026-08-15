import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("REPORT_OUT", ROOT / "generated_reports" / "intelligent-automation-report"))
OUT.mkdir(parents=True, exist_ok=True)

TITLE = "AI-Powered Intelligent Web Test Automation and Analytics Platform"
STUDENT_NAME = "Karan K A"
STUDENT_ID = "202217b2235"
PROGRAMME = "M.Tech. Software Engineering"
ORGANIZATION = "Birla Institute of Technology & Science, Pilani"
SUPERVISOR_NAME = "Gowdeswaran P C"
EXAMINER_NAME = "Aakash R"
ASSET_DIR = Path(os.environ.get("REPORT_ASSET_DIR", r"C:\Users\Acer\AppData\Local\Temp\codex-karan-report-assets"))
BITS_LOGO = ASSET_DIR / "image1.png"
STUDENT_SIGN = ASSET_DIR / "image3.jpg"
SUPERVISOR_SIGN = ASSET_DIR / "image4.jpg"
EXAMINER_SIGN = ASSET_DIR / "image5.jpg"


def styles():
    base = getSampleStyleSheet()
    base["Normal"].fontName = "Helvetica"
    base["Normal"].fontSize = 10.5
    base["Normal"].leading = 14
    base["Normal"].spaceAfter = 7
    base["Title"].fontName = "Helvetica-Bold"
    base["Title"].fontSize = 18
    base["Title"].leading = 23
    base["Title"].alignment = TA_CENTER
    base["Heading1"].fontName = "Helvetica-Bold"
    base["Heading1"].fontSize = 15
    base["Heading1"].textColor = colors.HexColor("#1F4D78")
    base["Heading1"].spaceBefore = 12
    base["Heading1"].spaceAfter = 8
    base["Heading2"].fontName = "Helvetica-Bold"
    base["Heading2"].fontSize = 12.5
    base["Heading2"].textColor = colors.HexColor("#1F4D78")
    base["Heading2"].spaceBefore = 8
    base["Heading2"].spaceAfter = 5
    base.add(ParagraphStyle("Center", parent=base["Normal"], alignment=TA_CENTER))
    base.add(ParagraphStyle("SmallCenter", parent=base["Normal"], fontSize=9.5, alignment=TA_CENTER))
    return base


def p(text, style):
    return Paragraph(text, style)


def table(data, widths):
    header_style = ParagraphStyle(
        "TableHeader",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=10.5,
        textColor=colors.black,
    )
    cell_style = ParagraphStyle(
        "TableCell",
        fontName="Helvetica",
        fontSize=8.3,
        leading=10.2,
        textColor=colors.black,
    )
    wrapped = []
    for r, row in enumerate(data):
        style = header_style if r == 0 else cell_style
        wrapped.append([value if hasattr(value, "drawOn") else Paragraph(str(value), style) for value in row])
    t = Table(wrapped, colWidths=widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#A6A6A6")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F4F7")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


def bullets(items, style):
    out = []
    for item in items:
        out.append(Paragraph("- " + item, style))
    return out


def page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawRightString(7.5 * inch, 0.5 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build():
    s = styles()
    story = []
    if BITS_LOGO.exists():
        story.append(Image(str(BITS_LOGO), width=0.82 * inch, height=0.78 * inch))
    story += [
        Spacer(1, 0.18 * inch),
        p(TITLE.upper(), s["Title"]),
        Spacer(1, 0.12 * inch),
        p("BITS ZG628T: Dissertation", s["Center"]),
        Spacer(1, 0.18 * inch),
        p("by", s["Center"]),
        p(STUDENT_NAME, s["Center"]),
        p(STUDENT_ID, s["Center"]),
        Spacer(1, 0.2 * inch),
        p("Dissertation work carried out at", s["Center"]),
        p(ORGANIZATION, s["Center"]),
        Spacer(1, 0.18 * inch),
        p(f"Submitted in partial fulfilment of {PROGRAMME} degree programme", s["Center"]),
        Spacer(1, 0.18 * inch),
        p("Under the Supervision of", s["Center"]),
        p(SUPERVISOR_NAME, s["Center"]),
        Spacer(1, 0.35 * inch),
        p("BIRLA INSTITUTE OF TECHNOLOGY & SCIENCE", s["Center"]),
        p("PILANI (RAJASTHAN)", s["Center"]),
        p("June 2026", s["Center"]),
        PageBreak(),
    ]

    story += [
        p("ABSTRACT", s["Heading1"]),
        p("Frequent releases in web applications make manual regression testing slow, repetitive, and difficult to maintain. This project presents an intelligent automation platform that transforms a user's natural-language testing requirement into executable browser steps. The system combines a FastAPI backend, a responsive dashboard, optional Qwen-based test planning through Ollama, deterministic fallback generation, Playwright browser execution, SQLite persistence, and analytics for reviewing test history.", s["Normal"]),
        p("The platform allows the user to create a saved workspace for a website URL, generate one or more test cases for that workspace, run selected cases in Chromium, and preserve screenshots, logs, status, duration, and error summaries. The completed implementation demonstrates how intelligent automation can support software quality assurance by reducing script-writing effort while keeping evidence, repeatability, and result visibility.", s["Normal"]),
        p("Keywords: intelligent automation, web testing, Playwright, FastAPI, natural-language test generation, SQLite, quality assurance.", s["Normal"]),
        Spacer(1, 0.35 * inch),
        table(
            [
                ["Signature of the Student", "Signature of the Supervisor", "Signature of the Additional Examiner"],
                [
                    Image(str(STUDENT_SIGN), width=1.2 * inch, height=0.52 * inch) if STUDENT_SIGN.exists() else "",
                    Image(str(SUPERVISOR_SIGN), width=1.2 * inch, height=0.52 * inch) if SUPERVISOR_SIGN.exists() else "",
                    Image(str(EXAMINER_SIGN), width=1.2 * inch, height=0.52 * inch) if EXAMINER_SIGN.exists() else "",
                ],
                [
                    f"Name: {STUDENT_NAME}<br/>ID: {STUDENT_ID}<br/>Date:<br/>Place:",
                    f"Name: {SUPERVISOR_NAME}<br/>Date:<br/>Place:",
                    f"Name: {EXAMINER_NAME}<br/>Date:<br/>Place:",
                ],
            ],
            [2.0 * inch, 2.0 * inch, 2.0 * inch],
        ),
        PageBreak(),
    ]

    story += [
        p("Contents", s["Heading1"]),
        p("1. Modules in the Intelligent Automation Platform ................................ 4", s["Normal"]),
        p("2. Functional Block Diagram and System Description ............................. 6", s["Normal"]),
        p("3. Major Technical Specifications .............................................. 8", s["Normal"]),
        p("4. Design Considerations ....................................................... 9", s["Normal"]),
        p("5. Testing, Results, and Validation ........................................... 10", s["Normal"]),
        p("6. Future Plan ................................................................ 11", s["Normal"]),
        p("7. References ................................................................ 11", s["Normal"]),
        Spacer(1, 0.15 * inch),
        p("List of Figures", s["Heading2"]),
        p("Figure 1: Logical architecture of the intelligent automation platform", s["Normal"]),
        p("Figure 2: End-to-end generation and execution workflow", s["Normal"]),
        p("List of Tables", s["Heading2"]),
        p("Table 1: Major software modules", s["Normal"]),
        p("Table 2: Major technical specifications", s["Normal"]),
        p("Table 3: Validation summary", s["Normal"]),
        PageBreak(),
    ]

    story += [
        p("1. MODULES IN THE INTELLIGENT AUTOMATION PLATFORM", s["Heading1"]),
        p("The project is organized as cooperating modules with clear responsibilities, which keeps the system suitable for academic demonstration while representing a practical automation workflow.", s["Normal"]),
        table(
            [
                ["Module", "Implementation", "Responsibility"],
                ["Dashboard", "HTML, CSS, JavaScript", "Creates URL workspaces, generates tests, runs cases, and reviews evidence."],
                ["API Layer", "FastAPI routes", "Handles sessions, test cases, runs, health status, and analytics."],
                ["AI Test Generator", "ai_service.py and llm_service.py", "Creates structured test steps using Qwen or deterministic fallback rules."],
                ["Execution Engine", "executor_service.py", "Runs steps through Playwright and classifies outcomes."],
                ["Persistence Layer", "SQLAlchemy and SQLite", "Stores workspaces, cases, runs, logs, screenshots, and analytics data."],
                ["Validation Suite", "pytest tests", "Verifies API behavior, planning rules, execution fallbacks, and analytics."],
            ],
            [1.4 * inch, 1.6 * inch, 3.2 * inch],
        ),
        p("Table 1: Major software modules", s["SmallCenter"]),
        p("The dashboard is the user's main workspace. The backend coordinates requests, validates schemas, stores records, and routes work to the generator and executor. The generator inspects visible controls and prepares executable steps. The executor opens Chromium, performs browser actions, captures screenshots, and stores evidence.", s["Normal"]),
        PageBreak(),
    ]

    arch = OUT / "figure-architecture.png"
    workflow = OUT / "figure-workflow.png"
    story += [
        p("2. FUNCTIONAL BLOCK DIAGRAM AND SYSTEM DESCRIPTION", s["Heading1"]),
        p("The platform follows a request-to-evidence workflow. A user begins from the dashboard, the backend prepares a structured plan, Playwright executes it in a browser, and the result is saved for review.", s["Normal"]),
        Image(str(arch), width=6.2 * inch, height=3.35 * inch),
        p("Figure 1: Logical architecture of the intelligent automation platform", s["SmallCenter"]),
        Image(str(workflow), width=6.2 * inch, height=2.3 * inch),
        p("Figure 2: End-to-end generation and execution workflow", s["SmallCenter"]),
        p("The flow starts with a URL workspace and requirement. The backend inspects page controls, generates validated steps, executes them in Chromium, and stores logs, screenshots, status, duration, and error details.", s["Normal"]),
        PageBreak(),
    ]

    story += [
        p("3. MAJOR TECHNICAL SPECIFICATIONS", s["Heading1"]),
        table(
            [
                ["Category", "Specification"],
                ["Project type", "AI-assisted intelligent web test automation and analytics platform"],
                ["Frontend", "Responsive HTML, CSS, and JavaScript dashboard"],
                ["Backend framework", "FastAPI with Pydantic validation"],
                ["Automation runtime", "Playwright with Chromium browser execution"],
                ["AI component", "Ollama with Qwen, plus deterministic fallback generation"],
                ["Database", "SQLite through SQLAlchemy ORM"],
                ["Supported actions", "goto, click, fill, press, wait, screenshot, and assertions"],
                ["Verification", "34 automated backend tests passing through pytest"],
            ],
            [2.0 * inch, 4.2 * inch],
        ),
        p("Table 2: Major technical specifications", s["SmallCenter"]),
        PageBreak(),
    ]

    story += [
        p("4. DESIGN CONSIDERATIONS", s["Heading1"]),
        p("The design emphasizes reliability, explainability, and local usability. AI-generated automation is constrained through schemas, supported action lists, validation, selector grounding, fallback planning, and runtime recovery.", s["Normal"]),
        p("Reliability and fallback behavior", s["Heading2"]),
        p("The system does not depend entirely on the language model. If Qwen is unavailable or returns an invalid plan, deterministic rules still create a useful test case.", s["Normal"]),
        p("Evidence preservation", s["Heading2"]),
        p("Each run stores logs, screenshots, status, duration, and error summaries so results can be audited later.", s["Normal"]),
        p("Safety of automated actions", s["Heading2"]),
        p("The project avoids destructive actions such as deleting data, placing orders, or using real credentials. Authentication checks use deliberately invalid accounts and verify rejection.", s["Normal"]),
        PageBreak(),
    ]

    story += [
        p("5. TESTING, RESULTS, AND VALIDATION", s["Heading1"]),
        table(
            [
                ["Validation Area", "Coverage", "Observed Result"],
                ["API health and schemas", "Health endpoint and request-response models", "Responses are shaped correctly."],
                ["Test generation", "Focused prompts, blank prompts, saved cases, and suites", "Generated tests are stored and returned."],
                ["Session behavior", "Workspace creation, update, deletion, and histories", "URL workspaces preserve related records."],
                ["AI planning rules", "Intent extraction, validation, grounding, fallback use", "Invalid AI output is handled safely."],
                ["Execution service", "Selector recovery, screenshots, logs, warnings, failures", "Runs classify outcomes and preserve evidence."],
                ["Analytics", "Counts, pass rate, average duration, recent runs", "Dashboard-ready analytics are returned."],
            ],
            [1.55 * inch, 2.35 * inch, 2.3 * inch],
        ),
        p("Table 3: Validation summary", s["SmallCenter"]),
        p("The current backend verification result is 34 passed tests. The implemented system can create a URL workspace, generate test cases, execute selected cases in a browser, store evidence, and display analytics.", s["Normal"]),
        p("6. FUTURE PLAN", s["Heading1"]),
        *bullets(
            [
                "Add authentication and role-based access.",
                "Move from SQLite to PostgreSQL for deployed environments.",
                "Introduce stronger locator healing using historical run evidence.",
                "Support CI/CD execution and downloadable execution reports.",
                "Add parallel browser execution and visual regression checks.",
            ],
            s["Normal"],
        ),
        p("7. REFERENCES", s["Heading1"]),
        *bullets(
            [
                "FastAPI documentation, https://fastapi.tiangolo.com/",
                "Playwright documentation, https://playwright.dev/python/",
                "SQLAlchemy documentation, https://www.sqlalchemy.org/",
                "SQLite documentation, https://www.sqlite.org/docs.html",
                "Ollama documentation, https://ollama.com/",
                "Project repository documentation: README.md, ARCHITECTURE.md, API_REFERENCE.md, TESTING.md, and USER_MANUAL.md.",
            ],
            s["Normal"],
        ),
    ]

    path = OUT / "Intelligent_Automation_Mid_Sem_Report.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=letter, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    doc.build(story, onFirstPage=page_number, onLaterPages=page_number)
    print(path)


if __name__ == "__main__":
    build()
