const pptxgen = require("pptxgenjs");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "AI Web Test Automation Project";
pptx.subject = "Viva presentation";
pptx.title = "AI-Powered Intelligent Web Test Automation and Analytics Platform";
pptx.company = "Academic Project";
pptx.lang = "en-US";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "en-US",
};

const C = {
  ink: "101828",
  muted: "667085",
  line: "D0D5DD",
  paper: "F8FAFC",
  panel: "FFFFFF",
  blue: "2563EB",
  teal: "0F766E",
  amber: "D97706",
  red: "B42318",
  slate: "1F2937",
  softBlue: "DBEAFE",
  softTeal: "CCFBF1",
  softAmber: "FEF3C7",
  softRed: "FEE4E2",
};

function addBg(slide, n) {
  slide.background = { color: C.paper };
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.333, h: 0.08, fill: { color: C.blue }, line: { color: C.blue } });
  slide.addText("AI-Powered Web Test Automation Platform", { x: 0.55, y: 7.05, w: 5.3, h: 0.18, fontSize: 7, color: "98A2B3", margin: 0 });
  slide.addText(String(n).padStart(2, "0"), { x: 12.2, y: 7.05, w: 0.55, h: 0.18, fontSize: 7, color: "98A2B3", align: "right", margin: 0 });
}

function title(slide, kicker, claim) {
  slide.addText(kicker.toUpperCase(), { x: 0.65, y: 0.42, w: 2.4, h: 0.25, fontSize: 9, bold: true, color: C.blue, margin: 0 });
  slide.addText(claim, { x: 0.65, y: 0.74, w: 10.8, h: 0.72, fontSize: 28, bold: true, color: C.ink, breakLine: false, fit: "shrink", margin: 0 });
}

function panel(slide, x, y, w, h, fill = C.panel) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { color: C.line, width: 0.8 } });
}

function pill(slide, x, y, text, fill = C.softBlue, color = C.blue) {
  slide.addShape(pptx.ShapeType.roundRect, { x, y, w: 1.35, h: 0.33, rectRadius: 0.08, fill: { color: fill }, line: { color: fill } });
  slide.addText(text, { x, y: y + 0.08, w: 1.35, h: 0.14, fontSize: 8, bold: true, color, align: "center", margin: 0 });
}

function bulletList(slide, x, y, items, opts = {}) {
  items.forEach((item, i) => {
    const yy = y + i * (opts.gap || 0.52);
    slide.addShape(pptx.ShapeType.ellipse, { x, y: yy + 0.09, w: 0.09, h: 0.09, fill: { color: opts.dot || C.blue }, line: { color: opts.dot || C.blue } });
    slide.addText(item, { x: x + 0.22, y: yy, w: opts.w || 4.3, h: 0.32, fontSize: opts.size || 14, color: opts.color || C.ink, fit: "shrink", margin: 0 });
  });
}

function metric(slide, x, y, value, label, color = C.teal) {
  panel(slide, x, y, 2.15, 1.1);
  slide.addText(value, { x: x + 0.18, y: y + 0.16, w: 1.75, h: 0.38, fontSize: 24, bold: true, color, margin: 0 });
  slide.addText(label, { x: x + 0.18, y: y + 0.64, w: 1.75, h: 0.32, fontSize: 9.5, color: C.muted, fit: "shrink", margin: 0 });
}

function node(slide, x, y, w, h, label, sub, fill = C.panel, accent = C.blue) {
  panel(slide, x, y, w, h, fill);
  slide.addShape(pptx.ShapeType.rect, { x, y, w: 0.06, h, fill: { color: accent }, line: { color: accent } });
  slide.addText(label, { x: x + 0.18, y: y + 0.14, w: w - 0.32, h: 0.24, fontSize: 13, bold: true, color: C.ink, margin: 0 });
  if (sub) slide.addText(sub, { x: x + 0.18, y: y + 0.45, w: w - 0.32, h: h - 0.55, fontSize: 9.5, color: C.muted, breakLine: false, fit: "shrink", margin: 0 });
}

function arrow(slide, x1, y1, x2, y2, color = C.blue) {
  slide.addShape(pptx.ShapeType.line, { x: x1, y: y1, w: x2 - x1, h: y2 - y1, line: { color, width: 2, beginArrowType: "none", endArrowType: "triangle" } });
}

function addNotes(slide, notes) {
  if (typeof slide.addNotes === "function") slide.addNotes(notes);
}

