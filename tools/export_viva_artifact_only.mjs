import path from "node:path";

import {
  createSlideContext,
  ensureArtifactToolWorkspace,
  importArtifactTool,
  importModuleFresh,
  resolveSlideFunction,
} from "file:///C:/Users/Acer/.codex/plugins/cache/openai-primary-runtime/presentations/26.601.10930/skills/presentations/scripts/artifact_tool_utils.mjs";

const root = process.cwd();
const workspace = path.join(root, "outputs", "manual-viva-presentation", "presentations", "jira-agent-viva");
const slidesDir = path.join(workspace, "slides");
const out = path.join(root, "docs", "AI-Web-Test-Automation-Viva.pptx");

await ensureArtifactToolWorkspace(workspace);
const artifact = await importArtifactTool(workspace);
const { Presentation, PresentationFile } = artifact;
const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });

for (let i = 1; i <= 10; i += 1) {
  const file = path.join(slidesDir, `slide-${String(i).padStart(2, "0")}.mjs`);
  const mod = await importModuleFresh(file);
  const { fn } = resolveSlideFunction(mod, undefined, i);
  const ctx = createSlideContext(artifact, {
    slideSize: { width: 1280, height: 720 },
    slideNumber: i,
    workspaceDir: workspace,
    outputDir: path.dirname(out),
    assetDir: path.join(workspace, "assets"),
  });
  await fn(presentation, ctx);
}

const pptx = await PresentationFile.exportPptx(presentation);
await pptx.save(out);
console.log(JSON.stringify({ out, slideCount: presentation.slides.count }, null, 2));
