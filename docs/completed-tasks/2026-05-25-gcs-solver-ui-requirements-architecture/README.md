---
task_id: 2026-05-25-gcs-solver-ui-requirements-architecture
status: complete
session_goal: "Research advanced UI design and GCS solver UI requirements, then persist a UI architecture adjustment record."
archive_target: docs/completed-tasks/2026-05-25-gcs-solver-ui-requirements-architecture/
experience_links: []
---

# GCS Solver UI Requirements Architecture

## Task Objective

Analyze GCS solver UI requirements from advanced UI practice, top
mathematician, computer scientist, and GCS user perspectives. Persist the
research as Markdown and adjust the UI architecture design with an explicit
architecture adjustment record.

## Scope And Non-Goals

In scope:

- internet-backed UI research;
- project-local architecture and Python viewer review;
- durable Markdown research report;
- architecture adjustment record;
- updates to UI architecture entry points and forward plan;
- task-card and completed-task closure.

Out of scope:

- Python GUI implementation;
- C++ contract changes;
- solver runtime, numeric, diagnostics, or IO behavior changes;
- new browser, HTTP, web asset, Figma, or external viewer dependency.

## Interaction Summary

The user requested `/plan` analysis of GCS solver UI needs and noted that the
current UI design was too simple. They then explicitly requested internet
research into current advanced UI design. The work therefore combined external
source research, existing GCS UI architecture review, and a planning-level
architecture update.

## Work Completed

- Created a scoped task card for the UI requirements architecture task.
- Researched advanced UI design and CAD/GCS-related UI patterns using official
  and authoritative sources.
- Reviewed current project UI architecture, design-system, viewer, diagnostics,
  runtime, and Python GUI evidence.
- Wrote a source-aware research report that reframes the target as a GCS
  Solver Evidence Workbench.
- Added a UI architecture adjustment record that names workbench zones, boundary
  rules, and follow-on phases.
- Updated architecture README, UI design-system conventions, and UI development
  plan to reference the adjustment.

## Files And Artifacts

- `docs/research/20260525/gcs-ui-requirements/01-advanced-ui-and-gcs-solver-requirements.md`:
  advanced UI and GCS solver UI requirements research report.
- `docs/architecture/92-gcs-ui-architecture-adjustment-record.md`: architecture
  adjustment record for the GCS Solver Evidence Workbench target.
- `docs/architecture/77-ui-design-development-plan-report.md`: updated with
  the solver-workbench adjustment and Phase 11/12 backlog.
- `docs/architecture/75-ui-design-system-conventions.md`: updated to name the
  Solver Evidence Workbench adjustment.
- `docs/architecture/README.md`: updated to index the adjustment record.
- `docs/agentic/tasks/2026-05-25-gcs-solver-ui-requirements-architecture.md`:
  task card for the work.
- `docs/completed-tasks/2026-05-25-gcs-solver-ui-requirements-architecture/README.md`:
  this archive.

## Evidence

External research sources included:

- Apple Human Interface Guidelines;
- Google Material Design;
- Microsoft Fluent 2;
- IBM Carbon Design System and Carbon Charts;
- IBM Design for AI;
- Nielsen Norman Group usability heuristics;
- W3C WCAG 2.2;
- Siemens D-Cubed 2D/3D DCM;
- Onshape Sketch Tools;
- Shapr3D constraint settings;
- FreeCAD Sketcher Workbench.

Project-local sources inspected included:

- `docs/architecture/75-ui-design-system-conventions.md`;
- `docs/architecture/76-ui-design-system-execution-plan.md`;
- `docs/architecture/77-ui-design-development-plan-report.md`;
- `docs/architecture/10-system/system-topology.md`;
- `docs/architecture/30-contracts/solver-contracts.md`;
- `src/gcs/viewer_bridge/viewer_bridge.cppm`;
- `python/gcs_viz/platform_gui.py`;
- `python/gcs_viz/viewer_bridge.py`;
- `python/gcs_viz/visualizer.py`;
- `.codex/skills/gcs-ui-design-steward/SKILL.md`;
- `.codex/skills/gcs-architecture-steward/SKILL.md`;
- `.codex/skills/gcs-python-gui-builder/SKILL.md`.