let s = pptx.addSlide(); addBg(s, 1);
s.addText("FINAL YEAR PROJECT", { x: 0.65, y: 0.6, w: 2.5, h: 0.2, fontSize: 9, bold: true, color: C.blue, margin: 0 });
s.addText("AI-Powered Intelligent Web Test Automation and Analytics Platform", { x: 0.65, y: 1.05, w: 8.9, h: 1.55, fontSize: 34, bold: true, color: C.ink, fit: "shrink", margin: 0 });
s.addText("A browser automation platform that converts natural-language requirements into executable Playwright tests, captures evidence, and reports execution analytics.", { x: 0.68, y: 3.02, w: 6.8, h: 0.75, fontSize: 15.5, color: C.muted, fit: "shrink", margin: 0 });
pill(s, 0.68, 4.04, "FastAPI"); pill(s, 2.15, 4.04, "Qwen AI", C.softTeal, C.teal); pill(s, 3.62, 4.04, "Playwright", C.softAmber, C.amber); pill(s, 5.09, 4.04, "SQLite");
metric(s, 0.7, 5.15, "25", "automated backend tests passing", C.teal); metric(s, 3.1, 5.15, "3", "result states: pass, fail, warning", C.blue); metric(s, 5.5, 5.15, "Real", "browser execution with screenshots", C.amber);
s.addText("Viva Presentation", { x: 9.9, y: 5.75, w: 1.9, h: 0.3, fontSize: 13, bold: true, color: C.ink, align: "right", margin: 0 });
addNotes(s, "Introduce the project as a complete AI-assisted testing platform: generate, execute, capture, and analyze.");

s = pptx.addSlide(); addBg(s, 2); title(s, "Problem", "Manual web testing is powerful, but hard to scale for changing applications.");
panel(s, 0.7, 1.75, 5.15, 4.2); s.addText("Traditional automation friction", { x: 0.95, y: 2.05, w: 4.3, h: 0.35, fontSize: 18, bold: true, color: C.ink, margin: 0 });
bulletList(s, 1.0, 2.72, ["Testers write scripts manually for every workflow.", "Locators break when websites change UI structure.", "Screenshots, logs, and reports are often separate.", "Non-programmers cannot easily create automation."], { w: 4.1, size: 13, gap: 0.58, dot: C.red });
panel(s, 6.7, 1.75, 4.65, 4.2, "F0F9FF"); s.addText("Project idea", { x: 7.05, y: 2.14, w: 3.8, h: 0.45, fontSize: 20, bold: true, color: C.blue, margin: 0 });
s.addText("Let the user describe a testing requirement in plain English. The system should generate, execute, store, and explain the test run from one dashboard.", { x: 7.05, y: 2.85, w: 3.75, h: 1.8, fontSize: 17, color: C.ink, fit: "shrink", margin: 0 });
s.addShape(pptx.ShapeType.rect, { x: 7.05, y: 5.18, w: 3.45, h: 0.04, fill: { color: C.blue }, line: { color: C.blue } });
addNotes(s, "Explain why this matters: it reduces script-writing burden and centralizes test evidence.");

s = pptx.addSlide(); addBg(s, 3); title(s, "Objectives", "The project combines generation, execution, evidence, and analytics in one workflow.");
[["Generate", "Convert URL + natural language into structured steps."], ["Execute", "Run steps in Chromium with Playwright automation."], ["Capture", "Save screenshots, console logs, status, and duration."], ["Analyze", "Store history in SQLite and show pass-rate analytics."]].forEach((c, i) => {
  const x = 0.72 + i * 2.9; panel(s, x, 1.92, 2.48, 1.9);
  s.addText(c[0], { x: x + 0.2, y: 2.2, w: 2.0, h: 0.32, fontSize: 19, bold: true, color: [C.blue, C.teal, C.amber, C.slate][i], margin: 0 });
  s.addText(c[1], { x: x + 0.2, y: 2.76, w: 1.95, h: 0.75, fontSize: 12.5, color: C.muted, fit: "shrink", margin: 0 });
});
panel(s, 1.3, 4.55, 9.4, 1.05, "ECFDF3"); s.addText("Academic target: simple enough to demo, complete enough to show real automation behavior.", { x: 1.7, y: 4.84, w: 8.6, h: 0.45, fontSize: 18, bold: true, color: C.teal, align: "center", margin: 0 });
addNotes(s, "Use this slide to state the measurable objectives of the implementation.");

