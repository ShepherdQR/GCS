# UI Phase 7 Diagnostics Overlay Work Plan

Date: 2026-05-25

Status: complete.

Parent architecture:

- `docs/architecture/77-ui-design-development-plan-report.md`
- `docs/architecture/92-gcs-ui-architecture-adjustment-record.md`
- `docs/architecture/93-ui-phase6-focus-projection-work-plan.md`

Governing conventions:

- **GCS Evidence-First Interface Grammar**
- **GCS Warm Evidence Tokens**
- **GCS Visual Integrity Gate**

## Objective

Make solve diagnostic state visible in the viewport by extending the existing
focus projection with conservative constraint states:

- `satisfied`
- `violated`
- `unknown`

This phase does not claim richer diagnostics than the current solver output can
support. If a constraint ID cannot be tied to a state, the UI must fall back to
`unknown` rather than inventing evidence.

## Scope

In scope:

- UI-neutral constraint-state projection helpers in
  `python/gcs_viz/viewer_bridge.py`;
- safe parsing of constraint status lines already visible in solver text output;
- viewport rendering of `satisfied`, `violated`, and `unknown` states in 3D,
  graph, and three-view modes;
- legend entries only when diagnostic states are present;
- no-Tk tests for projection and safe fallback behavior.

Out of scope:

- residual magnitudes;
- conflict/redundancy sets;
- local-to-global context overlays;
- C++ report schema changes;
- scene/history persistence changes;
- new rendering dependencies.

## Projection Contract

Diagnostic focus extends the Phase 6 focus shape:

```text
{
  "mode": "diagnostic",
  "rigid_set_ids": [],
  "geometry_ids": [],
  "constraint_ids": [],
  "constraint_states": {
    0: "satisfied",
    1: "violated",
    2: "unknown"
  }
}
```

Rules:

- `constraint_states` may appear together with selection focus.
- Unknown or missing constraints are ignored by projection helpers.
- Missing states for known constraints are filled as `unknown` only when the
  caller explicitly requests a full graph projection.
- Violated state must be visually stronger than satisfied state.
- Satisfied state must remain quiet and must not overpower focus.
- Focus still takes precedence for line width and label detail.

## Detailed Execution Plan

1. Add projection helpers.
   - Add `constraint_state_projection(...)`.
   - Normalize allowed states to `satisfied`, `violated`, or `unknown`.
   - Add `combine_focus_with_constraint_states(...)` for GUI use.

2. Parse only safe solver text evidence.
   - Extend `_parse_solve_report` to collect constraint IDs only from lines that
     contain a recognizable constraint ID plus `SATISFIED` or `VIOLATED`.
   - If output only has aggregate counts, keep per-constraint states unknown.

3. Feed diagnostics to the viewport.
   - Store diagnostic focus in `platform_gui.py`.
   - Redraw after solve with diagnostic focus.
   - Preserve selection focus by merging it with diagnostic states outside
     replay.

4. Render supplied states.
   - Add visualizer helpers for constraint state color, alpha, width, and label
     suffix.
   - Add diagnostic legend entries only when `constraint_states` exists.
   - Keep renderer free of parsing and solver semantics.

5. Validate.
   - Add no-Tk tests for projection and parser fallback.
   - Run focused tests, UI QA, syntax check, task-card validation, archive
     validation, and closure score.

## Acceptance Gates

- Violated constraints render visibly in all three view modes when supplied.
- Satisfied constraints stay quieter than focus and violation states.
- Unknown states are visually conservative and not presented as failure.
- Aggregate-only solve output does not invent per-constraint states.
- Focus and diagnostic states can coexist.
- Projection tests run without importing Tk.

## Verification Plan

```bat
$env:PYTHONPATH="$PWD\python"; python -m unittest tests.tools.test_gcs_viz_history_replay tests.tools.test_gcs_ui_qa
python tools\ui_qa\gcs_ui_qa.py
python -B -c "from pathlib import Path; files=[Path('python/gcs_viz/viewer_bridge.py'), Path('python/gcs_viz/platform_gui.py'), Path('python/gcs_viz/visualizer.py')]; [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print('syntax compile ok')"
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-ui-phase7-diagnostics-overlay.md
```

Manual GUI verification remains optional until the local interpreter has
`matplotlib` available.

## Completion Summary

Completed on 2026-05-25.

Implemented:

- `constraint_state_projection(...)` in `python/gcs_viz/viewer_bridge.py`;
- `constraint_states_from_solve_text(...)` in `python/gcs_viz/viewer_bridge.py`;
- `combine_focus_with_constraint_states(...)` in `python/gcs_viz/viewer_bridge.py`;
- diagnostic focus storage and merge behavior in `python/gcs_viz/platform_gui.py`;
- constraint-state styling in `python/gcs_viz/visualizer.py` for 3D, graph,
  and three-view modes;
- no-Tk tests for projection, safe fallback, and focus/state coexistence.

Validation:

```bat
$env:PYTHONPATH="$PWD\python"; python -m unittest tests.tools.test_gcs_viz_history_replay tests.tools.test_gcs_ui_qa
python tools\ui_qa\gcs_ui_qa.py
python -B -c "from pathlib import Path; files=[Path('python/gcs_viz/viewer_bridge.py'), Path('python/gcs_viz/platform_gui.py'), Path('python/gcs_viz/visualizer.py')]; [compile(p.read_text(encoding='utf-8'), str(p), 'exec') for p in files]; print('syntax compile ok')"
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-ui-phase7-diagnostics-overlay.md
```

Observed result:

- focused unittest suite passed 15/15;
- UI QA passed with existing advisory contrast warnings and skipped headless
  render because `matplotlib` is missing in the current interpreter;
- no-write syntax compile passed;
- task-card validation passed.

Skipped or degraded checks:

- `python -m compileall -q python\gcs_viz` could not write to the existing
  `__pycache__` directory in this environment.
- `platform_gui` import could not complete because the active Python
  interpreter does not have `matplotlib` installed.
- Manual desktop verification was not run for the same dependency reason.
