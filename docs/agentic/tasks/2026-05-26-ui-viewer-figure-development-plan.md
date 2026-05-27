---
task_id: 2026-05-26-ui-viewer-figure-development-plan
status: complete
request: "Turn the next development plan for the UI/viewer/scientific figures line into a saved development plan, push it, and run codex-task-closeout."
scope: architecture
risk: medium
owning_agent: gcs-ui-design-steward
specialist_agents:
  - gcs-architecture-steward
  - gcs-scientific-figure-producer
affected_contracts:
  - GCS Evidence-First Interface Grammar
  - GCS Scientific Figure Pipeline
  - GCS Visual Integrity Gate
  - viewer_bridge projection boundary
affected_paths:
  - docs/architecture/
  - docs/product/demos/d5-solver-evidence-workbench/
  - docs/agentic/tasks/
  - docs/completed-tasks/
required_evidence:
  - validate-task-card
  - validate-completed-task-report
  - score-closure-report
  - validate-docs
  - git diff --check
human_gate_required: false
human_gate_reason: "User explicitly requested a saved development plan, closeout, and push."
---

# 2026-05-26-ui-viewer-figure-development-plan

## Scope

Create a durable next-stage development plan for the UI/viewer/scientific
figures line and link it from the active architecture and demo docs.

## Non-Goals

- Do not update `docs/architecture/95-gcs-narrative-map.md`.
- Do not change GUI, solver, report, or figure-generation behavior.
- Do not claim that future milestones are implemented.

## Context To Read

- `docs/architecture/75-ui-design-system-conventions.md`
- `docs/architecture/76-ui-design-system-execution-plan.md`
- `docs/architecture/97-ui-viewer-figure-integration-plan.md`
- `docs/architecture/70-visualization/viewer-phase-10-visual-qa.md`
- `docs/architecture/70-visualization/visual-evidence-manifest.md`
- `docs/product/demos/d5-solver-evidence-workbench/`
- `codex-task-closeout`

## Acceptance Gates

- A new saved development plan exists under `docs/architecture/`.
- The plan starts from VE-001/VE-002 and names next milestones.
- Relevant architecture/demo indexes link to the plan.
- Closeout archive records evidence and push state.
- Narrative map remains unchanged.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-ui-viewer-figure-development-plan.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-ui-viewer-figure-development-plan\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-ui-viewer-figure-development-plan\README.md --min-score 30
python tools\agentic_design\agentic_toolkit.py validate-docs
git diff --check
```

## Evidence Bundle

- Created `docs/architecture/98-ui-viewer-figure-development-plan.md`.
- Linked it from `97-ui-viewer-figure-integration-plan.md`,
  `76-ui-design-system-execution-plan.md`, `docs/architecture/README.md`, and
  the D5 demo package.
- `docs/architecture/95-gcs-narrative-map.md` was not modified.

## Residual Risks

- The plan is architecture guidance only; implementation work remains in future
  UVF milestones.
- Narrative map reassessment is intentionally deferred until a new proof point
  lands.
