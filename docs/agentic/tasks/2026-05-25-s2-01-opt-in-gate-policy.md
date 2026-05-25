---
task_id: 2026-05-25-s2-01-opt-in-gate-policy
status: complete
request: "Execute S2-01 by designing opt-in task-card and completed-report quality-gate policy without default enforcement."
scope: docs
risk: medium
owning_agent: gcs-quality-steward
specialist_agents:
  - gcs-architecture-steward
affected_contracts:
  - Agentic quality-gate policy
  - Task-card validation workflow
  - Completed-task report validation workflow
affected_paths:
  - docs/agentic/quality-gate-opt-in-policy.md
  - docs/agentic/README.md
  - docs/architecture/69-ci-ready-quality-gates.md
  - docs/agentic/agile-pdca-roadmap.md
  - docs/agentic/near-term-agent-plan.md
  - docs/completed-tasks/
required_evidence:
  - validate-task-card
  - validate-completed-task-report
  - score-closure-report
  - validate-docs
human_gate_required: false
human_gate_reason: ""
---

# S2-01 Opt-In Gate Policy

## Scope

Design the opt-in policy for task-card and completed-task report checks in
`run-quality-gates`.

## Non-Goals

- Do not implement CLI flags in this step.
- Do not make task-card or completed-report validation part of the default
  quality gate.
- Do not bulk-validate legacy archives.
- Do not change E001 scorer thresholds.
- Do not touch solver, runtime, IO, viewer, fixture, or CTest behavior.

## Context To Read

- `.codex/skills/gcs-quality-steward/SKILL.md`
- `tools/agentic_design/agentic_toolkit.py`
- `tests/tools/test_agentic_toolkit.py`
- `docs/architecture/69-ci-ready-quality-gates.md`
- `docs/agentic/lifecycle-runbook.md`
- `docs/agentic/task-to-archive-checklist.md`
- `docs/agentic/agile-pdca-roadmap.md`

## Acceptance Gates

- A policy document names proposed flags, gate IDs, pathspec rules, defaults,
  legacy behavior, and implementation order.
- `docs/architecture/69-ci-ready-quality-gates.md` records the planned opt-in
  behavior without claiming implementation.
- The Agile PDCA roadmap marks S2-01 done and registers follow-up tasks.
- The completed-task archive validates and scores at or above 30.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-s2-01-opt-in-gate-policy.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-s2-01-opt-in-gate-policy\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-s2-01-opt-in-gate-policy\README.md --min-score 30
python tools\agentic_design\agentic_toolkit.py validate-docs
```

## Evidence Bundle

- `validate-task-card`: passed.
- `validate-completed-task-report`: passed.
- `score-closure-report`: passed at 36/40.
- `validate-docs`: passed.

## Residual Risks

- The flags are not implemented yet; S2-02 and S2-03 own executable behavior.
- Pathspec expansion needs careful tests so unmatched includes cannot become
  false passes.
- Legacy exemption must remain explicit until S2-04.
