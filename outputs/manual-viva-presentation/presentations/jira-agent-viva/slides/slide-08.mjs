import { bg, C, footer, metric, panel, title } from "./common.mjs";

export async function slide08(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  title(slide, ctx, "Validation", "The system is covered by automated backend tests and live browser verification.");
  metric(slide, ctx, 90, 195, "25", "pytest tests passing", C.teal);
  metric(slide, ctx, 340, 195, "Qwen", "AI intent + plan generation tested", C.blue);
  metric(slide, ctx, 590, 195, "Suite", "multi-case generation tested", C.amber);
  metric(slide, ctx, 840, 195, "Live", "Flipkart flows verified", C.teal);
  panel(slide, ctx, 120, 390, 930, 150, "#FFFFFF");
  ctx.addText(slide, { x: 155, y: 420, w: 850, h: 34, text: "Recent robustness fixes", fontSize: 24, bold: true, color: C.ink });
  ctx.addText(slide, { x: 155, y: 468, w: 850, h: 58, text: "Popup dismissal, generic link repair, Flipkart OTP login handling, screenshot fallback, noisy console filtering, and URL checks that do not wait for slow external assets.", fontSize: 21, color: C.muted });
  footer(slide, ctx, 8);
  return slide;
}
