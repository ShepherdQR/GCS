---
task_id: 2026-05-30-strengthen-09-institutional-agents-learning
status: draft
request: "Execute 3 immediate actions from the narrative-line-09 weakness analysis: (1) night-watch calibration run with dated findings directory, (2) seed packages (templates + refusal evals) for bookkeeper, collation-officer, and gardener candidates, (3) classify last 10 bladesmith forging notes and create agent trigger registry. All three are independent and parallelizable. Push when done."
scope: docs/agentic/institutional-agents, docs/agentic/evals, docs/agentic/nightly-runs, .claude/agents
risk: low
owning_agent: gcs-architecture-steward
specialist_agents:
  - none
affected_contracts:
  - none
affected_paths:
  - docs/agentic/
required_evidence:
  - validate-docs
  - validate-inventory
  - check-dependencies
human_gate_required: false
human_gate_reason: ""
---

# 2026-05-30-strengthen-09-institutional-agents-learning

## Scope

Describe what is in scope and what is intentionally out of scope.

## Non-Goals

- Do not change solver runtime semantics.
- Do not redefine architecture contracts in `docs/agentic`.

## Context To Read

- `docs/architecture/README.md`
- Owning skill: `gcs-architecture-steward`

## Acceptance Gates

- The owning boundary is clear.
- Required evidence is produced or a reason is recorded.
- Residual risks are named.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-30-strengthen-09-institutional-agents-learning.md
```

## Evidence Bundle

Record commands run, important outputs, changed files, and skipped checks.

## Residual Risks

List remaining uncertainty, review focus, or follow-up work.