Document presence and linkage check:

```text
rg -n "Solver Evidence Workbench|Phase 11|Phase 12|gcs-ui-architecture-adjustment|advanced-ui-and-gcs" docs\architecture docs\research\20260525\gcs-ui-requirements docs\agentic\tasks\2026-05-25-gcs-solver-ui-requirements-architecture.md

Result:
- research report contains the Solver Evidence Workbench recommendation;
- architecture README links the new adjustment record;
- UI development plan links the adjustment and research report;
- UI development plan contains Phase 11 and Phase 12 backlog sections;
- UI design-system conventions name the workbench adjustment.
```

Task-card validation:

```text
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-gcs-solver-ui-requirements-architecture.md

Result: [OK] task-card passed.
```

Completed-task validation:

```text
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-gcs-solver-ui-requirements-architecture\README.md

Result: [OK] completed-task-report passed.
```

Closure score:

```text
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-gcs-solver-ui-requirements-architecture\README.md --min-score 30

Result: closure score 35/40, passed min score 30.
```

Whitespace check:

```text
git diff --check -- docs\architecture\README.md docs\architecture\75-ui-design-system-conventions.md docs\architecture\77-ui-design-development-plan-report.md docs\architecture\92-gcs-ui-architecture-adjustment-record.md docs\research\20260525\gcs-ui-requirements\01-advanced-ui-and-gcs-solver-requirements.md docs\agentic\tasks\2026-05-25-gcs-solver-ui-requirements-architecture.md

Result: passed; Git reported only CRLF normalization warnings for existing docs.
```

## Decisions

- Reframe the UI target as **GCS Solver Evidence Workbench**.
- Keep **GCS Quiet Technical Atelier** as the taste thesis and make
  **GCS Evidence-First Interface Grammar** the product-architecture driver for
  future GUI phases.
- Preserve the local desktop stack: Tkinter plus embedded Matplotlib.
- Treat `viewer_bridge` as the durable read-only evidence boundary.
- Allow text parsing only as a temporary fallback that degrades to `unknown`;
  structured reports are authoritative when available.
- Add Phase 11, Constraint Manager And Repair Drafts, and Phase 12,
  Local-To-Global Evidence Inspector, to the UI architecture backlog.

## Skipped Checks And Risks

- Build, CTest, and Python GUI compile checks were skipped because no code,
  schemas, fixtures, or runtime behavior changed.
- Browser/manual visual QA was skipped because this task changed architecture
  documentation, not rendered UI behavior.
- Implementation feasibility remains future work, especially delivery of
  structured C++ viewer projections to the Python GUI.
- Some external source mappings are design inference, not proof that a given
  CAD product's workflow directly transfers to GCS.

## Follow-Up

Recommended next implementation task:

```text
Title: UI Phase 6 focus projection workbench primitive

Goal:
Move selection/replay focus projection into pure viewer-bridge helpers, add
table-selection highlighting for rigid sets, geometries, and constraints, and
test the projection path without importing Tk.
```

Near-term sequence:

- Phase 6: selection/focus projection;
- Phase 7: diagnostic-state overlay;
- Phase 11: constraint manager and repair drafts once diagnostic projections
  are stable;
- Phase 12: local-to-global evidence inspector after planner/diagnostic reports
  are ready.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-25-gcs-solver-ui-requirements-architecture/`
- Task card:
  `docs/agentic/tasks/2026-05-25-gcs-solver-ui-requirements-architecture.md`
- Owning skill:
  `gcs-ui-design-steward`
- Specialist skills:
  `gcs-architecture-steward`, `gcs-python-gui-builder`
- No skill, eval, fixture, or tool update is required immediately.
