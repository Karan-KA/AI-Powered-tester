import { bg, C, footer, node, title } from "./common.mjs";

export async function slide10(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  title(slide, ctx, "Viva Demo", "A short demo can prove generation, execution, evidence, and analytics end to end.");
  const steps = [
    ["1", "Open /app", "Show the dashboard and analytics cards."],
    ["2", "Generate test", "Use Flipkart or example.com with a natural prompt."],
    ["3", "Inspect steps", "Explain intent summary, source label, and expected result."],
    ["4", "Run test", "Show logs, status, duration, and screenshots."],
    ["5", "Explain design", "Map the run back to FastAPI, Qwen, Playwright, SQLite."]
  ];
  steps.forEach((s, i) => {
    const y = 170 + i * 94;
    ctx.addShape(slide, { x: 92, y: y + 8, w: 44, h: 44, fill: C.blue, line: ctx.line("#00000000", 0), geometry: "ellipse" });
    ctx.addText(slide, { x: 92, y: y + 18, w: 44, h: 22, text: s[0], fontSize: 18, bold: true, color: "#FFFFFF", align: "center" });
    node(slide, ctx, 160, y, 900, 62, s[1], s[2], "#FFFFFF", [C.blue, C.teal, C.amber, C.blue, C.teal][i]);
  });
  ctx.addText(slide, { x: 112, y: 645, w: 960, h: 30, text: "Closing line: AI reduces script-writing effort, while Playwright and evidence capture keep the tests verifiable.", fontSize: 20, bold: true, color: C.ink, align: "center" });
  footer(slide, ctx, 10);
  return slide;
}
