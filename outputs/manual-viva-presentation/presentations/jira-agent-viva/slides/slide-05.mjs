import { bg, C, footer, node, title } from "./common.mjs";

export async function slide05(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  title(slide, ctx, "AI Pipeline", "The generator interprets intent first, then creates executable steps with repair rules.");
  const stages = [
    ["1. Inspect page", "Collect visible inputs, buttons, links, headings, media."],
    ["2. Interpret prompt", "Separate test data from expected behavior."],
    ["3. Plan workflow", "Use Qwen AI for steps, assertions, screenshots."],
    ["4. Ground selectors", "Repair invented or broad selectors using real controls."],
    ["5. Save test", "Persist source, intent summary, expected result, and steps."]
  ];
  stages.forEach((s, i) => node(slide, ctx, 82 + i * 224, 235, 190, 190, s[0], s[1], i % 2 ? "#F0FDF4" : "#EFF6FF", [C.blue, C.teal, C.amber, C.blue, C.teal][i]));
  ctx.addText(slide, { x: 120, y: 505, w: 990, h: 64, text: "If Ollama/Qwen is unavailable or invalid, deterministic fallback still creates useful tests. This avoids a blank or broken system during demo.", fontSize: 24, color: C.ink, align: "center" });
  footer(slide, ctx, 5);
  return slide;
}
