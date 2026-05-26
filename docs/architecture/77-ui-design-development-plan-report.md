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
- `docs/architecture/92-gcs-ui-architecture-adjustment-record.md`
- `tools/ui_qa/gcs_ui_qa.py`

## 2026-05-25 Solver Workbench Adjustment

The UI architecture is now interpreted as a **GCS Solver Evidence Workbench**.
The visual thesis remains **GCS Quiet Technical Atelier**, but the product
architecture now requires workbench surfaces for constraint inspection,
diagnostic evidence, replay provenance, and safe repair drafts.

This adjustment is recorded in
`docs/architecture/92-gcs-ui-architecture-adjustment-record.md` and is backed
by
`docs/research/20260525/gcs-ui-requirements/01-advanced-ui-and-gcs-solver-requirements.md`.

Practical consequence: future UI phases must identify which workbench zone they
affect and must preserve the projection boundary. `viewer_bridge` and
`session_runtime` expose structured evidence; `platform_gui.py` orchestrates
Tk state and user actions; `visualizer.py` draws supplied states only.

## Current Phase Ledger

| Phase | Name | Status | Current Evidence |
| --- | --- | --- | --- |
| 1 | Theme Foundation | Complete | `python/gcs_viz/color_scheme.py`, themed Tk/Matplotlib surfaces |
| 2 | Viewport Semantics | Complete | Focus dictionary, geometry markers, constraint line styles |
| 3 | Inspector Layout | Complete | Model summary, object browser notebook, command zone |
| 4 | Replay And Solve Polish | Complete | Replay rail, progress, action text, solve summary |
| 5 | Design QA And Accessibility | Complete | `tools/ui_qa/gcs_ui_qa.py`, UI QA fixture and unittest |
| 6 | Interaction Semantics | Complete | `selection_focus`, replay focus projection, table-selection highlighting |
| 7 | Solve Diagnostics Overlay | Complete | `constraint_states`, safe fallback, renderer overlays |
| 8 | Accessibility And Contrast Refinement | Complete | `STATE_TEXT_COLORS`, dynamic graph-node label contrast, UI QA contrast checks |
| 9 | Replay Rail Refinement | Complete | `project_history_frame`, viewport speed control, deletion hints |
| 10 | Manual Visual QA Pass | Planned | Local GUI screenshot and taste calibration cycle |
| 11 | Constraint Manager And Repair Drafts | Backlog | Constraint row projection, diagnostic filters, safe repair candidates |
| 12 | Local-To-Global Evidence Inspector | Backlog | Context covers, boundary projections, gluing, obstruction paths |

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

Status: complete.

Goal:

Make selection a first-class UI state. Table selection and future viewport
selection should share the same focus projection used by replay.

Detailed implementation plan:

- `docs/architecture/93-ui-phase6-focus-projection-work-plan.md`

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

Completion evidence:

- `python/gcs_viz/viewer_bridge.py` now owns pure `selection_focus(...)` and
  `history_focus_from_entry(...)` projection helpers.
- `python/gcs_viz/platform_gui.py` binds rigid-set, geometry, and constraint
  table selection to canvas focus and keeps replay focus authoritative while
  replay is active.
- `tests/tools/test_gcs_viz_history_replay.py` covers selection and replay
  focus projection without importing Tk.
- `docs/architecture/93-ui-phase6-focus-projection-work-plan.md` records the
  detailed plan, completion evidence, and environment-limited checks.

## Phase 7: Solve Diagnostics Overlay

Status: complete.

Goal:

Make solve results visible in the viewport, not just in a summary rail.

Detailed implementation plan:

- `docs/architecture/94-ui-phase7-diagnostics-overlay-work-plan.md`

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

Completion evidence:

- `python/gcs_viz/viewer_bridge.py` now owns conservative constraint-state
  projection, solver-text extraction, and focus/state merge helpers.
- `python/gcs_viz/platform_gui.py` stores diagnostic constraint states from
  solve output and merges them with selection focus outside replay.
- `python/gcs_viz/visualizer.py` renders supplied `satisfied`, `violated`, and
  `unknown` states in 3D, graph, and three-view modes with diagnostic legend
  entries only when states are present.
- `tests/tools/test_gcs_viz_history_replay.py` covers safe fallback behavior:
  aggregate-only output does not invent per-constraint satisfied/violated
  states.
- `docs/architecture/94-ui-phase7-diagnostics-overlay-work-plan.md` records
  the detailed plan, evidence, and environment-limited checks.

