# GCS UI Architecture Adjustment Record

Date: 2026-05-25

Status: accepted as planning guidance; implementation remains future work.

Research source:

- `docs/research/20260525/gcs-ui-requirements/01-advanced-ui-and-gcs-solver-requirements.md`

Governing conventions:

- **GCS Quiet Technical Atelier** remains the visual taste thesis.
- **GCS Warm Evidence Tokens** remain the token vocabulary.
- **GCS Evidence-First Interface Grammar** becomes the primary product
  architecture driver for the next UI phases.
- **GCS Visual Integrity Gate** remains the default QA boundary for visual
  artifacts.

## Decision

The GCS UI architecture is adjusted from "styled local viewer with solver
summary" to **GCS Solver Evidence Workbench**.

The target UI is now:

> A local desktop solver workbench that lets users construct geometry, inspect
> constraints, run solves, see structured rank/residual/diagnostic evidence,
> replay provenance, and draft repair commands without letting the UI own solver
> truth.

This is an architecture adjustment, not a GUI rewrite. The approved stack
remains Tkinter plus embedded Matplotlib. The boundary rule remains that
`python/gcs_viz` observes snapshots, histories, reports, and projections while
solver truth stays in the kernel, diagnostics, numeric engine, and
`session_runtime`.

## Motivation

The previous UI plan correctly established taste, tokens, visual QA, and a
clean viewer boundary. The external UI/GCS research added a stronger product
requirement: advanced GCS users need an inspectable solver workbench, not only
an improved canvas.

Three viewpoints drive the adjustment:

| Viewpoint | Need | UI implication |
| --- | --- | --- |
| Top mathematician | Trust depends on rank, nullity, residual, gauge, gluing, and obstruction evidence | Make solve results certificate-like and inspectable |
| CS expert | Trust depends on typed contracts, provenance, replay, and testability | Consume `viewer_bridge`/runtime projections, not free-form text |
| GCS user | Productivity depends on construction, diagnosis, repair, and export | Add constraint manager, diagnostic overlay, replay timeline, and repair drafts |

## Architecture Changes

### 1. Product Zones

The workbench target has six zones. These zones guide future layout decisions
without forcing a one-shot implementation.

| Zone | Owner boundary | Durable truth source | UI responsibility |
| --- | --- | --- | --- |
| Model Canvas | `visualizer.py` | Supplied graph/projection state | Draw geometry, constraints, focus, and diagnostic overlays |
| Model/Constraint Inspector | `platform_gui.py` plus Python viewer helpers | Current editable graph and future viewer projections | List, filter, select, edit, and link objects to the canvas |
| Solver Evidence Rail | `platform_gui.py` | `session_runtime::CommandResult`, reports, or safe fallback | Show status precedence, commit/rollback, rank/residual summary |
| Diagnostics Workbench | `viewer_bridge` projection consumed by GUI | `diagnostics` and runtime reports | Inspect DOF, rank, residuals, conflicts, redundancies, obstructions |
| Replay/Provenance Timeline | Python/C++ viewer bridge projection | `session_runtime` history and replay evidence | Show frame state, stages, report codes, deletion hints, export artifacts |
| Repair Draft Panel | `viewer_bridge` draft plus `session_runtime` command route | diagnostics responsibility sets and command validation | Present candidate repairs as drafts, never direct solver mutation |

### 2. Projection Boundary

`viewer_bridge` is the durable read-only evidence boundary for advanced UI
state. The GUI may temporarily parse text output only when structured reports
are unavailable. Such parsing must degrade to `unknown`; it must not invent
rank, residual, or diagnostic truth.

Required projection families:

- scene/entity/constraint projection;
- selection/focus projection;
- diagnostic overlay projection;
- snapshot summary projection;
- history-frame and replay-evidence projection;
- interaction command draft projection;
- future constraint-manager row projection.

### 3. Workbench Capability Matrix

Future UI implementation should be accepted only when it answers the following
questions:

| Capability | Mathematician test | CS test | User test |
| --- | --- | --- | --- |
| Selection/focus | Can I identify the entity or constraint under discussion? | Is focus a pure projection? | Does table selection highlight the viewport object? |
| Diagnostic overlay | Can I inspect residual/rank evidence per constraint/context? | Is state structured and testable? | Can I see violated, satisfied, and unknown constraints? |
| Constraint manager | Can I find redundant/conflicting constraints? | Are filters based on stable IDs and reports? | Can I sort/filter constraints and jump to affected geometry? |
| Replay/provenance | Can I tell which evidence produced the current state? | Is the timeline deterministic? | Can I replay and understand a deletion, solve, or rollback? |
| Repair draft | Can I see why the candidate follows from evidence? | Does it route through command validation? | Can I preview a safe next step after failure? |
| Local-to-global inspector | Can I inspect covers, overlaps, and obstructions? | Does it consume planner/diagnostic reports? | Can I tell where global assembly failed? |

## Adjusted Phase Guidance

`docs/architecture/77-ui-design-development-plan-report.md` remains the active
execution plan, but its planned phases now carry workbench intent:

- Phase 6, Interaction Semantics, is the first workbench primitive: stable
  selection/focus projection.
- Phase 7, Solve Diagnostics Overlay, is the first solver-evidence overlay:
  constraint states and residual/diagnostic visibility.
- Phase 8, Accessibility And Contrast Refinement, becomes semantic redundancy:
  every state must be visible through text, shape, focus, and machine-readable
  projection, not color alone.
- Phase 9, Replay Rail Refinement, becomes provenance hardening: history frames,
  report codes, deletion hints, and exportable replay evidence.
- Phase 10, Manual Visual QA Pass, must include workbench states, not only
  visual taste states.

Two follow-on phases are added to the architecture backlog:

| Phase | Name | Purpose |
| --- | --- | --- |
| 11 | Constraint Manager And Repair Drafts | Turn constraint rows, residuals, conflict/redundancy evidence, and safe candidate actions into a navigable workbench surface. |
| 12 | Local-To-Global Evidence Inspector | Expose context covers, boundary projections, gluing reports, and obstruction paths once planner/diagnostic contracts are ready. |

## Boundary Rules

- Do not move residual, rank, gauge, conflict, redundancy, or obstruction
  computation into Tk widgets or Matplotlib renderers.
- Do not persist selected IDs, diagnostic UI state, or temporary repair drafts
  in scene files unless an IO contract explicitly adopts them.
- Do not let the renderer infer solver status from color, labels, or text.
  Renderer input must contain explicit state.
- Do not add browser, HTTP server, web assets, or external viewer dependencies
  for this architecture adjustment.
- Do not make repair candidates mutate the graph directly. They must become
  command drafts that pass through runtime validation and normal history.

## Required Documentation Updates

- `docs/architecture/README.md` should list this record in the visualization
  and aesthetic system section.
- `docs/architecture/77-ui-design-development-plan-report.md` should include
  the solver-workbench adjustment and Phase 11/12 backlog.
- Future phase design documents should name which workbench zone they affect.

## Deferred Work

- No Python implementation is made in this task.
- No C++ contract changes are made in this task.
- No Figma, browser, or external UI runtime dependency is introduced.
- Structured CLI or binding delivery of C++ viewer projections to Python
  remains a future implementation decision.

## Acceptance Criteria For The Next Implementation Increment

The next UI implementation increment should satisfy:

- pure selection/focus projection can be tested without importing Tk;
- table selection highlights the corresponding viewport object;
- replay focus still works;
- no solver truth moves into `platform_gui.py` or `visualizer.py`;
- `tools/ui_qa/gcs_ui_qa.py` or focused tests cover the new projection path.
