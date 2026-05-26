---
task_id: 2026-05-26-ui-viewer-figure-integration
status: complete
request: "Execute the six-step plan to integrate UI, viewer, scientific figures, visual evidence manifests, D5 demo packaging, and viewer phase 8/9 refinements; commit and push the isolated branch."
scope: implementation
risk: medium
owning_agent: gcs-ui-design-steward
specialist_agents:
  - gcs-architecture-steward
  - gcs-viewer-bridge-steward
  - gcs-scientific-figure-producer
  - gcs-python-gui-builder
affected_contracts:
  - viewer_bridge projection helpers
  - GCS Scientific Figure Pipeline
  - GCS Visual Integrity Gate
affected_paths:
  - docs/agentic/
  - docs/architecture/
  - docs/product/
  - python/gcs_viz/
  - tools/architecture_visualization/
  - tools/ui_qa/
  - tests/tools/
required_evidence:
  - focused viewer and visual QA tests
  - Figure 72 browser export
  - UI QA
  - screenshot baseline
  - validate-task-card
  - validate-completed-task-report
  - score-closure-report
  - validate-docs
human_gate_required: false
human_gate_reason: "User explicitly asked to execute the six-step plan and push the scoped result."
---

# 2026-05-26-ui-viewer-figure-integration

## Scope

Execute the six-step UI/viewer/scientific-figure integration plan:

- add an architecture integration plan that binds viewer projections, UI QA,
  scientific figures, and product demos into one evidence chain;
- update the narrative map, architecture README, demo ladder, and demo index;
- harden Figure 72 P7 review artifacts with browser PNG/PDF export,
  screenshot baseline coverage, atlas/report links, and Art Director review;
- complete viewer Phase 8 and Phase 9 refinements through contrast-safe state
  text tokens, dynamic graph-node label contrast, replay frame projection, and
  viewport replay speed control;
- add a shared visual evidence manifest;
- create a D5 Solver Evidence Workbench demo package.

## Non-Goals

- Do not change solver runtime semantics.
- Do not compute solver rank, residual, gluing, conflict, redundancy, or
  obstruction truth in the viewer.
- Do not add Figma MCP, a browser-hosted app, or a new GUI stack.
- Do not include unrelated repository-audit/session-efficiency work from the
  original dirty `master` checkout.

## Context To Read

- `docs/architecture/README.md`
- Owning skill: `gcs-ui-design-steward`
- `gcs-architecture-steward`
- `gcs-viewer-bridge-steward`
- `gcs-scientific-figure-producer`
- `gcs-python-gui-builder`
- `task-scoped-session-closer`

## Acceptance Gates

- UI/viewer/scientific-figure line has one active integration plan.
- Figure 72 has first-class PNG/PDF review artifacts and screenshot baseline
  coverage.
- Viewer Phase 8 and Phase 9 have focused implementation and no-Tk tests.
- D5 demo package links source scene, projection evidence, review artifacts,
  QA evidence, and residual risk.
- Required evidence is produced or a reason is recorded.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-ui-viewer-figure-integration.md
python -B -m unittest tests.tools.test_gcs_viz_history_replay tests.tools.test_gcs_ui_qa tests.tools.test_browser_export tests.tools.test_gcs_screenshot_baseline
python -B -c "from pathlib import Path; files=[Path('python/gcs_viz/viewer_bridge.py'),Path('python/gcs_viz/platform_gui.py'),Path('python/gcs_viz/visualizer.py'),Path('python/gcs_viz/color_scheme.py'),Path('tools/ui_qa/gcs_ui_qa.py'),Path('tools/architecture_visualization/browser_export.py')]; [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print('syntax compile ok')"
python tools\architecture_visualization\showcase_fixture_evidence.py
python tools\architecture_visualization\showcase_scene_html_compositor.py --check
python tools\ui_qa\gcs_ui_qa.py
python tools\ui_qa\gcs_screenshot_baseline.py
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-ui-viewer-figure-integration\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-ui-viewer-figure-integration\README.md --min-score 30
python tools\agentic_design\agentic_toolkit.py validate-docs
```

## Evidence Bundle

- Created isolated worktree branch
  `codex/2026-05-26-ui-viewer-figure-integration` from current
  `origin/master` to avoid unrelated dirty files in the original checkout.
- `python -B tools\architecture_visualization\browser_export.py --figure figure72 --formats png,pdf --viewport 1600x1400 --timeout-seconds 90 --require-browser`: passed after sandbox escalation; generated Figure 72 PNG/PDF and token-passing browser manifest.
- `python -B -m unittest tests.tools.test_gcs_viz_history_replay tests.tools.test_gcs_ui_qa tests.tools.test_browser_export tests.tools.test_gcs_screenshot_baseline`: passed 24/24.
- Syntax compile for changed Python files: passed.
- `python tools\architecture_visualization\showcase_fixture_evidence.py`: passed, 2 fixtures checked.
- `python tools\architecture_visualization\showcase_scene_html_compositor.py --check`: passed, Figure 72 HTML up to date.
- `python tools\ui_qa\gcs_ui_qa.py`: passed with existing advisory graphic-accent contrast warnings and headless render skipped because `matplotlib` is missing.
- `python tools\ui_qa\gcs_screenshot_baseline.py`: passed, 2 baselines checked.
- `validate-completed-task-report`: passed.
- `score-closure-report --min-score 30`: passed with 36/40.

## Residual Risks

- Phase 10 manual GUI screenshot review remains future work because the local
  interpreter still lacks `matplotlib` for headless render/import coverage.
- The legacy `_build_left_panel_legacy_unused` function remains retired rather
  than physically removed in this batch; active GUI builders remain the
  inspected path.
- Current Python diagnostic states still rely on safe text parsing when
  structured report projection is unavailable.
