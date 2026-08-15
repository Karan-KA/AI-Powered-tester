import { bg, C, footer, metric, node, title } from "./common.mjs";

export async function slide06(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  title(slide, ctx, "Execution", "Playwright turns generated steps into browser evidence, not just text output.");
  node(slide, ctx, 80, 190, 300, 120, "Actions", "goto, click, fill, press, wait", "#FFFFFF", C.blue);
  node(slide, ctx, 80, 350, 300, 120, "Assertions", "title, text, URL, visible element, value, count", "#FFFFFF", C.teal);
  node(slide, ctx, 450, 190, 300, 120, "Evidence", "screenshots, console logs, duration", "#FFFFFF", C.amber);
  node(slide, ctx, 450, 350, 300, 120, "Resilience", "popup dismissal, selector recovery, warning state", "#FFFFFF", C.blue);
  metric(slide, ctx, 835, 200, "Pass", "workflow completed", C.teal);
  metric(slide, ctx, 835, 335, "Fail", "required step failed", C.red);
  metric(slide, ctx, 835, 470, "Warning", "main flow completed with skipped optional step", C.amber);
  footer(slide, ctx, 6);
  return slide;
}
