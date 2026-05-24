# UI Design Development Plan Report

Snapshot date: 2026-05-24.

This report consolidates the GCS UI aesthetic line into one execution-oriented
plan. It records completed phases, the next design-hardening phases, and the
rules for scheduling later implementation work.

The governing taste remains:

> GCS should feel like a quiet technical atelier: warm, precise, mathematical,
> evidence-rich, and calm under repeated use.

This is a viewer and design-system plan. It does not move durable solver truth
into the UI. The Python viewer may project snapshots, histories, summaries, and
diagnostic states, but kernel, session-runtime, solver, and IO contracts remain
outside the GUI.

## Source Documents

- `docs/architecture/72-ui-aesthetic-roadmap.md`
- `docs/architecture/72-ui-aesthetic-phase-1-theme-foundation.md`
- `docs/architecture/72-ui-aesthetic-phase-2-viewport-semantics.md`
- `docs/architecture/72-ui-aesthetic-phase-3-inspector-layout.md`
- `docs/architecture/72-ui-aesthetic-phase-4-replay-solve-polish.md`
- `docs/architecture/72-ui-aesthetic-phase-5-design-qa-accessibility.md`
- `docs/architecture/73-gcs-visual-taste-guide.md`
- `docs/architecture/75-ui-design-system-conventions.md`
- `docs/architecture/76-ui-design-system-execution-plan.md`
- `tools/ui_qa/gcs_ui_qa.py`

## Current Phase Ledger

| Phase | Name | Status | Current Evidence |
| --- | --- | --- | --- |
| 1 | Theme Foundation | Complete | `python/gcs_viz/color_scheme.py`, themed Tk/Matplotlib surfaces |
| 2 | Viewport Semantics | Complete | Focus dictionary, geometry markers, constraint line styles |
| 3 | Inspector Layout | Complete | Model summary, object browser notebook, command zone |
| 4 | Replay And Solve Polish | Complete | Replay rail, progress, action text, solve summary |
| 5 | Design QA And Accessibility | Complete | `tools/ui_qa/gcs_ui_qa.py`, UI QA fixture and unittest |
| 6 | Interaction Semantics | Planned | Selection/focus projection hardening |
| 7 | Solve Diagnostics Overlay | Planned | Constraint state projection and renderer overlays |
| 8 | Accessibility And Contrast Refinement | Planned | Status text colors, node label strategy, stale UI cleanup |
| 9 | Replay Rail Refinement | Planned | History frame projection, rail controls, deletion hints |
| 10 | Manual Visual QA Pass | Planned | Local GUI screenshot and taste calibration cycle |

## Execution Protocol

Each remaining phase should follow this loop:

1. Re-open this report and the relevant phase design document.
2. Persist any phase-specific design adjustment before implementation.
3. Implement only the smallest coherent phase scope.
4. Run the phase checks plus `tools/ui_qa/gcs_ui_qa.py`.
5. Commit on a `codex-ui-*` branch.
6. Push the branch.
7. Fast-forward merge into `master` when validated.
8. Push `master`.
9. Update this report if the next phase changes.

Do not mix UI-design work with scene-generation, agentic, or solver-runtime
changes unless the phase explicitly requires a cross-boundary contract.

## Phase 1: Theme Foundation

Status: complete.

Purpose:

- replace default Tkinter/Matplotlib visual chrome with a shared warm technical
  theme;
- define initial semantic color tokens;
- make the viewer feel deliberate without changing workflows.

Key files:

- `python/gcs_viz/color_scheme.py`
- `python/gcs_viz/platform_gui.py`
- `python/gcs_viz/visualizer.py`
- `docs/architecture/72-ui-aesthetic-phase-1-theme-foundation.md`

Boundary:

- no layout rewrite;
- no solver or scene schema changes;
- no new dependencies.

Completion evidence:

- shared `GCS_THEME`;
- muted rigid-set and constraint palettes;
- themed Tk surfaces, table surfaces, status/log surfaces, Matplotlib canvas,
  axes, legends, and summary text.

## Phase 2: Viewport Semantics

Status: complete.

Purpose:

- make the viewport read as a geometric workspace;
- encode geometry type by form and constraint type by line style;
- introduce renderer focus states for replay and future selection.

Key files:

- `python/gcs_viz/visualizer.py`
- `python/gcs_viz/viewer_bridge.py`
- `python/gcs_viz/platform_gui.py`
- `docs/architecture/72-ui-aesthetic-phase-2-viewport-semantics.md`

Boundary:

- renderer accepts projection and focus only;
- renderer does not know Tk, files, solver process, or model mutation;
- focus is transient view state.

Completion evidence:

- `focus` dictionary supports `geometry_ids`, `constraint_ids`, and
  `rigid_set_ids`;
