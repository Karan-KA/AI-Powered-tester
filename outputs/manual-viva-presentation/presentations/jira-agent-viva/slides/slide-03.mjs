import { bg, bulletList, C, footer, panel, title } from "./common.mjs";

export async function slide03(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  title(slide, ctx, "Objectives", "The project combines generation, execution, evidence, and analytics in one workflow.");
  const cols = [
    ["Generate", "Convert URL + natural language into structured steps."],
    ["Execute", "Run steps in Chromium with Playwright automation."],
    ["Capture", "Save screenshots, console logs, status, and duration."],
    ["Analyze", "Store history in SQLite and show pass-rate analytics."]
  ];
  cols.forEach((c, i) => {
    const x = 70 + i * 290;
    panel(slide, ctx, x, 190, 245, 190);
    ctx.addText(slide, { x: x + 20, y: 220, w: 200, h: 34, text: c[0], fontSize: 26, bold: true, color: [C.blue, C.teal, C.amber, C.slate][i] });
    ctx.addText(slide, { x: x + 20, y: 275, w: 195, h: 78, text: c[1], fontSize: 18, color: C.muted });
  });
  panel(slide, ctx, 130, 455, 940, 105, "#ECFDF3");
  ctx.addText(slide, { x: 170, y: 484, w: 860, h: 44, text: "Academic target: simple enough to demo, complete enough to show real automation behavior.", fontSize: 26, bold: true, color: C.teal, align: "center" });
  footer(slide, ctx, 3);
  return slide;
}
