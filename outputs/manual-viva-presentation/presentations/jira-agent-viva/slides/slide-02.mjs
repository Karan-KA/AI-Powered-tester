import { bg, bulletList, C, footer, panel, title } from "./common.mjs";

export async function slide02(presentation, ctx) {
  const slide = presentation.slides.add();
  bg(slide, ctx);
  title(slide, ctx, "Problem", "Manual web testing is powerful, but hard to scale for changing applications.");
  panel(slide, ctx, 66, 178, 520, 420);
  ctx.addText(slide, { x: 92, y: 208, w: 430, h: 34, text: "Traditional automation friction", fontSize: 24, bold: true, color: C.ink });
  bulletList(slide, ctx, 98, 270, [
    "Testers write scripts manually for every workflow.",
    "Locators break when websites change UI structure.",
    "Screenshots, logs, and reports are often separate.",
    "Non-programmers cannot easily create automation."
  ], { w: 420, size: 18, gap: 54, dot: C.red });
  panel(slide, ctx, 666, 178, 460, 420, "#F0F9FF");
  ctx.addText(slide, { x: 700, y: 218, w: 375, h: 48, text: "Project idea", fontSize: 26, bold: true, color: C.blue });
  ctx.addText(slide, {
    x: 700, y: 286, w: 370, h: 180,
    text: "Let the user describe a testing requirement in plain English. The system should generate, execute, store, and explain the test run from one dashboard.",
    fontSize: 24, color: C.ink,
  });
  ctx.addShape(slide, { x: 700, y: 510, w: 340, h: 4, fill: C.blue, line: ctx.line("#00000000", 0) });
  footer(slide, ctx, 2);
  return slide;
}
