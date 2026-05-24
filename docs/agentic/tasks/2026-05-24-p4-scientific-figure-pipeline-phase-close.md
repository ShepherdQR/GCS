---
task_id: 2026-05-24-p4-scientific-figure-pipeline-phase-close
status: complete
request: "Close P4 Scientific Figure Pipeline after P4.4 and replan downstream visual-integrity work."
scope: architecture
risk: low
owning_agent: gcs-ui-design-steward
specialist_agents:
  - gcs-scientific-figure-producer
affected_contracts:
  - GCS Scientific Figure Pipeline
  - GCS Visual Integrity Gate
affected_paths:
  - docs/architecture/86-p4-scientific-figure-pipeline-phase-close.md
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

# P4 Scientific Figure Pipeline Phase Close

## Scope

Summarize P4 after P4.1-P4.4, close the phase in the execution plan, and
restate the downstream sequence before P5.2 starts.

## Non-Goals

- Do not change figure renderer code.
- Do not regenerate assets.
- Do not add visual QA gates; P5 owns them.
- Do not decide Figma MCP; P6.4 owns that.

## Context To Read

- `docs/architecture/76-ui-design-system-execution-plan.md`
- `docs/architecture/82-ui-design-next-work-plan.md`
- `docs/architecture/85-p4-4-execution-map-rebuild.md`

## Execution Plan

1. Write a P4 phase-close summary.
2. Mark P4 done in the execution plan.
3. Move the next step to P5.2 in the persisted next-work plan.
4. Archive the phase-close task and extract a reusable process lesson.
5. Validate and commit the phase-close docs.

## Acceptance Gates

- P4 status is `Done`.
- The phase-close note names completed P4 steps, stable decisions, residual
  risks, and downstream plan.
- P5.2 is the next explicit step.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-24-p4-scientific-figure-pipeline-phase-close.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-24-p4-scientific-figure-pipeline-phase-close\README.md
python tools\agentic_design\agentic_toolkit.py validate-docs
git diff --check -- docs/architecture docs/agentic/tasks docs/completed-tasks
```

## Evidence Bundle

- Phase-close note added.
- P4 marked done.
- P5.2 declared as next step.

## Residual Risks

- P4 close does not add new pixel/layout QA; that work begins in P5.2.
