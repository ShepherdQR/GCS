# Advanced UI Design And GCS Solver Requirements

Date: 2026-05-25

Scope: Internet-backed UI research plus project-local architecture review for
the GCS solver viewer. This report focuses on solver-facing UI requirements,
not on a visual refresh or an implementation patch.

## Executive Summary

The current GCS UI direction has good foundations: a named design system,
semantic tokens, visual QA, a local Tk/Matplotlib stack, and a C++ viewer bridge
that already models diagnostic overlays and replay evidence. The missing leap
is product architecture. The UI should now be treated as a **GCS Solver Evidence
Workbench**, not just as a sketch canvas with nicer styling.

Current advanced UI practice points in the same direction: mature systems use
semantic tokens, dense but navigable layouts, accessible state representation,
direct manipulation with explicit inspectors, and transparent AI/algorithmic
evidence. For GCS this means every solve must expose what changed, what
remains free, what failed, what evidence supports the status, and how the user
can recover.

From a top mathematician's perspective, the UI must show local-to-global
structure: context covers, boundary projections, rank/nullity, gauge and free
variables, residuals, obstruction evidence, and whether a visual conclusion is
a theorem-like certificate or merely a numeric attempt.

From a computer scientist's perspective, the UI must consume typed projections
from `viewer_bridge` and `session_runtime`, preserve provenance, keep renderer
logic pure, support deterministic replay, and make advanced states testable
without a desktop session.

From a GCS user's perspective, the UI must help construct, inspect, diagnose,
repair, replay, and export scenes. A constraint manager, linked selection,
diagnostic overlays, solve evidence rail, repair candidates, and replay
timeline are core workbench features, not luxury polish.

## Source Register

