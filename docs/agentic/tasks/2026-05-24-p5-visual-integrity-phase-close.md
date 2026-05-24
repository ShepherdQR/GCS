---
task_id: 2026-05-24-p5-visual-integrity-phase-close
status: complete
request: "Close P5 Visual Integrity QA and replan P6 after screenshot baselines landed."
scope: architecture
risk: low
owning_agent: gcs-ui-design-steward
specialist_agents:
  - gcs-scientific-figure-producer
affected_contracts:
  - GCS Visual Integrity Gate
  - GCS Scientific Figure Pipeline
  - GCS Art Director Review
affected_paths:
  - docs/architecture/87-p5-visual-integrity-phase-close.md
  - docs/architecture/76-ui-design-system-execution-plan.md
  - docs/architecture/82-ui-design-next-work-plan.md
required_evidence:
  - validate-task-card
  - validate-completed-task-report
  - validate-docs
  - git-diff-check
human_gate_required: false
human_gate_reason: ""
---

# P5 Visual Integrity QA Phase Close

## Scope

Summarize P5 after P5.1-P5.4, close the phase in the execution plan, decide
default versus reviewer-only visual gates, and restate the downstream P6
sequence.

## Non-Goals

- Do not change UI QA code.
- Do not regenerate figure assets.
- Do not add more screenshot baselines.
- Do not decide Figma MCP; P6.4 owns that.

## Context To Read

- `docs/architecture/76-ui-design-system-execution-plan.md`
- `docs/architecture/82-ui-design-next-work-plan.md`
- `docs/architecture/70-visualization/screenshot-baseline-gate.md`

## Execution Plan

1. Write a P5 phase-close summary.
2. Mark P5 done and P6 active in the execution plan.
3. Decide which visual-integrity checks are default quality gates and which
   remain reviewer-only.
4. Move the next step to P6.1 in the persisted next-work plan.
5. Archive the phase-close task and extract a reusable process lesson.
6. Validate and commit the phase-close docs.

## Acceptance Gates

- P5 status is `Done`.
- P6 status is active or next.
- The phase-close note names completed P5 steps, default gates,
  reviewer-only gates, residual risks, and downstream P6 plan.
- P6.1 is the next explicit step.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-p5-visual-integrity-phase-close.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-p5-visual-integrity-phase-close\README.md
python tools\agentic_design\agentic_toolkit.py validate-docs
git diff --check -- docs/architecture docs/agentic/tasks docs/completed-tasks
```

## Evidence Bundle

- Phase-close note added.
- P5 marked done.
- P6.1 declared as next step.
- Default and reviewer-only visual gate boundary recorded.

## Residual Risks

- P5 close does not create new showcase artifacts; P6 owns that proof.
