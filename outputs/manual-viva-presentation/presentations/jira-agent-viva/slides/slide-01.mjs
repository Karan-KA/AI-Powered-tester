import { bg, C, footer, metric, pill } from "./common.mjs";

export async function slide01(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  ctx.addText(slide, { x: 62, y: 62, w: 260, h: 28, text: "FINAL YEAR PROJECT", fontSize: 13, bold: true, color: C.blue });
  ctx.addText(slide, {
    x: 62, y: 112, w: 860, h: 160,
    text: "AI-Powered Intelligent Web Test Automation and Analytics Platform",
    fontSize: 48, bold: true, color: C.ink, typeface: ctx.fonts.title,
  });
  ctx.addText(slide, {
    x: 64, y: 300, w: 650, h: 70,
    text: "A browser automation platform that converts natural-language requirements into executable Playwright tests, captures evidence, and reports execution analytics.",
    fontSize: 22, color: C.muted,
  });
  pill(slide, ctx, 64, 400, "FastAPI");
  pill(slide, ctx, 214, 400, "Qwen AI", C.softTeal, C.teal);
  pill(slide, ctx, 364, 400, "Playwright", C.softAmber, C.amber);
  pill(slide, ctx, 514, 400, "SQLite");
  metric(slide, ctx, 64, 510, "25", "automated backend tests passing", C.teal);
  metric(slide, ctx, 304, 510, "3", "result states: pass, fail, warning", C.blue);
  metric(slide, ctx, 544, 510, "Real", "browser execution with screenshots", C.amber);
  ctx.addText(slide, { x: 970, y: 560, w: 180, h: 34, text: "Viva Presentation", fontSize: 18, bold: true, color: C.ink, align: "right" });
  footer(slide, ctx, 1);
  return slide;
}
