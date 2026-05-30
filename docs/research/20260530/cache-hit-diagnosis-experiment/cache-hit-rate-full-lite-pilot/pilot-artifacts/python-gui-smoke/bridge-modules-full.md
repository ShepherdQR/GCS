# Python GUI Smoke: Bridge Modules Full Lane

Run id: `python-gui-smoke-1-full`
Task pair: `python-gui-smoke-1`
Mode: Full
Date: 2026-05-31
Controller task card:
`docs/agentic/tasks/2026-05-31-cache-hit-pilot-eight-pairs.md`

## Scope

Smoke-check the Python GUI bridge/facade layer for import drift, syntax
validity, and responsibility boundaries. This run used the existing controller
task card and did not create a new task card.

Inspected context:

- `.codex/skills/gcs-python-gui-builder/SKILL.md`
- `.codex/skills/gcs-python-gui-builder/references/python-gui-map.md`
- `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/experiment-plan.md`
- `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/pilot-runbook-8-pairs.md`
- `python/gcs_viz/viewer_bridge.py`
- `python/gcs_viz/engine_bridge.py`
- `python/gcs_viz/platform_gui.py`
- `python/gcs_viz/visualizer.py`

## Command Evidence

| Command | Result | Evidence |
|---|---|---|
| `python -m compileall -q python\gcs_viz` | Pass | Exit code 0, no stdout/stderr. |
| `python -c "import sys; sys.path.insert(0, r'C:\Users\QR\.codex\worktrees\8e09\GCS_A\python'); from gcs_viz.viewer_bridge import project_history_frame, build_history_graph; history=[{'action':'AddRigidSet','payload':{'id':1}},{'action':'AddGeometry','payload':{'id':2,'type':1,'rigid_set_id':1,'v':[0.0,0.0,0.0]}}]; p=project_history_frame(history,1); g=build_history_graph(history,1); print('viewer_bridge smoke ok', p['action_label'], len(g.rigid_sets), len(g.geometries))"` | Pass | Printed `viewer_bridge smoke ok AddGeometry 1 1`. |
| `rg -n "viewer_bridge\|EngineBridge\|FigureCanvasTkAgg\|history\|build_.*figure\|build_.*on_figure\|replay\|messagebox" python\gcs_viz` | Pass | Located bridge/facade imports and replay/rendering call sites. |
| `rg -n "def (view_renderers\|graph_summary\|selection_focus\|history_focus_from_entry\|constraint_state_projection\|combine_focus_with_constraint_states\|constraint_states_from_solve_text\|render_graph_view\|render_message\|build_history_graph\|project_history_frame\|apply_history_entry\|parse_replay_evidence_report\|format_evidence_summary)" python\gcs_viz\viewer_bridge.py` | Pass | Confirmed facade surface in `viewer_bridge.py`. |
| `rg -n "def (is_available\|run_pipeline\|solve\|solve_with_evidence)" python\gcs_viz\engine_bridge.py` | Pass | Confirmed solver process bridge surface in `engine_bridge.py`. |

## Module Responsibility Summary

`python/gcs_viz/viewer_bridge.py` is the read-only facade layer for GUI-facing
projection work. It dispatches view rendering, summarizes graphs, builds
selection and diagnostic focus overlays, reconstructs history frames, applies
history entries into replay graphs, and parses/formats replay evidence reports.
The facade imports renderer functions lazily through `view_renderers()`, which
keeps importing the bridge from pulling in matplotlib rendering until needed.

`python/gcs_viz/engine_bridge.py` owns C++ solver process discovery and
invocation. It resolves `GCS_EXE` or the default
`out/build/clang-ninja/GCS.exe`, runs the solver with a timeout, and optionally
captures replay evidence through `--save-replay-evidence`. The GUI receives
structured result dictionaries rather than constructing solver commands inline.

`python/gcs_viz/platform_gui.py` consumes both bridge surfaces. It constructs
`EngineBridge`, imports `viewer_bridge` helpers, uses `graph_summary()` for the
summary rail, `selection_focus()` and `combine_focus_with_constraint_states()`
for focused rendering, `render_graph_view()` for canvas redraws, and
`project_history_frame()` plus `build_history_graph()` for history replay. Solve
completion parses solver text into constraint states through the bridge facade
before refreshing the canvas.

`python/gcs_viz/visualizer.py` provides the rendering functions consumed by the
facade: `build_3d_on_figure()`, `build_graph_on_figure()`, and
`build_three_view_on_figure()`. These functions draw onto a supplied matplotlib
figure and accept focus overlays, matching the GUI-builder responsibility rule
that rendering code should not own Tk widgets, solver process invocation, or
model mutation.

## Pass/Fail

Pass.

The Python GUI package compiles, and the bridge/facade replay path imports and
projects a minimal history without requiring a GUI window. The inspected module
boundaries match the GUI stewardship map: GUI orchestration in
`platform_gui.py`, process invocation in `engine_bridge.py`, read-only view and
replay projection in `viewer_bridge.py`, and figure drawing in `visualizer.py`.

## Issues

- No blocking issue found in the bridge/facade smoke path.
- Nonblocking observation: `platform_gui.py` appears to contain a mojibake-like
  GUI title separator when read as UTF-8. This does not affect compile or
  bridge behavior, but a future GUI polish pass should verify the intended
  title glyph in a live Tk window.

## Residual Risk

- This smoke did not launch `scripts\start_gui.cmd` or open a Tk window, so it
  does not prove desktop display availability, TkAgg backend behavior, or live
  user interaction.
- This smoke did not run `GCS.exe`, so solver availability and replay evidence
  generation remain covered only by `EngineBridge.is_available()` semantics and
  code inspection.
- The import/projection check exercises a narrow AddRigidSet/AddGeometry
  history path; constraint update/removal replay and diagnostic focus overlays
  were inspected but not executed.

## Pilot Metrics Suggestion

- Suggested `audit_score_0_5`: 5
- `validation_passed`: true
- `rework_turns`: 0
- `defect_or_reopen_count`: 0
- Changed files: `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/pilot-artifacts/python-gui-smoke/bridge-modules-full.md`
