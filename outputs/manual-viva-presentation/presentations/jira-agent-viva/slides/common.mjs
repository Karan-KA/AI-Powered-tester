export const C = {
  ink: "#101828",
  muted: "#667085",
  line: "#D0D5DD",
  paper: "#F8FAFC",
  panel: "#FFFFFF",
  blue: "#2563EB",
  teal: "#0F766E",
  amber: "#D97706",
  red: "#B42318",
  slate: "#1F2937",
  softBlue: "#DBEAFE",
  softTeal: "#CCFBF1",
  softAmber: "#FEF3C7",
};

export function bg(slide, ctx) {
  ctx.addShape(slide, { x: 0, y: 0, w: 1280, h: 720, fill: C.paper });
  ctx.addShape(slide, { x: 0, y: 0, w: 1280, h: 8, fill: C.blue });
}

export function title(slide, ctx, kicker, claim) {
  ctx.addText(slide, {
    x: 62, y: 42, w: 250, h: 24, text: kicker.toUpperCase(),
    fontSize: 12, bold: true, color: C.blue, typeface: ctx.fonts.body,
  });
  ctx.addText(slide, {
    x: 62, y: 70, w: 1030, h: 72, text: claim,
    fontSize: 38, bold: true, color: C.ink, typeface: ctx.fonts.title,
  });
}

export function footer(slide, ctx, n) {
  ctx.addText(slide, {
    x: 62, y: 682, w: 520, h: 20,
    text: "AI-Powered Web Test Automation Platform",
    fontSize: 10, color: "#98A2B3",
  });
  ctx.addText(slide, {
    x: 1172, y: 682, w: 44, h: 20, text: String(n).padStart(2, "0"),
    fontSize: 10, color: "#98A2B3", align: "right",
  });
}

export function panel(slide, ctx, x, y, w, h, fill = C.panel) {
  return ctx.addShape(slide, {
    x, y, w, h, fill, line: ctx.line(C.line, 1), geometry: "roundRect",
  });
}

export function pill(slide, ctx, x, y, text, fill = C.softBlue, color = C.blue) {
  ctx.addShape(slide, { x, y, w: 132, h: 30, fill, line: ctx.line("#00000000", 0), geometry: "roundRect" });
  ctx.addText(slide, { x: x + 10, y: y + 7, w: 112, h: 18, text, fontSize: 11, bold: true, color, align: "center" });
}

export function bulletList(slide, ctx, x, y, items, opts = {}) {
  const color = opts.color || C.ink;
  const size = opts.size || 20;
  items.forEach((item, i) => {
    const yy = y + i * (opts.gap || 44);
    ctx.addShape(slide, { x, y: yy + 8, w: 8, h: 8, fill: opts.dot || C.blue, line: ctx.line("#00000000", 0), geometry: "ellipse" });
    ctx.addText(slide, { x: x + 22, y: yy, w: opts.w || 470, h: 36, text: item, fontSize: size, color });
  });
}

export function metric(slide, ctx, x, y, value, label, color = C.teal) {
  panel(slide, ctx, x, y, 210, 112);
  ctx.addText(slide, { x: x + 20, y: y + 18, w: 170, h: 42, text: value, fontSize: 34, bold: true, color, typeface: ctx.fonts.title });
  ctx.addText(slide, { x: x + 20, y: y + 63, w: 170, h: 40, text: label, fontSize: 14, color: C.muted });
}

export function node(slide, ctx, x, y, w, h, label, sub, fill = C.panel, accent = C.blue) {
  panel(slide, ctx, x, y, w, h, fill);
  ctx.addShape(slide, { x, y, w: 6, h, fill: accent, line: ctx.line("#00000000", 0) });
  ctx.addText(slide, { x: x + 18, y: y + 16, w: w - 34, h: 26, text: label, fontSize: 18, bold: true, color: C.ink });
  if (sub) ctx.addText(slide, { x: x + 18, y: y + 46, w: w - 34, h: h - 56, text: sub, fontSize: 13, color: C.muted });
}

export function arrow(slide, ctx, x1, y1, x2, y2, color = C.blue) {
  const w = Math.max(2, x2 - x1);
  ctx.addShape(slide, { x: x1, y: y1, w, h: 3, fill: color, line: ctx.line("#00000000", 0) });
  ctx.addShape(slide, { x: x2 - 9, y: y2 - 6, w: 12, h: 12, fill: color, line: ctx.line("#00000000", 0), geometry: "triangle" });
}
