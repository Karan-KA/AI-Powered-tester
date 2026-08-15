import { arrow, bg, C, footer, node, title } from "./common.mjs";

export async function slide04(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  title(slide, ctx, "Architecture", "A modular backend keeps AI generation separate from browser execution and storage.");
  node(slide, ctx, 70, 220, 190, 110, "Dashboard", "HTML, CSS, JavaScript\\nGenerate and run tests", "#FFFFFF", C.blue);
  node(slide, ctx, 330, 220, 190, 110, "FastAPI", "REST endpoints\\nSwagger documentation", "#FFFFFF", C.teal);
  node(slide, ctx, 590, 160, 220, 110, "AI Service", "Qwen via Ollama\\nRule fallback + grounding", "#FFFFFF", C.amber);
  node(slide, ctx, 590, 350, 220, 110, "Executor", "Playwright + Chromium\\nScreenshots and logs", "#FFFFFF", C.blue);
  node(slide, ctx, 900, 220, 210, 110, "SQLite", "Test cases\\nRun history and analytics", "#FFFFFF", C.teal);
  arrow(slide, ctx, 265, 274, 325, 274);
  arrow(slide, ctx, 525, 255, 585, 210);
  arrow(slide, ctx, 525, 292, 585, 405);
  arrow(slide, ctx, 815, 210, 895, 255);
  arrow(slide, ctx, 815, 405, 895, 305);
  ctx.addText(slide, { x: 132, y: 520, w: 910, h: 58, text: "The design uses service modules, so AI behavior, execution behavior, database models, and API routes can be tested independently.", fontSize: 24, color: C.ink, align: "center" });
  footer(slide, ctx, 4);
  return slide;
}
