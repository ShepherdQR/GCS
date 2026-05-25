---
task_id: 2026-05-25-agentic-governance-execution
status: complete
request: "Persist the next AI governance plan and implement the first executable PR audit and nightly calibration tooling."
scope: tool
risk: medium
owning_agent: gcs-quality-steward
specialist_agents:
  - gcs-architecture-steward
  - task-scoped-session-closer
affected_contracts:
  - Agentic PR audit governance
  - Nightly immune diagnostics workflow
  - Agentic toolkit command surface
affected_paths:
  - docs/agentic/ai-governance-next-actions.md
  - docs/agentic/pr-audit-governance.md
  - docs/agentic/nightly-immune-diagnostics.md
  - docs/agentic/schemas/
  - docs/agentic/pr-audits/
  - docs/agentic/nightly-runs/
  - tools/agentic_design/agentic_toolkit.py
  - tests/tools/test_agentic_toolkit.py
  - docs/completed-tasks/2026-05-25-agentic-governance-execution/
required_evidence:
  - validate-task-card
  - python -m unittest tests.tools.test_agentic_toolkit
  - audit-pr smoke run
  - update-nightly-index smoke run
  - validate-docs
  - validate-completed-task-report
  - score-closure-report
human_gate_required: false
human_gate_reason: ""
---

# Agentic Governance Execution

## Scope

Persist the next AI governance roadmap as durable Markdown and implement the
first executable layer from that roadmap.

In scope:

- Add a maintained AI governance next-actions document.
- Add a machine-readable PR audit schema reference.
- Add an `audit-pr` prototype to the agentic toolkit.
- Add a nightly run index/calibration helper to the agentic toolkit.
- Add focused unit tests for the new toolkit behavior.
- Close the task with a completed-task archive and validation evidence.

## Non-Goals

- Do not change solver, runtime, IO, viewer, or scene semantics.
- Do not make PR audit a required default CI gate in this task.
- Do not allow unattended merge, approval, force-push, branch deletion, or
  fixture promotion.
- Do not create a dashboard UI before the JSON and Markdown contracts settle.

## Context To Read

- `docs/agentic/pr-audit-governance.md`
- `docs/agentic/nightly-immune-diagnostics.md`
- `docs/research/20260525/agentic-pr-governance/README.md`
- `docs/agentic/lifecycle-runbook.md`
- `docs/agentic/quality-gate-opt-in-policy.md`
- `docs/architecture/62-module-agents.md`
- `docs/architecture/65-agentic-implementation-tooling.md`

## Acceptance Gates

- The roadmap document records the next AI governance work as prioritized
  Markdown tasks.
- The PR audit schema names the same fields as the governance document and can
  be used by later validators.
- The `audit-pr` command emits deterministic JSON from a base/head diff without
  running network commands or mutating the repository.
- The nightly index helper summarizes dated `findings.json` files and records
  calibration status when fewer than two runs exist.
- Unit tests cover classification, schema-shaped audit output, and nightly
  index generation.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-agentic-governance-execution.md
python -m unittest tests.tools.test_agentic_toolkit
python tools\agentic_design\agentic_toolkit.py audit-pr --base codex/agentic-pr-governance-nightly --head HEAD --include-worktree --task-card docs/agentic/tasks/2026-05-25-agentic-governance-execution.md --output docs/agentic/pr-audits/2026-05-25-agentic-governance-execution.json --force
python tools\agentic_design\agentic_toolkit.py update-nightly-index --force
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-agentic-governance-execution\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-agentic-governance-execution\README.md --min-score 30
```

## Evidence Bundle

- Worktree created from `codex/agentic-pr-governance-nightly`.
- Task card created before implementation.
- Focused unit tests passed for `tests.tools.test_agentic_toolkit`.
- `update-nightly-index --force` generated `docs/agentic/nightly-runs/README.md`.
- `audit-pr` generated
  `docs/agentic/pr-audits/2026-05-25-agentic-governance-execution.json`.
- Completed-task archive validated and scored above the closure threshold.
- Agentic quality gates passed with build, CTest, and CLI explicitly skipped.

## Residual Risks

- The first `audit-pr` command is heuristic and should remain advisory until
  calibrated against real PR reviews.
- The nightly index reads local run artifacts only; it does not prove the
  scheduled automation has completed successfully.
