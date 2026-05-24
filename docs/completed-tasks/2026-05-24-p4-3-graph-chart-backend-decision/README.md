---
task_id: 2026-05-24-p4-3-graph-chart-backend-decision
status: complete
session_goal: "Close P4.3 by recording whether graph/chart backends are needed before the Figure 71 rebuild."
archive_target: docs/completed-tasks/2026-05-24-p4-3-graph-chart-backend-decision/
experience_links:
  - docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-24-p4-3-graph-chart-backend-decision-forging-note.md
---

# P4.3 Graph/Chart Backend Decision

## Task Objective

Decide whether the execution-map figure pipeline needs a new graph or chart
backend before P4.4 rebuilds Figure 71. The objective was to make the
dependency boundary explicit before visual work resumed.

## Scope And Non-Goals

In scope:

- review the third-party dependency policy;
- record a structured graph/chart backend decision;
- update the UI/scientific-figure roadmap;
- archive the step and extract a reusable process lesson.

Out of scope:

- adding or installing graph/chart/Figma/MCP/browser dependencies;
- changing CMake or production targets;
- rebuilding Figure 71 assets;
- changing solver/runtime/viewer code.

## Interaction Summary

After P5.1 landed token lint, the persisted roadmap pointed to P4.3 before
P4.4. This step used the third-party governance lens to decide whether the
execution-map rebuild justified a new backend. The decision was to defer all
external graph/chart backends and keep P4.4 on the repo-native pipeline.

## Work Completed

- Added `docs/architecture/84-p4-3-graph-chart-backend-decision.md`.
- Recorded `ThirdPartyDecision`: defer graph/chart backends for P4.4.
- Captured future provider order and dependency metadata requirements.
- Updated `docs/architecture/76-ui-design-system-execution-plan.md`.
- Updated `docs/architecture/82-ui-design-next-work-plan.md`.

## Files And Artifacts

- `docs/architecture/84-p4-3-graph-chart-backend-decision.md`: structured
  dependency decision.
- `docs/agentic/tasks/2026-05-24-p4-3-graph-chart-backend-decision.md`: task
  card.
- `docs/completed-tasks/2026-05-24-p4-3-graph-chart-backend-decision/README.md`:
  this archive.
- `docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-24-p4-3-graph-chart-backend-decision-forging-note.md`:
  process lesson.

## Evidence

```text
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-p4-3-graph-chart-backend-decision.md
Passed.

python -B tools\ui_qa\gcs_token_lint.py
Passed.

python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-p4-3-graph-chart-backend-decision\README.md
Passed.

git diff --check -- docs/architecture docs/agentic/tasks docs/completed-tasks
Passed with only existing CRLF conversion warnings.
```

## Decisions

- Decision: defer graph/chart backends for P4.4. Rationale: Figure 71 does not
  yet need a true graph layout or quantitative chart compiler.
- Decision: keep P4.4 repo-native. Rationale: P4.2 browser export and P5.1
  token lint are enough to guard the current asset rebuild.
- Decision: future graph/chart candidates must go through a full
  `ThirdPartyRequest`. Rationale: dependency policy requires version, URL,
  license, scope, provider order, offline behavior, and audit gates.

## Skipped Checks And Risks

- Full C++ build and CTest were skipped because P4.3 is a documentation-only
  dependency decision.
- The decision may be revisited if P6 showcase work introduces genuine graph
  or chart panels.
- P4.3 does not improve Figure 71 visual quality directly; P4.4 owns the
  actual rebuild.

## Follow-Up

- Execute P4.4 by regenerating Figure 71 assets through the repo-native
  pipeline and demoting the old SVG output to prototype history.
- Reassess graph/chart needs only after P5.2/P5.3 layout gates make richer
  panels measurable.

## Archive Handoff

- Archive path:
  `docs/completed-tasks/2026-05-24-p4-3-graph-chart-backend-decision/`
- Related experience:
  - `docs/agentic/institutional-agents/001-bladesmith-quench-forge/examples/2026-05-24-p4-3-graph-chart-backend-decision-forging-note.md`
- Skill, eval, fixture, or tool update needed: no immediate skill update; use
  this decision as input to P4.4 and P6.4.