- 3D, graph, and three-view renderers share semantic state;
- replay current frame can highlight the relevant object.

## Phase 3: Inspector Layout

Status: complete.

Purpose:

- reshape the left column from stacked debug controls into a model inspector;
- make loaded model name and model state visible without scrolling;
- separate object editing from primary commands.

Key files:

- `python/gcs_viz/platform_gui.py`
- `docs/architecture/72-ui-aesthetic-phase-3-inspector-layout.md`

Boundary:

- keep existing dialogs and handlers;
- keep graph mutation in GUI command handlers;
- do not rewrite renderer or scene IO.

Completion evidence:

- model summary section;
- object browser notebook for rigid sets, geometries, and constraints;
- command zone for Solve, Replay History, Save, and Load.

## Phase 4: Replay And Solve Polish

Status: complete.

Purpose:

- make temporal workflows visible near the viewport;
- avoid making users read the bottom log to understand replay or solve state;
- keep solve output as a UI projection rather than durable solver truth.

Key files:

- `python/gcs_viz/platform_gui.py`
- `docs/architecture/72-ui-aesthetic-phase-4-replay-solve-polish.md`

Boundary:

- replay remains an in-window reconstruction, not a modal window;
- `Solve` replay entries stay markers and do not re-run the solver;
- C++ process invocation remains owned by `engine_bridge.py`.

Completion evidence:

- replay rail with state, step, action, progress, and stop control;
- solve summary string with running, success, warning, error, or unknown state;
- `_parse_solve_report` provides a UI-level projection of current text output.

## Phase 5: Design QA And Accessibility

Status: complete.

Purpose:

- convert taste rules into lightweight checks;
- make future UI changes reviewable without requiring a display server;
- create a richer UI QA fixture.

Key files:

- `docs/architecture/72-ui-aesthetic-phase-5-design-qa-accessibility.md`
- `tools/ui_qa/gcs_ui_qa.py`
- `tests/tools/test_gcs_ui_qa.py`
- `fixtures/scene/ui_qa/mixed_geometry_constraints.json`
- `python/gcs_viz/color_scheme.py`
- `python/gcs_viz/platform_gui.py`

Boundary:

- do not import Tk GUI in headless CI checks;
- optional Matplotlib render smoke may skip when dependency is missing;
- warnings may report semantic colors unsuitable for small text without failing
  the gate.

Completion evidence:

- UI QA checks parse architecture docs, theme tokens, active GUI command labels,
  and UI QA fixture contracts;
- `text_secondary` contrast was refined;
- active command labels in the current GUI path are ASCII text;
- UI QA fixture covers point, line, plane, and all five constraint types.

## Phase 6: Interaction Semantics

Status: planned.

Goal:

Make selection a first-class UI state. Table selection and future viewport
selection should share the same focus projection used by replay.

Deliverables:

- move replay focus mapping from `platform_gui.py` into a pure
  `viewer_bridge.py` projection function;
- add table-selection handlers for rigid sets, geometries, and constraints;
- pass selection focus into `render_graph_view`;
- define precedence when replay and selection both exist;
- document the focus projection contract for future hit testing.

Suggested files:

- `python/gcs_viz/viewer_bridge.py`
- `python/gcs_viz/platform_gui.py`
- `tests` or `tools/ui_qa` coverage for pure focus projection
- a new phase note if the implementation changes the plan

Boundary:

- do not add canvas hit testing yet;
- do not persist selected IDs in scene files;
- do not mutate solver truth from renderer events.

Acceptance:

- selecting a table row visibly highlights the corresponding viewport object;
- replay focus still works;
- focus projection can be tested without importing Tk.

## Phase 7: Solve Diagnostics Overlay

Status: planned.

Goal:

Make solve results visible in the viewport, not just in a summary rail.

Deliverables:

- extend focus/projection with `constraint_states`;
- render `satisfied`, `violated`, and `unknown` constraint states in 3D, graph,
  and three-view modes;
- add legend entries only when diagnostic states are present;
- keep solve-report parsing in GUI or viewer-bridge projection, not renderer
  truth;
- update UI QA to validate diagnostic-state projection.

Suggested files:

- `python/gcs_viz/visualizer.py`
- `python/gcs_viz/viewer_bridge.py`
- `python/gcs_viz/platform_gui.py`
- `tools/ui_qa/gcs_ui_qa.py`

Boundary:

- current parser may remain text-based until C++ emits structured reports;
- a text parser must degrade to `unknown` rather than inventing diagnostics;
- renderer only draws supplied states.

Acceptance:

- violated constraints are visible in all view modes;
- satisfied states remain quiet and do not overpower focus;
- solve summary and viewport states agree.

