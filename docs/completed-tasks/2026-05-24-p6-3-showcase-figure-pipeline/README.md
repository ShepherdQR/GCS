---
task_id: 2026-05-24-p6-3-showcase-figure-pipeline
status: complete
session_goal: "Produce the P6.3 showcase figure through a tokenized HTML compositor and visual-integrity gates."
archive_target: docs/completed-tasks/2026-05-24-p6-3-showcase-figure-pipeline/
experience_links:
  - docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-24-p6-3-showcase-figure-pipeline-forging-note.md
---

# P6.3 Showcase Figure Pipeline

## Task Objective

Create a production Figure 72 HTML artifact that uses the P6.1 brief, P6.2
fixture evidence, shared visual tokens, and P5 visual-integrity gates.

## Scope And Non-Goals

In scope:

- add a Figure 72 spec;
- add a tokenized HTML compositor;
- generate the Figure 72 HTML artifact;
- extend text-overflow and overlap/contrast gates to Figure 72;
- promote compositor freshness and tests into default quality gates;
- update atlas, roadmap, and archive.

Out of scope:

- installing Figma or MCP tooling;
- adding graph/chart dependencies;
- deleting the legacy SVG;
- adding a Figure 72 screenshot baseline.

## Interaction Summary

P6.2 made fixture evidence renderer-consumable. P6.3 uses that evidence to
produce a layout-aware HTML showcase artifact rather than treating the older
coordinate SVG as the final production surface.

## Work Completed

- Added `tools/architecture_visualization/specs/figure72.yaml`.
- Added `tools/architecture_visualization/showcase_scene_html_compositor.py`.
- Generated `figure72-gcs-integrated-showcase-scene.html`.
- Added `tests/tools/test_showcase_scene_html_compositor.py`.
- Extended `gcs_text_overflow.py` and `gcs_overlap_contrast.py` to scan Figure
  72 HTML.
- Added compositor check and tests to default quality gates.
- Updated the architecture atlas and CI quality-gate docs.

## Files And Artifacts

- `tools/architecture_visualization/specs/figure72.yaml`
- `tools/architecture_visualization/showcase_scene_html_compositor.py`
- `docs/architecture/70-visualization/assets/figure72-gcs-integrated-showcase-scene.html`
- `tests/tools/test_showcase_scene_html_compositor.py`
- `tools/ui_qa/gcs_text_overflow.py`
- `tools/ui_qa/gcs_overlap_contrast.py`
- `tools/agentic_design/agentic_toolkit.py`
- `tests/tools/test_agentic_toolkit.py`
- `docs/architecture/90-p6-3-showcase-figure-pipeline.md`
- `docs/architecture/70-visualization/gcs-architecture-atlas.md`

## Evidence

```text
python -B tools\architecture_visualization\showcase_scene_html_compositor.py --check
Figure 72 showcase HTML is up to date.

python -m unittest tests.tools.test_showcase_scene_html_compositor
Ran 3 tests.
OK

python -B tools\ui_qa\gcs_text_overflow.py
GCS text overflow checks passed (170 budgets)

python -B tools\ui_qa\gcs_overlap_contrast.py
GCS overlap/contrast checks passed (13 boxes, 90 contrast targets)

python tools\agentic_design\agentic_toolkit.py run-quality-gates
All requested quality gates passed, including
python.showcase_scene_html_compositor,
python.showcase_scene_html_compositor_tests, python.gcs_text_overflow, and
python.gcs_overlap_contrast.
```

## Decisions

- Decision: make HTML the P6.3 production path. Rationale: the showcase is
  dense, evidence-rich, and text-heavy, so browser layout is a better fit than
  coordinate SVG text placement.
- Decision: keep the SVG as a legacy atlas artifact. Rationale: it remains a
  deterministic scene view, but the HTML artifact now carries the production
  panel/evidence hierarchy.
- Decision: do not add a Figure 72 screenshot baseline in P6.3. Rationale:
  P6.4 first needs to judge whether external design tooling or browser export
  work is worth the extra boundary.

## Skipped Checks And Risks

- Full quality gates passed before commit; no P6.3-specific source checks were
  skipped.
- Figure 72 has no promoted PNG/PDF review baseline yet.
- Art Director approval is conditional until a browser-rendered review artifact
  or external review surface is chosen.

## Follow-Up

- Execute P6.4 Figma MCP decision.
- Use the P6.3 HTML artifact as the concrete repo-native alternative in that
  decision.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-24-p6-3-showcase-figure-pipeline/`
- Related experience:
  - `docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-24-p6-3-showcase-figure-pipeline-forging-note.md`
- Skill, eval, fixture, or tool update needed: P6.4 should decide whether
  Figma MCP adds collaboration or editable-layout value beyond this HTML path.