s = pptx.addSlide(); addBg(s, 4); title(s, "Architecture", "A modular backend keeps AI generation separate from browser execution and storage.");
node(s, 0.7, 2.2, 1.95, 1.1, "Dashboard", "HTML, CSS, JavaScript\nGenerate and run tests", C.panel, C.blue);
node(s, 3.35, 2.2, 1.95, 1.1, "FastAPI", "REST endpoints\nSwagger docs", C.panel, C.teal);
node(s, 6.0, 1.6, 2.25, 1.1, "AI Service", "Qwen via Ollama\nFallback + grounding", C.panel, C.amber);
node(s, 6.0, 3.5, 2.25, 1.1, "Executor", "Playwright + Chromium\nScreenshots and logs", C.panel, C.blue);
node(s, 9.15, 2.2, 2.15, 1.1, "SQLite", "Test cases\nRun history and analytics", C.panel, C.teal);
arrow(s, 2.68, 2.75, 3.25, 2.75); arrow(s, 5.35, 2.55, 5.9, 2.15); arrow(s, 5.35, 2.95, 5.9, 4.02); arrow(s, 8.28, 2.15, 9.05, 2.55); arrow(s, 8.28, 4.05, 9.05, 3.05);
s.addText("Service modules make AI behavior, execution behavior, database models, and API routes independently testable.", { x: 1.25, y: 5.25, w: 9.2, h: 0.6, fontSize: 16.5, color: C.ink, align: "center", fit: "shrink", margin: 0 });
addNotes(s, "Walk through data flow: dashboard to API, AI generation, execution, storage, analytics.");

s = pptx.addSlide(); addBg(s, 5); title(s, "AI Pipeline", "The generator interprets intent first, then creates executable steps with repair rules.");
[["1. Inspect page", "Collect visible inputs, buttons, links, headings, media."], ["2. Interpret prompt", "Separate test data from expected behavior."], ["3. Plan workflow", "Use Qwen AI for steps, assertions, screenshots."], ["4. Ground selectors", "Repair invented or broad selectors using real controls."], ["5. Save test", "Persist source, intent summary, expected result, and steps."]].forEach((st, i) => node(s, 0.7 + i * 2.35, 2.35, 1.95, 1.9, st[0], st[1], i % 2 ? "F0FDF4" : "EFF6FF", [C.blue, C.teal, C.amber, C.blue, C.teal][i]));
s.addText("If Ollama/Qwen is unavailable or invalid, deterministic fallback still creates useful tests. This avoids a blank or broken demo.", { x: 1.15, y: 5.12, w: 10, h: 0.65, fontSize: 16.5, color: C.ink, align: "center", fit: "shrink", margin: 0 });
addNotes(s, "Emphasize that the project is AI-first but not AI-fragile.");

s = pptx.addSlide(); addBg(s, 6); title(s, "Execution", "Playwright turns generated steps into browser evidence, not just text output.");
node(s, 0.8, 1.9, 3.0, 1.18, "Actions", "goto, click, fill, press, wait", C.panel, C.blue);
node(s, 0.8, 3.52, 3.0, 1.18, "Assertions", "title, text, URL, visible element, value, count", C.panel, C.teal);
node(s, 4.45, 1.9, 3.0, 1.18, "Evidence", "screenshots, console logs, duration", C.panel, C.amber);
node(s, 4.45, 3.52, 3.0, 1.18, "Resilience", "popup dismissal, selector recovery, warning state", C.panel, C.blue);
metric(s, 8.35, 2.0, "Pass", "workflow completed", C.teal); metric(s, 8.35, 3.35, "Fail", "required step failed", C.red); metric(s, 8.35, 4.7, "Warning", "main flow completed with skipped optional step", C.amber);
addNotes(s, "Explain why warning exists: it distinguishes real failure from optional/not-applicable steps.");

s = pptx.addSlide(); addBg(s, 7); title(s, "Dashboard", "The user experience is intentionally simple: generate, inspect, run, and review.");
panel(s, 0.75, 1.82, 4.75, 4.3); s.addText("Main controls", { x: 1.05, y: 2.15, w: 3.6, h: 0.34, fontSize: 18, bold: true, color: C.ink, margin: 0 });
bulletList(s, 1.12, 2.78, ["Website URL input", "Natural language requirement", "Inspect & Generate Test", "Run Latest and Run Generated Suite", "Optional visible browser mode"], { w: 3.8, size: 13.2, gap: 0.5 });
panel(s, 6.5, 1.82, 4.75, 4.3, "F8FAFC"); s.addText("Review panels", { x: 6.8, y: 2.15, w: 3.6, h: 0.34, fontSize: 18, bold: true, color: C.ink, margin: 0 });
bulletList(s, 6.88, 2.78, ["Saved tests with step list", "AI/fallback source label", "Execution status and duration", "Logs and screenshots", "Analytics counts and pass rate"], { w: 3.8, size: 13.2, gap: 0.5, dot: C.teal });
addNotes(s, "Mention that the UI is deliberately simple for academic demonstration.");

