---
task_id: 2026-05-25-ui-phase6-focus-projection
status: complete
session_goal: "Implement UI Phase 6 focus projection as the first Solver Evidence Workbench interaction primitive and push the validated node."
archive_target: docs/completed-tasks/2026-05-25-ui-phase6-focus-projection/
experience_links: []
---

# UI Phase 6 Focus Projection

## Task Objective

Add the next UI workbench step to the plan, implement pure focus projection for
table selection and replay, connect rigid-set/geometry/constraint table
selection to canvas highlighting, and leave a validated handoff.

## Scope And Non-Goals

In scope:

- Phase 6 detailed work plan;
- Python `viewer_bridge` focus projection helpers;
- Tk table-selection orchestration in `platform_gui.py`;
- replay focus migration out of GUI-local logic;
- pure unit tests and UI QA checks;
- completed-task archive and index entry.

Out of scope:

- canvas hit testing;
- diagnostic overlays or residual states;
- scene/history schema changes;
- solver, runtime, C++ contract, or IO behavior changes;
- browser, HTTP, Figma, or external viewer dependencies;
- manual desktop GUI run.

## Interaction Summary

The user accepted the recommendation to implement Phase 6 next and authorized
the agent to proceed rhythmically and push at validated nodes. The work
therefore opened a scoped implementation task, updated the plan, implemented
the focus projection slice, verified it with pure tests, and prepared this
archive for commit and push.

## Work Completed

- Added `docs/architecture/93-ui-phase6-focus-projection-work-plan.md` with the
  detailed Phase 6 implementation plan and focus projection contract.
- Updated `docs/architecture/77-ui-design-development-plan-report.md` to mark
  Phase 6 complete and Phase 7 as the next standalone work item.
- Added `selection_focus(...)` to `python/gcs_viz/viewer_bridge.py`.
- Added `history_focus_from_entry(...)` to `python/gcs_viz/viewer_bridge.py`.
- Replaced GUI-local replay focus construction in `platform_gui.py`.
- Bound rigid-set, geometry, and constraint table selection to canvas focus.
- Preserved replay focus precedence while replay is active.
- Added no-Tk unit coverage for selection and history focus projection.

## Files And Artifacts

- `docs/architecture/93-ui-phase6-focus-projection-work-plan.md`: detailed plan,
  focus contract, evidence, and residual risks.
- `docs/architecture/77-ui-design-development-plan-report.md`: Phase 6 status
  and next-step update.
- `python/gcs_viz/viewer_bridge.py`: pure projection helpers.
- `python/gcs_viz/platform_gui.py`: table-selection event wiring and replay
  focus consumption.
- `tests/tools/test_gcs_viz_history_replay.py`: focus projection tests.
- `docs/agentic/tasks/2026-05-25-ui-phase6-focus-projection.md`: task card.
- `docs/completed-tasks/2026-05-25-ui-phase6-focus-projection/README.md`: this
  archive.
- `docs/completed-tasks/README.md`: completed-task index entry.

## Evidence

Focused tests:

```text
$env:PYTHONPATH="$PWD\python"; python -m unittest tests.tools.test_gcs_viz_history_replay tests.tools.test_gcs_ui_qa

Result: 10 tests passed.
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
python -B -c "from pathlib import Path; files=[Path('python/gcs_viz/viewer_bridge.py'), Path('python/gcs_viz/platform_gui.py')]; [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print('syntax compile ok')"

Result: syntax compile ok.
```

Task-card validation:

```text
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-ui-phase6-focus-projection.md

Result: [OK] task-card passed.
```

Completed-task validation:

```text
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-ui-phase6-focus-projection\README.md

Result: [OK] completed-task-report passed.
```

Closure score:

```text
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-ui-phase6-focus-projection\README.md --min-score 30

Result: closure score 36/40, passed min score 30.
```

Whitespace check:

```text
git diff --check -- python\gcs_viz\viewer_bridge.py python\gcs_viz\platform_gui.py tests\tools\test_gcs_viz_history_replay.py docs\architecture\93-ui-phase6-focus-projection-work-plan.md docs\architecture\77-ui-design-development-plan-report.md docs\agentic\tasks\2026-05-25-ui-phase6-focus-projection.md

Result: passed; Git reported only CRLF normalization warnings.
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

- Keep focus projection in `python/gcs_viz/viewer_bridge.py`, not Tk handlers.
- Keep `visualizer.py` unchanged; it already consumes the `focus` dictionary.
- Let selection focus include related object IDs:
  rigid set -> geometries; geometry -> rigid set; constraint -> geometries and
  rigid sets.
- Return `None` for unfocused replay markers such as `Solve`.
- Preserve replay focus precedence while replay is active and restore current
  selection focus after replay stop or completion.

## Skipped Checks And Risks

- Manual GUI launch was skipped because the active Python interpreter lacks
  `matplotlib`.
- The implementation is covered by pure projection tests and syntax checks, but
  actual desktop highlighting still deserves a later visual smoke once GUI
  dependencies are installed.
- Existing contrast warnings remain advisory and are already tracked for later
  accessibility refinement.
- Unrelated dirty and staged worktree changes were preserved and not included
  in this task scope.

## Follow-Up

Recommended next task:

```text
Title: UI Phase 7 diagnostic overlay

Goal:
Add structured constraint diagnostic states to the focus/projection path so
satisfied, violated, and unknown constraints can be rendered in all view modes
without making the renderer infer solver truth.
```

Implementation should start from the Phase 6 focus projection helpers in
`python/gcs_viz/viewer_bridge.py`.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-25-ui-phase6-focus-projection/`
- Task card:
  `docs/agentic/tasks/2026-05-25-ui-phase6-focus-projection.md`
- Branch:
  `codex-ui-phase6-focus-projection`
- Owning skill:
  `gcs-ui-design-steward`
- Specialist skills:
  `gcs-architecture-steward`, `gcs-python-gui-builder`
