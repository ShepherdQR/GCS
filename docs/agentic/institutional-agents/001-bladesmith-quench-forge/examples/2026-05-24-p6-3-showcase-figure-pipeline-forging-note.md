# Experience Forging Note: P6.3 Showcase Figure Pipeline

Date: 2026-05-24

Role: `Bladesmith Quench-Forge`

Status: reusable

## Source Scope

- Session/task: `2026-05-24-p6-3-showcase-figure-pipeline`
- Time range: P6.3 showcase HTML figure production
- Source artifacts:
  - `tools/architecture_visualization/showcase_scene_html_compositor.py`
  - `tools/architecture_visualization/specs/figure72.yaml`
  - `docs/architecture/70-visualization/assets/figure72-gcs-integrated-showcase-scene.html`
  - `docs/architecture/90-p6-3-showcase-figure-pipeline.md`
  - `docs/completed-tasks/2026-05-24-p6-3-showcase-figure-pipeline/README.md`

## Raw Material Classification

| Type | Notes |
| --- | --- |
| Facts | Figure 72 now has a tokenized HTML production artifact with 69 text budgets, 7 layout boxes, and 69 contrast targets. |
| Decisions | Treat HTML as the P6.3 production path and keep SVG as legacy atlas evidence. |
| Preferences | Dense showcase figures should consume metadata rather than hard-code evidence facts. |
| Hypotheses | Repo-native HTML may be enough unless P6.4 identifies a collaboration/editable-layout gap. |
| Open questions | Whether to add a browser PNG/PDF baseline or use Figma MCP for review. |

## Forged Lessons

| Lesson | Trigger | Action | Guardrail | Evidence | Boundary |
| --- | --- | --- | --- | --- | --- |
| Upgrade dense coordinate figures with layout-aware HTML when text evidence grows. | The showcase needs seven evidence panels and negative/public gate evidence. | Build a tokenized HTML compositor from scene and metadata. | Keep domain glyph coordinates small and keep text in layout flow. | Text overflow and overlap/contrast checks pass across Figure 71 and 72. | Ends when browser review artifacts or Figma handoff are required. |
| Make generated figure freshness a gate. | A generated HTML asset is committed. | Add a `--check` mode to fail stale generated output. | Do not let default gates rewrite tracked assets silently. | `python.showcase_scene_html_compositor` runs in quality gates. | Applies to generated production artifacts. |

## Rejected Generalizations

| Claim | Why rejected or provisional | Evidence needed |
| --- | --- | --- |
| "The old SVG must be deleted." | It remains useful as a deterministic atlas view and has existing references. | Deprecation plan after HTML/PDF review artifacts exist. |
| "Figma MCP is unnecessary now." | P6.3 proves repo-native HTML, but P6.4 still needs to judge review and collaboration gaps. | P6.4 governance decision. |

## Recommended Promotion

Choose one:

- update a checklist.

Rationale:

Generated HTML figures should have a freshness check and should join the same
text, contrast, and overlap gates as earlier production figures.

## Follow-Up

- Use the P6.3 HTML artifact as evidence in the Figma MCP decision.
- If Figma is deferred, consider adding a Figure 72 browser review PNG/PDF
  baseline as the next repo-native review surface.
