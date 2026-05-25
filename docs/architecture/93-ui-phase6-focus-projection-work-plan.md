# UI Phase 6 Focus Projection Work Plan

Date: 2026-05-25

Status: complete.

Parent architecture:

- `docs/architecture/77-ui-design-development-plan-report.md`
- `docs/architecture/92-gcs-ui-architecture-adjustment-record.md`

Governing conventions:

- **GCS Evidence-First Interface Grammar**
- **GCS Quiet Technical Atelier**
- **GCS Visual Integrity Gate**

## Objective

Make selection a first-class workbench primitive by moving focus construction
into UI-neutral projection helpers and wiring table selection to canvas
highlighting.

This phase is the first implementation slice of the **GCS Solver Evidence
Workbench** adjustment. Later diagnostic overlays, constraint-manager filters,
repair drafts, and local-to-global inspectors should reuse this projection
shape rather than inventing separate UI state.

## Scope

In scope:

- pure focus projection helpers in `python/gcs_viz/viewer_bridge.py`;
- replay focus construction moved out of `platform_gui.py`;
- table-selection handlers for rigid sets, geometries, and constraints;
- selection-to-canvas highlighting in all existing renderer modes through the
  existing `focus` dictionary;
- focused tests that do not import Tk.

Out of scope:

- canvas hit testing;
- diagnostic constraint states;
- solver report parsing changes;
- scene schema or history schema changes;
- renderer redesign;
- browser, HTTP, or external viewer dependencies.

## Detailed Execution Plan

1. Add projection helpers.
   - Add `selection_focus(...)` for rigid-set, geometry, and constraint table
     selection.
   - Add `history_focus_from_entry(...)` for replay steps.
   - Add a small normalization helper so focus IDs are sorted, unique, and
     integer-safe.

2. Replace GUI-local replay focus logic.
   - Import `history_focus_from_entry` in `platform_gui.py`.
   - Remove the GUI method that builds replay focus internally.
   - Keep replay focus precedence while replay is active.

3. Wire table selection.
   - Bind `<<TreeviewSelect>>` for rigid set, geometry, and constraint tables.
   - Build selection focus from selected row IDs.
   - Redraw the current canvas with selection focus when replay is not active.
   - Preserve selection focus across view changes and manual refresh.

4. Validate without desktop dependency.
   - Extend `tests/tools/test_gcs_viz_history_replay.py` or adjacent tests for
     selection and history focus projection.
   - Run Python compile/import checks for `python/gcs_viz`.
   - Run focused unittest coverage for viewer bridge projection.

5. Update lifecycle records.
   - Mark this plan complete or record residual risks.
   - Fill task-card evidence.
   - Create completed-task archive, validate it, score it, commit scoped files,
     and push the branch.

## Focus Projection Contract

Projection helpers produce either `None` or a dictionary with this shape:

```text
{
  "mode": "selection" | "replay",
  "rigid_set_ids": [int, ...],
  "geometry_ids": [int, ...],
  "constraint_ids": [int, ...],
}
```

Rules:

- IDs are sorted and unique.
- Bad IDs are ignored.
- Selecting a rigid set highlights that rigid set and its geometries.
- Selecting a geometry highlights the geometry and its rigid set.
- Selecting a constraint highlights the constraint, attached geometries, and
  their rigid sets.
- Replay focus has precedence over table-selection focus while replay is
  active.
- The renderer must not infer solver meaning from focus state; it only draws
  supplied focus.

## Acceptance Gates

- Selecting a rigid set, geometry, or constraint row highlights the
  corresponding object family in the active viewport.
- Replay highlighting still works and is not canceled by selection.
- View changes preserve selection highlighting outside replay.
- Focus projection is tested without importing Tk.
- No solver truth moves into `platform_gui.py` or `visualizer.py`.

## Verification Plan

```bat
python -m compileall -q python\gcs_viz
set PYTHONPATH=%CD%\python
python -m unittest tests.tools.test_gcs_viz_history_replay
python -c "import gcs_viz.platform_gui; print('platform_gui import ok')"
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-ui-phase6-focus-projection.md
```

Manual GUI launch remains optional for this phase because the core projection
contract is covered by pure tests and no rendered styling changed.

## Completion Summary

Completed on 2026-05-25.

Implemented:

- `selection_focus(...)` in `python/gcs_viz/viewer_bridge.py`;
- `history_focus_from_entry(...)` in `python/gcs_viz/viewer_bridge.py`;
- table-selection bindings for rigid sets, geometries, and constraints in
  `python/gcs_viz/platform_gui.py`;
- replay focus migration from GUI-local logic to viewer-bridge projection;
- focused unit tests in `tests/tools/test_gcs_viz_history_replay.py`.

Validation:

```bat
$env:PYTHONPATH="$PWD\python"; python -m unittest tests.tools.test_gcs_viz_history_replay tests.tools.test_gcs_ui_qa
python tools\ui_qa\gcs_ui_qa.py
python -B -c "from pathlib import Path; files=[Path('python/gcs_viz/viewer_bridge.py'), Path('python/gcs_viz/platform_gui.py')]; [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print('syntax compile ok')"
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-ui-phase6-focus-projection.md
```

Observed result:

- focused unittest suite passed 10/10;
- UI QA passed with existing advisory contrast warnings and skipped headless
  render because `matplotlib` is missing in the current interpreter;
- no-write syntax compile passed;
- task-card validation passed.

Skipped or degraded checks:

- `python -m compileall -q python\gcs_viz` could not write to the existing
  `__pycache__` directory in this environment.
- `platform_gui` import could not complete because the active Python
  interpreter does not have `matplotlib` installed. This is an environment
  dependency gap, not a syntax failure.
