import { bg, bulletList, C, footer, panel, title } from "./common.mjs";

export async function slide09(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  title(slide, ctx, "Limits & Future", "The platform is complete for demonstration, with clear paths to production hardening.");
  panel(slide, ctx, 78, 185, 485, 410, "#FFF7ED");
  ctx.addText(slide, { x: 108, y: 220, w: 360, h: 30, text: "Current limitations", fontSize: 24, bold: true, color: C.amber });
  bulletList(slide, ctx, 116, 290, [
    "Local AI quality depends on Ollama/Qwen availability.",
    "Public sites can change selectors and anti-bot behavior.",
    "SQLite is best for academic/demo scope.",
    "Advanced report export is future work."
  ], { w: 390, size: 18, gap: 56, dot: C.amber });
  panel(slide, ctx, 646, 185, 485, 410, "#ECFDF3");
  ctx.addText(slide, { x: 676, y: 220, w: 360, h: 30, text: "Future scope", fontSize: 24, bold: true, color: C.teal });
  bulletList(slide, ctx, 684, 290, [
    "PostgreSQL and multi-user accounts.",
    "CI/CD integration for scheduled test runs.",
    "PDF/HTML execution reports.",
    "Parallel browser execution and visual regression."
  ], { w: 390, size: 18, gap: 56, dot: C.teal });
  footer(slide, ctx, 9);
  return slide;
}
