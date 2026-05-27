---
task_id: 2026-05-26-ui-viewer-figure-integration
status: complete
session_goal: "Integrated the UI/viewer/scientific-figure narrative through a shared evidence chain, hardened Figure 72 review artifacts, completed viewer Phase 8 and Phase 9 refinements, added a visual evidence manifest and D5 demo package, then prepared scoped validation and push."
archive_target: docs/completed-tasks/2026-05-26-ui-viewer-figure-integration/
experience_links:
  - docs/agentic/experience/001-task-scoped-session-closure/
---

# 2026-05-26-ui-viewer-figure-integration

## Task Objective

Execute and archive the six-step plan to integrate GCS UI, viewer bridge,
scientific figures, visual QA, and product demo packaging into one
evidence-first narrative line.

## Scope And Non-Goals

In scope:

- Architecture plan for UI/viewer/scientific-figure integration.
- Narrative map, architecture README, demo ladder, and demo index updates.
- Figure 72 P7 review artifact hardening.
- Viewer Phase 8 contrast/accessibility refinement.
- Viewer Phase 9 replay history-frame projection refinement.
- Shared visual evidence manifest.
- D5 Solver Evidence Workbench demo package.
- Focused validation, task card, archive, commit, and push.

Out of scope:

- Solver runtime semantics, numeric behavior, report codes, and scene IO
  migrations.
- Figma MCP or external design-tool installation.
- A new browser/web GUI stack.
- Unrelated repository-audit/session-efficiency changes from the original dirty
  local checkout.

## Interaction Summary

The user first asked for a plan to strengthen the split UI/viewer/scientific
figures line in the narrative map. The resulting plan named six execution
items: integration plan, narrative update, Figure 72 P7 hardening, viewer Phase
8/9 continuation, D5 demo packaging, and visual evidence manifest. The user
then asked to execute those six items and push.

Work was moved to the isolated branch
`codex/2026-05-26-ui-viewer-figure-integration` in a sibling worktree so the
original dirty `master` checkout would not be mixed into the commit.

## Work Completed

- Added `docs/architecture/97-ui-viewer-figure-integration-plan.md` to define
  the shared evidence chain:
  `solver/replay report -> viewer_bridge projection -> workbench overlay ->
  screenshot/QA artifact -> scientific figure/demo package`.
- Updated `docs/architecture/95-gcs-narrative-map.md`,
  `docs/architecture/README.md`, and `docs/product/gcs-demo-ladder.md` so the
  split visual line is now tracked as an active integration line.
- Added Figure 72 review PNG/PDF artifacts and browser manifest, then promoted
  the PNG into the screenshot baseline manifest.
- Updated Figure 72 atlas/report docs and recorded conditional Art Director
  approval.
- Added contrast-safe `STATE_TEXT_COLORS`, dynamic graph-node label contrast,
  UI QA contrast checks, and the Phase 8 note.
- Added `project_history_frame(...)`, replay deletion hints, mirrored replay
  speed control in the viewport rail, tests, and the Phase 9 note.
- Added `docs/architecture/70-visualization/visual-evidence-manifest.md`.
- Added the D5 Solver Evidence Workbench demo package under
  `docs/product/demos/d5-solver-evidence-workbench/`.

## Files And Artifacts

- `docs/architecture/97-ui-viewer-figure-integration-plan.md`: active
  integration plan.
- `docs/architecture/70-visualization/visual-evidence-manifest.md`: shared
  visual evidence index.
- `docs/product/demos/d5-solver-evidence-workbench/README.md` and
  `evidence.md`: first D5 demo package.
- `docs/architecture/70-visualization/assets/figure72-gcs-integrated-showcase-scene.review.png`:
  Figure 72 review PNG baseline artifact.
- `docs/architecture/70-visualization/assets/figure72-gcs-integrated-showcase-scene.review.pdf`:
  Figure 72 review PDF.
- `docs/architecture/70-visualization/assets/figure72-gcs-integrated-showcase-browser-export.json`:
  Figure 72 browser export manifest.
- `docs/architecture/70-visualization/assets/screenshot-baselines.json`:
  added Figure 72 PNG exact hash baseline.
- `python/gcs_viz/color_scheme.py`: added `STATE_TEXT_COLORS` and graph-node
  label text tokens.
- `python/gcs_viz/viewer_bridge.py`: added `project_history_frame(...)`.
- `python/gcs_viz/platform_gui.py`: consumes contrast-safe state text and
  history-frame projection; mirrors replay speed in the viewport rail.
- `python/gcs_viz/visualizer.py`: dynamic graph-node label color selection.
- `tools/ui_qa/gcs_ui_qa.py`: checks state text and graph-node label contrast.
- `tools/architecture_visualization/browser_export.py` and
  `tools/architecture_visualization/specs/figure72.yaml`: Figure 72 token smoke
  support and review artifact paths.
- `tests/tools/test_gcs_viz_history_replay.py`,
  `tests/tools/test_browser_export.py`: focused regression coverage.

## Evidence

```text
python -B tools\architecture_visualization\browser_export.py --figure figure72 --formats png,pdf --viewport 1600x1400 --timeout-seconds 90 --require-browser
PASS after sandbox escalation; generated Figure 72 review PNG/PDF and token-passing browser manifest.

python -B -m unittest tests.tools.test_gcs_viz_history_replay tests.tools.test_gcs_ui_qa tests.tools.test_browser_export tests.tools.test_gcs_screenshot_baseline
PASS: 24/24 tests.

python -B -c "... compile changed Python files ..."
PASS: syntax compile ok.

python tools\architecture_visualization\showcase_fixture_evidence.py
PASS: 2 fixtures checked.

python tools\architecture_visualization\showcase_scene_html_compositor.py --check
PASS: Figure 72 showcase HTML is up to date.

python tools\ui_qa\gcs_ui_qa.py
PASS with advisory graphic-accent contrast warnings; headless render skipped because matplotlib is missing.

python tools\ui_qa\gcs_screenshot_baseline.py
PASS: 2 baselines checked.
```

## Decisions

- Use a sibling isolated worktree and branch because the original checkout had
  unrelated dirty files and a moving `master` state.
- Treat Figure 72 browser review artifacts as first-class P7 output and keep
  the deterministic SVG as secondary legacy atlas output.
- Keep Figma MCP deferred because the repo-native HTML/PNG/PDF path now covers
  the concrete review need.
- Split graphic state colors from small-text state colors rather than
  darkening the graphic evidence palette.
- Keep the live GUI screenshot as Phase 10 follow-up instead of pretending the
  Figure 72 artifact proves desktop GUI rendering.

## Skipped Checks And Risks

- `tools/ui_qa/gcs_ui_qa.py` skipped optional headless render because the
  active interpreter does not have `matplotlib`.
- Manual desktop GUI review was not run; it remains Phase 10.
- `_build_left_panel_legacy_unused` remains physically present but retired and
  outside active GUI builder checks.
- Python diagnostic overlays still use safe text parsing until structured
  solver report projection is available.

## Follow-Up

- Run Phase 10 manual visual QA and add a viewer screenshot entry to the visual
  evidence manifest.
- Start Phase 11 constraint-manager and repair-draft projection once diagnostic
  projections are stable enough.
- Add D1 and D2 product demo packages so earlier ladder levels are as concrete
  as D5.

## Archive Handoff

- Archive path: `docs/completed-tasks/2026-05-26-ui-viewer-figure-integration/`
- Related experience:
  - docs/agentic/experience/001-task-scoped-session-closure/
- Skill, eval, fixture, or tool update needed: none; this task reused existing
  stewardship skills and extended existing browser/UI QA tools.