s = pptx.addSlide(); addBg(s, 8); title(s, "Validation", "The system is covered by automated backend tests and live browser verification.");
metric(s, 0.9, 1.95, "25", "pytest tests passing", C.teal); metric(s, 3.4, 1.95, "Qwen", "AI intent + plan generation tested", C.blue); metric(s, 5.9, 1.95, "Suite", "multi-case generation tested", C.amber); metric(s, 8.4, 1.95, "Live", "Flipkart flows verified", C.teal);
panel(s, 1.2, 3.9, 9.4, 1.55); s.addText("Recent robustness fixes", { x: 1.55, y: 4.2, w: 8.5, h: 0.34, fontSize: 18, bold: true, color: C.ink, margin: 0 });
s.addText("Popup dismissal, generic link repair, Flipkart OTP login handling, screenshot fallback, noisy console filtering, and URL checks that do not wait for slow external assets.", { x: 1.55, y: 4.72, w: 8.55, h: 0.55, fontSize: 14.2, color: C.muted, fit: "shrink", margin: 0 });
addNotes(s, "Use this slide for credibility: the project was iterated against real failure cases.");

s = pptx.addSlide(); addBg(s, 9); title(s, "Limits & Future", "The platform is complete for demonstration, with clear paths to production hardening.");
panel(s, 0.8, 1.85, 4.9, 4.1, "FFF7ED"); s.addText("Current limitations", { x: 1.1, y: 2.18, w: 3.6, h: 0.32, fontSize: 18, bold: true, color: C.amber, margin: 0 });
bulletList(s, 1.18, 2.88, ["Local AI quality depends on Ollama/Qwen availability.", "Public sites can change selectors and anti-bot behavior.", "SQLite is best for academic/demo scope.", "Advanced report export is future work."], { w: 3.9, size: 13, gap: 0.58, dot: C.amber });
panel(s, 6.45, 1.85, 4.9, 4.1, "ECFDF3"); s.addText("Future scope", { x: 6.75, y: 2.18, w: 3.6, h: 0.32, fontSize: 18, bold: true, color: C.teal, margin: 0 });
bulletList(s, 6.83, 2.88, ["PostgreSQL and multi-user accounts.", "CI/CD integration for scheduled test runs.", "PDF/HTML execution reports.", "Parallel browser execution and visual regression."], { w: 3.9, size: 13, gap: 0.58, dot: C.teal });
addNotes(s, "Be honest about limitations but show strong future expansion.");

s = pptx.addSlide(); addBg(s, 10); title(s, "Viva Demo", "A short demo can prove generation, execution, evidence, and analytics end to end.");
[["1", "Open /app", "Show the dashboard and analytics cards."], ["2", "Generate test", "Use Flipkart or example.com with a natural prompt."], ["3", "Inspect steps", "Explain intent summary, source label, and expected result."], ["4", "Run test", "Show logs, status, duration, and screenshots."], ["5", "Explain design", "Map the run back to FastAPI, Qwen, Playwright, SQLite."]].forEach((st, i) => {
  const y = 1.7 + i * 0.92;
  s.addShape(pptx.ShapeType.ellipse, { x: 0.92, y: y + 0.08, w: 0.44, h: 0.44, fill: { color: C.blue }, line: { color: C.blue } });
  s.addText(st[0], { x: 0.92, y: y + 0.19, w: 0.44, h: 0.16, fontSize: 12, bold: true, color: "FFFFFF", align: "center", margin: 0 });
  node(s, 1.6, y, 9.1, 0.62, st[1], st[2], C.panel, [C.blue, C.teal, C.amber, C.blue, C.teal][i]);
});
s.addText("Closing line: AI reduces script-writing effort, while Playwright and evidence capture keep the tests verifiable.", { x: 1.1, y: 6.42, w: 9.7, h: 0.3, fontSize: 14.5, bold: true, color: C.ink, align: "center", fit: "shrink", margin: 0 });
addNotes(s, "Use this as your live viva running order.");

pptx.writeFile({ fileName: "docs/AI-Web-Test-Automation-Viva.pptx" });
