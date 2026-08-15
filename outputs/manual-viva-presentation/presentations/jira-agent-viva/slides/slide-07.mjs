import { bg, bulletList, C, footer, panel, title } from "./common.mjs";

export async function slide07(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  title(slide, ctx, "Dashboard", "The user experience is intentionally simple: generate, inspect, run, and review.");
  panel(slide, ctx, 74, 180, 470, 430);
  ctx.addText(slide, { x: 104, y: 214, w: 360, h: 34, text: "Main controls", fontSize: 25, bold: true, color: C.ink });
  bulletList(slide, ctx, 112, 280, [
    "Website URL input",
    "Natural language requirement",
    "Inspect & Generate Test",
    "Run Latest and Run Generated Suite",
    "Optional visible browser mode"
  ], { w: 360, size: 19, gap: 50 });
  panel(slide, ctx, 642, 180, 470, 430, "#F8FAFC");
  ctx.addText(slide, { x: 672, y: 214, w: 360, h: 34, text: "Review panels", fontSize: 25, bold: true, color: C.ink });
  bulletList(slide, ctx, 680, 280, [
    "Saved tests with step list",
    "AI/fallback source label",
    "Execution status and duration",
    "Logs and screenshots",
    "Analytics counts and pass rate"
  ], { w: 360, size: 19, gap: 50, dot: C.teal });
  footer(slide, ctx, 7);
  return slide;
}