## Phase 8: Accessibility And Contrast Refinement

Status: complete.

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

Completion evidence:

- `python/gcs_viz/color_scheme.py` now splits graphic state accents from
  contrast-safe `STATE_TEXT_COLORS`.
- `python/gcs_viz/platform_gui.py` uses `STATE_TEXT_COLORS` for log, DOF,
  solve-summary, and replay-state text.
- `python/gcs_viz/visualizer.py` chooses graph-node label text dynamically by
  contrast against each rigid-set fill.
- `tools/ui_qa/gcs_ui_qa.py` checks state text contrast and graph-node label
  contrast.
- `docs/architecture/70-visualization/viewer-accessibility-contrast-refinement.md`
  records the status-text versus graphic-accent token rule.

## Phase 9: Replay Rail Refinement

Status: complete.

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

Completion evidence:

- `python/gcs_viz/viewer_bridge.py` now exposes
  `project_history_frame(history, index)`.
- `python/gcs_viz/platform_gui.py` consumes the frame projection for rail
  action text, progress, title, focus, and deletion hints.
- The replay speed control is mirrored into the viewport rail while sharing
  the existing speed variable.
- `tests/tools/test_gcs_viz_history_replay.py` covers frame projection and
  deletion hints without importing Tk.
- `docs/architecture/70-visualization/viewer-history-frame-projection.md`
  records the projection contract.

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

## Phase 11: Constraint Manager And Repair Drafts

Status: backlog.

Goal:

Turn constraints into a navigable solver workbench surface rather than a simple
object table.

Deliverables:

- constraint-manager rows with stable constraint IDs, type, attached entities,
  value, residual state, conflict/redundancy tags, and selection link;
- filters for type, state, rigid set/entity involvement, and diagnostic
  responsibility set;
- repair candidates presented as command drafts, not direct graph mutation;
- report export or snapshot evidence for the active diagnostic selection;
- focused tests for projection/filter behavior without importing Tk.

Suggested files:

- `python/gcs_viz/viewer_bridge.py`
- `python/gcs_viz/platform_gui.py`
- future C++ or CLI viewer projection export if structured reports are needed
- `tools/ui_qa/gcs_ui_qa.py`

Boundary:

- do not compute residuals, redundancies, or conflicts in GUI table code;
- do not let repair drafts bypass `session_runtime` command validation;
- do not persist UI filters or selected rows in scene files.

Acceptance:

- users can find a violated or redundant constraint and highlight affected
  geometry;
- candidate repair actions explain their evidence source;
- repair drafts remain non-mutating until explicitly accepted through runtime
  command flow.

## Phase 12: Local-To-Global Evidence Inspector

Status: backlog.

Goal:

Expose the solver's context-cover, boundary-projection, gluing, and obstruction
evidence once planner and diagnostics contracts are ready enough for UI
projection.

Deliverables:

- read-only context cover summary;
- overlap and boundary-projection table;
- gluing status and boundary residual view;
- obstruction path view linking contexts, projections, entities, and
  constraints;
- compact canvas hints for active context or failed overlap.

Suggested files:

- `src/gcs/viewer_bridge`
- `python/gcs_viz/viewer_bridge.py`
- `python/gcs_viz/platform_gui.py`
- `python/gcs_viz/visualizer.py` only for supplied context/overlap states

Boundary:

- consume planner/diagnostic reports only;
- do not expose speculative planner internals before contracts stabilize;
- do not turn the UI into a decomposition-planner policy layer.

Acceptance:

- a user can tell which local context solved, which overlap failed, and which
  evidence supports that conclusion;
- mathematician-facing rank/residual/gluing evidence remains traceable to
  reports;
- renderer support is driven by explicit projection state.

## Scheduling Recommendation

The next standalone work item should be Phase 10 or Phase 11, depending on
whether manual visual QA or constraint-manager projection is more urgent.

Reasoning:

- Phase 6 turned the existing focus contract into a reusable interaction
  primitive.
- Phase 7 built diagnostics overlays on top of the same projection path.
- Phase 8 refined contrast and text/state strategy around the active focus and
  diagnostic states.
- Phase 9 refined replay through a pure history-frame projection.
- Phase 10 should run a real desktop visual QA pass once the local Python
  environment has display and matplotlib support.
- Phase 11 should follow once diagnostic projections are stable enough to make
  constraint filtering meaningful.
- Phase 12 should wait until planner and diagnostics reports expose enough
  context-cover and gluing evidence to avoid UI-side inference.

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