| Source | Date/version | Used for | Confidence |
| --- | ---: | --- | --- |
| [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines) | Accessed 2026-05-25 | Legibility, interaction clarity, platform-grade restraint | High |
| [Google Material Design](https://m3.material.io/) | Accessed 2026-05-25 | Tokenized adaptive design-system framing | High |
| [Microsoft Fluent 2](https://fluent2.microsoft.design/) and [Fluent 2 design tokens](https://fluent2.microsoft.design/design-tokens) | Accessed 2026-05-25 | Semantic tokens, scalable component vocabulary | High |
| [IBM Carbon Design System](https://carbondesignsystem.com/) and [Carbon color](https://carbondesignsystem.com/elements/color/overview/) | Accessed 2026-05-25 | Enterprise-grade density, color discipline, accessibility | High |
| [IBM Carbon Charts data visualization](https://charts.carbondesignsystem.com/) | Accessed 2026-05-25 | Structured chart/dashboard grammar for dense evidence | Medium |
| [IBM Design for AI](https://www.ibm.com/design/ai/) | Accessed 2026-05-25 | Transparency, explainability, user control in algorithmic UI | High |
| [Nielsen Norman Group: 10 usability heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/) | Accessed 2026-05-25 | Visibility of system status, error recovery, recognition over recall | High |
| [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/) | Accessed 2026-05-25 | Accessibility baseline for contrast, focus, names, and alternatives | High |
| [Siemens D-Cubed 2D DCM](https://plm.sw.siemens.com/en-US/plm-components/d-cubed/2d-dcm/) and [3D DCM](https://plm.sw.siemens.com/en-US/plm-components/d-cubed/3d-dcm/) | Accessed 2026-05-25 | Commercial GCS capability framing: constraint solve, variation, motion, diagnostics | High |
| [Onshape Sketch Tools](https://cad.onshape.com/help/Content/sketch-tools.htm) | Accessed 2026-05-25 | CAD sketcher UX: constraints, fully defined state, direct editing | High |
| [Shapr3D Constraints](https://support.shapr3d.com/hc/en-us/articles/7394385784476-Constraint-Settings) | Accessed 2026-05-25 | User-facing constraint visibility and automatic/manual constraint control | Medium |
| [FreeCAD Sketcher Workbench](https://wiki.freecad.org/Sketcher_Workbench) | Accessed 2026-05-25 | Open CAD sketcher concepts: constraints, degrees of freedom, solver messages | Medium |
| `docs/architecture/75-ui-design-system-conventions.md` | 2026-05-24 | Existing GCS UI design-system contract | High |
| `docs/architecture/77-ui-design-development-plan-report.md` | 2026-05-24 | Current phase ledger and planned UI work | High |
| `docs/architecture/10-system/system-topology.md` | Current repo | Solver/viewer dependency direction | High |
| `docs/architecture/30-contracts/solver-contracts.md` | Current repo | Structured rank, residual, diagnostic, and viewer-facing evidence contracts | High |
| `src/gcs/viewer_bridge/viewer_bridge.cppm` | Current repo | Existing typed projection surface for scene, overlay, replay, and summary | High |
| `python/gcs_viz/platform_gui.py` | Current repo | Current local GUI surface and text-parser solve summary | High |
| `python/gcs_viz/viewer_bridge.py` | Current repo | Python read-only rendering/replay facade | High |

## Findings

### 1. Advanced UI Is Evidence Architecture, Not Decoration

The strongest contemporary UI systems share a few traits that matter directly
to GCS:

- visual language is tokenized and governed, not scattered through component
  code;
- dense operational screens prioritize scannability over hero-page spectacle;
- system status is visible at the point of work;
- error prevention and recovery are explicit workflows;
- accessibility is treated as semantic redundancy, not only color contrast;
- algorithmic or AI-assisted systems expose confidence, provenance, and human
  control.

This validates the existing GCS conventions in
`75-ui-design-system-conventions.md`: color must encode evidence, logs are
secondary, and solve reports must be visible as structured evidence. The next
architecture step should therefore deepen the evidence model rather than add a
new visual style.

### 2. CAD And GCS Products Reveal The Missing Workbench Surface

Commercial and open CAD sketchers do not stop at a canvas. They expose
constraints, constraint visibility, degrees of freedom, editing modes, and
recovery flows. Onshape, Shapr3D, FreeCAD, and Siemens D-Cubed sources all
converge on the same user need: users must see and control why geometry is
fixed, free, over-constrained, or inconsistent.

For GCS, this implies these first-class surfaces:

| Surface | User question | Solver evidence required |
| --- | --- | --- |
| Model canvas | What is selected, constrained, free, or violated? | Geometry/constraint IDs, focus, diagnostic state |
| Constraint manager | Which constraints define the model, and which are suspicious? | Constraint type, entities, residual, redundancy/conflict tags |
| DOF/rank inspector | Why is the model under/over/well constrained? | Structural DOF, numeric rank, nullity, gauge/free variables |
| Solve evidence rail | What did the last solve do? | Accepted/rolled back, status precedence, residual/rank summary |
| Local-to-global inspector | Which contexts solved and glued? | CoverPlan, BoundaryProjection, GluingReport, ObstructionReport |
| Replay/provenance timeline | What sequence produced this state? | Runtime history, frame projection, stage trace, report codes |
| Repair candidate panel | What can I try next? | Conflict/redundancy/obstruction responsibility sets and command drafts |

The current Python UI has model summary, object tables, solve summary, replay
rail, and renderer focus. It does not yet have the constraint manager,
structured diagnostic overlay, local-to-global inspector, or repair workflow.

### 3. Mathematical Users Need Certificate-Like Visibility

A top mathematician will not trust a GCS result because the points look right.
They need to inspect the claim behind the picture:

- the dimension of the variable space and equation space;
- structural rank versus numeric rank;
- nullity, free variables, frozen variables, and gauge policy;
- residuals per constraint and per context;
- local sections and boundary compatibility;
- whether an obstruction is local, overlap-based, numeric, or semantic;
- whether the solve committed or rolled back.

The repository already defines much of this vocabulary in
`docs/architecture/30-contracts/solver-contracts.md` and
`src/gcs/viewer_bridge/viewer_bridge.cppm`. The UI architecture should make
those projections visible rather than re-deriving truth from text.

### 4. CS Experts Need A Testable Projection Boundary

The best architecture move is not to make the GUI smarter. It is to make the
projection contract richer and more consumable:

- `session_runtime` owns commands, transactions, history, rollback, and
  accepted state;
- `diagnostics` owns DOF, rank, residual, conflict, redundancy, and obstruction
  semantics;
- `viewer_bridge` owns read-only scene, overlay, summary, interaction draft,
  and history-frame projections;
- `python/gcs_viz/platform_gui.py` owns Tk orchestration and current editable
  graph actions;
- `python/gcs_viz/visualizer.py` only draws supplied states;
- `python/gcs_viz/viewer_bridge.py` should host UI-neutral projection helpers
  and replay reconstruction.

This boundary matches `docs/architecture/10-system/system-topology.md`. It also
matches advanced UI practice: complex state should be centralized in typed
models and projections, while components render or dispatch commands.

### 5. GCS Users Need Repair Loops, Not Just Status Messages

The current UI can tell a user that a solve succeeded, warned, or failed. A
professional GCS tool must also answer "what do I do next?"

Minimum repair-loop requirements:

- select a violated or redundant constraint and highlight affected geometry;
- filter constraints by type, state, rigid set, residual, and responsibility
  set;
- show candidate actions as drafts, not direct mutation;
- preview whether deleting, relaxing, or adding a constraint changes DOF/rank;
- keep undo/replay provenance visible for every accepted edit;
- export a structured report for debugging and regression fixtures.

This is where current advanced UI and GCS-specific solver needs meet. The
interface must become an interactive debugger for geometric reasoning.

## Current Architecture Gap Analysis

| Area | Current evidence | Gap | Recommended adjustment |
| --- | --- | --- | --- |
| Design system | `75`, `76`, `77`, token lint, visual QA | Strong aesthetic governance, but solver-workbench capabilities are scattered across planned phases | Add a solver-workbench architecture layer over the existing aesthetic plan |
| Scene rendering | `visualizer.py` supports focus in 3D/graph/three-view | Focus only covers selected/replay objects; diagnostic states are planned but absent | Extend projection to constraint/entity states, not renderer-owned inference |
| Solve feedback | `platform_gui.py` has solve summary and `_parse_solve_report` | Free-form text parsing can invent or lose solver truth | Structured viewer/runtime reports are authoritative; text parser may only degrade to `unknown` |
| Constraint inspection | Object tables exist | No professional constraint manager or residual/conflict filters | Add constraint manager requirements before major feature UI work |
| Local-to-global semantics | Architecture docs define contexts, boundaries, gluing, obstructions | UI currently has no cover/gluing inspector | Add a deferred but explicit Local-to-Global Inspector surface |
| Replay/provenance | Replay rail exists; C++ viewer bridge has replay evidence artifacts | Python replay still reconstructs scene-construction history locally | Move frame/title/focus/progress projection into pure bridge helpers |
| Accessibility | Visual QA gates exist | Small-text semantic colors and graph labels remain known risks | Treat accessibility as state redundancy and agent-readable semantics |
| Agent/use by tools | Agentic docs and reports exist | UI state is not yet fully machine-readable | Expose stable projection snapshots/report artifacts for humans and tools |

## Recommended Target: GCS Solver Evidence Workbench

The UI target should be described as:

> A local desktop solver workbench that lets users construct geometry, inspect
> constraints, run solves, see structured rank/residual/diagnostic evidence,
> replay provenance, and draft repair commands without letting the UI own solver
> truth.

The workbench has six product zones:

1. **Model Canvas**: primary geometry, constraints, focus, diagnostic overlay,
   and local-to-global visual hints.
2. **Model/Constraint Inspector**: model summary, rigid sets, geometries,
   constraints, filters, edit actions, and selection-to-canvas linking.
3. **Solver Evidence Rail**: status precedence, accepted/rolled back state,
   residual/rank summaries, and report-code chips.
4. **Diagnostics Workbench**: DOF/rank/nullity, conflict sets, redundancy sets,
   obstruction sets, and residual tables.
5. **Replay And Provenance Timeline**: command history, frame projection,
   stage traces, deletion hints, and report export.
6. **Repair Draft Panel**: candidate commands derived from diagnostics,
   presented as drafts that route through `session_runtime`.

This target preserves the current stack: Tkinter plus embedded Matplotlib. It
does not require a web app, HTTP server, external design tool, or a GUI rewrite.

## Architecture Recommendations

1. Promote "GCS Solver Evidence Workbench" as the next UI architecture thesis.
   Keep "GCS Quiet Technical Atelier" as taste; make workbench capability the
   product architecture.

2. Treat `viewer_bridge` as the sole durable viewer evidence boundary. Python
   may mirror helpers temporarily, but GUI code must not parse free-form text
   when structured reports exist.

3. Reframe Phase 6 through Phase 10 in `77-ui-design-development-plan-report.md`
   as workbench phases:
   selection/focus, diagnostic overlay, accessibility/semantic state, replay
   provenance, and manual evidence QA.

4. Add a new follow-on phase for a constraint manager and repair draft panel.
   This should happen before large local-to-global visualizations, because
   users need a stable constraint list to navigate evidence.

5. Add a later local-to-global inspector for context covers, overlaps, gluing,
   and obstruction paths. This should consume planner/diagnostic reports rather
   than re-running solver logic in the UI.

6. Make every advanced UI feature pass three tests:
   "Can a mathematician inspect the claim?", "Can a CS expert trace the data
   contract?", and "Can a GCS user recover from failure?"

## Open Questions

- Which structured report format will the Python GUI consume first: JSON
  command-result artifacts, C++ viewer bridge bindings, or a CLI export path?
- Should the constraint manager arrive before or after Phase 7 diagnostic
  overlays? The research suggests before, but the current plan has overlay next.
- What is the minimal local-to-global inspector that helps users without
  exposing unfinished decomposition-planner internals?
- Should repair candidates be limited to non-mutating draft commands until the
  session runtime has stronger preview semantics?

## Recommended Next Task

Run a focused UI architecture increment:

- update `77-ui-design-development-plan-report.md` to name the solver workbench
  interpretation;
- implement Phase 6 as pure focus projection, including table selection;
- add test coverage for projection helpers without importing Tk;
- then implement a small diagnostic-state projection for constraints using
  structured data when available and `unknown` fallback otherwise.
