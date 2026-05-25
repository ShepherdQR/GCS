---
task_id: 2026-05-25-ui-phase7-diagnostics-overlay
status: complete
session_goal: "Implement UI Phase 7 diagnostics overlay on top of the Phase 6 focus projection path and push the validated node."
archive_target: docs/completed-tasks/2026-05-25-ui-phase7-diagnostics-overlay/
experience_links: []
---

# UI Phase 7 Diagnostics Overlay

## Task Objective

Extend the Phase 6 focus projection path with conservative constraint diagnostic
states so solve results can become visible in the viewport without moving
solver truth into the renderer.

## Scope And Non-Goals

In scope:

- Phase 7 detailed work plan;
- pure constraint-state projection helpers;
- safe solver-text extraction for recognizable constraint IDs;
- GUI diagnostic focus storage and merge with selection focus;
- renderer support for `satisfied`, `violated`, and `unknown` states;
- no-Tk unit tests and UI QA checks.

Out of scope:

- residual magnitudes;
- conflict or redundancy sets;
- repair drafts;
- C++ report schema changes;
- scene/history persistence changes;
- new rendering dependencies;
- manual desktop GUI run.

## Interaction Summary

The user authorized continued execution after the Phase 6 node. The task
therefore opened a scoped Phase 7 branch, created the detailed plan, implemented
diagnostic-state projection and rendering, validated the narrow contract, and
prepared this archive for commit and push.

## Work Completed

- Added `docs/architecture/94-ui-phase7-diagnostics-overlay-work-plan.md`.
- Updated `docs/architecture/77-ui-design-development-plan-report.md` to mark
  Phase 7 complete and Phase 8 as next.
- Added `constraint_state_projection(...)` in `viewer_bridge.py`.
- Added `constraint_states_from_solve_text(...)` in `viewer_bridge.py`.
- Added `combine_focus_with_constraint_states(...)` in `viewer_bridge.py`.
- Updated `platform_gui.py` so solve reports store diagnostic states and merge
  them with selection focus.
- Updated `visualizer.py` so supplied diagnostic states affect line color,
  width, alpha, labels, and legends in 3D, graph, and three-view modes.
- Added tests for projection normalization, unknown fallback, safe text parsing,
  and selection/diagnostic coexistence.

## Files And Artifacts

- `docs/architecture/94-ui-phase7-diagnostics-overlay-work-plan.md`: detailed
  plan and evidence.
- `docs/architecture/77-ui-design-development-plan-report.md`: Phase 7 status
  and next-step update.
- `python/gcs_viz/viewer_bridge.py`: pure constraint-state projection helpers.
- `python/gcs_viz/platform_gui.py`: GUI diagnostic focus orchestration.
- `python/gcs_viz/visualizer.py`: supplied-state rendering.
- `tests/tools/test_gcs_viz_history_replay.py`: projection and fallback tests.
- `docs/agentic/tasks/2026-05-25-ui-phase7-diagnostics-overlay.md`: task card.
- `docs/completed-tasks/2026-05-25-ui-phase7-diagnostics-overlay/README.md`:
  this archive.
- `docs/completed-tasks/README.md`: completed-task index entry.

## Evidence

Focused tests:

```text
$env:PYTHONPATH="$PWD\python"; python -m unittest tests.tools.test_gcs_viz_history_replay tests.tools.test_gcs_ui_qa

Result: 15 tests passed.
```

UI QA:

```text
python tools\ui_qa\gcs_ui_qa.py

Result: UI QA checks passed.
Notes: headless render skipped because matplotlib is missing; existing advisory
contrast warnings were reported for semantic accent colors on bg_panel_alt.
```

Syntax check without writing pycache:

```text
python -B -c "from pathlib import Path; files=[Path('python/gcs_viz/viewer_bridge.py'), Path('python/gcs_viz/platform_gui.py'), Path('python/gcs_viz/visualizer.py')]; [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print('syntax compile ok')"

Result: syntax compile ok.
```

Task-card validation:

```text
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-ui-phase7-diagnostics-overlay.md

Result: [OK] task-card passed.
```

Completed-task validation:

```text
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-ui-phase7-diagnostics-overlay\README.md

Result: [OK] completed-task-report passed.
```

Closure score:

```text
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-ui-phase7-diagnostics-overlay\README.md --min-score 30

Result: closure score 36/40, passed min score 30.
```

Environment-limited checks:

```text
python -m compileall -q python\gcs_viz

Result: failed because the active environment could not write existing
__pycache__ files.
```

```text
$env:PYTHONPATH="$PWD\python"; python -B -c "import gcs_viz.platform_gui; print('platform_gui import ok')"

Result: failed before GUI code ran because the active interpreter does not have
matplotlib installed.
```

## Decisions

- Keep diagnostic-state projection in `python/gcs_viz/viewer_bridge.py`.
- Parse per-constraint states only when solver text contains a recognizable
  constraint ID and `SATISFIED` or `VIOLATED`.
- Treat aggregate-only output as insufficient for per-constraint satisfied or
  violated overlays; fill `unknown` only as a conservative viewport state.
- Keep focus and diagnostics coexisting: focus controls emphasis and label
  detail, while diagnostic state controls evidence color.
- Keep `visualizer.py` as a renderer over supplied state, not a parser or solver
  diagnostic owner.

## Skipped Checks And Risks

- Manual GUI launch was skipped because the active Python interpreter lacks
  `matplotlib`.
- The code path is covered by pure projection tests and syntax checks, but the
  exact desktop visual result still needs a later GUI smoke once dependencies
  are installed.
- Existing contrast warnings remain advisory and are now more relevant for
  Phase 8.
- The unrelated dirty file `docs/research/OpusTime/OpusTime.md` was preserved
  and not included in this task scope.

## Follow-Up

Recommended next task:

```text
Title: UI Phase 8 accessibility and contrast refinement

Goal:
Separate graphic accent tokens from small-text state tokens, tighten diagnostic
label readability, and turn the remaining advisory contrast warnings into a
clear pass/fail policy where the design system is ready.
```

Phase 8 should begin from the active focus and diagnostic states now present in
Phases 6 and 7.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-25-ui-phase7-diagnostics-overlay/`
- Task card:
  `docs/agentic/tasks/2026-05-25-ui-phase7-diagnostics-overlay.md`
- Branch:
  `codex-ui-phase7-diagnostics-overlay`
- Owning skill:
  `gcs-ui-design-steward`
- Specialist skills:
  `gcs-architecture-steward`, `gcs-python-gui-builder`