## Phase 8: Accessibility And Contrast Refinement

Status: planned.

Goal:

Reduce remaining accessibility warnings and make the design system more robust
under dense, repeated use.

Deliverables:

- separate small-text semantic colors from graphic accent colors;
- choose graph node label text dynamically for contrast;
- remove or retire the unused legacy `_build_left_panel` path after confirming
  no callers remain;
- tighten UI QA warnings into failures where the design system is ready;
- document status text versus graphic state token rules.

Suggested files:

- `python/gcs_viz/color_scheme.py`
- `python/gcs_viz/visualizer.py`
- `python/gcs_viz/platform_gui.py`
- `tools/ui_qa/gcs_ui_qa.py`
- `docs/architecture/75-ui-design-system-conventions.md`

Boundary:

- no palette reset;
- preserve the warm technical atelier thesis;
- do not create a one-hue theme or decorative gradients.

Acceptance:

- no low-contrast small text in active GUI paths;
- graph labels remain readable on all current rigid-set colors;
- UI QA report distinguishes hard failures from advisory warnings.

## Phase 9: Replay Rail Refinement

Status: planned.

Goal:

Turn the first replay rail into a more product-grade temporal control surface.

Deliverables:

- move or mirror replay speed control into the viewport rail;
- add a pure `project_history_frame(history, index)` function;
- keep replay title, focus, step, total, action, and progress in one projection;
- define deletion ghost hints for removed geometry and constraints;
- make stop, complete, and error states visually distinct without relying on
  symbols.

Suggested files:

- `python/gcs_viz/viewer_bridge.py`
- `python/gcs_viz/platform_gui.py`
- `python/gcs_viz/visualizer.py` only if ghost hints require renderer support
- `tools/ui_qa/gcs_ui_qa.py`

Boundary:

- no separate replay window;
- no solver re-run during replay;
- no animation framework dependency.

Acceptance:

- replay is understandable without log text;
- speed changes affect subsequent steps;
- delete actions show what changed rather than disappearing silently.

## Phase 10: Manual Visual QA Pass

Status: planned.

Goal:

Run the UI against real desktop states and calibrate taste beyond static checks.

Deliverables:

- manual run of `scripts/start_gui.cmd`;
- checklist results for empty model, `triangle_003.json`,
  `mixed_geometry_constraints.json`, active replay, solve success, solve
  warning/error when available, and narrow desktop width;
- screenshots or written visual notes if screenshots are not practical;
- final polish ticket list for any overlap, density, contrast, or hierarchy
  issues found.

Suggested files:

- `docs/architecture/72-ui-aesthetic-roadmap.md`
- `docs/architecture/77-ui-design-development-plan-report.md`
- optional review notes under `docs/research/20260524/`
- optional completed-task archive if the pass results in implementation work

Boundary:

- no raw screenshot baseline unless explicitly approved;
- do not block on a full C++ solve if the local engine is unavailable;
- record skipped checks clearly.

Acceptance:

- the GUI has been inspected in a real desktop session;
- visual notes separate defects from future preferences;
- this report is updated with the next UI phase recommendation.

## Scheduling Recommendation

The next standalone work item should be Phase 6, followed by Phase 7.

Reasoning:

- Phase 6 turns the existing focus contract into a reusable interaction
  primitive.
- Phase 7 then builds diagnostics overlays on top of the same projection path.
- Phase 8 should follow once the active interaction paths reveal where contrast
  and text strategy actually matter most.
- Phase 9 should refine replay after selection and diagnostic state precedence
  are clear.
- Phase 10 should be run after Phase 8 or Phase 9, unless a manual GUI review
  is needed sooner to unblock confidence.

## Known Risks

- `platform_gui.py` still contains legacy code paths that are no longer active;
  Phase 8 should retire them after static checks prove the new inspector path
  is authoritative.
- Solve diagnostics currently rely on text parsing; structured solver reports
  should eventually replace this projection.
- The current local shell may lack `matplotlib`; `tools/ui_qa/gcs_ui_qa.py`
  skips render smoke in that case. A fuller visual QA pass needs the GUI
  runtime environment.
- Some semantic accent colors remain suitable for graphics but not small text;
  keep color plus text/state wording together until Phase 8 resolves token
  separation.

## Branch And Commit Discipline

Preferred branch names:

- `codex-ui-phase6-interaction-semantics`
- `codex-ui-phase7-diagnostics-overlay`
- `codex-ui-phase8-accessibility-contrast`
- `codex-ui-phase9-replay-rail`
- `codex-ui-phase10-manual-visual-qa`

Each branch should merge back to `master` only after the relevant checks pass
and unrelated worktree changes remain unstaged.
