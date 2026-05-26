---
task_id: 2026-05-26-repository-audit-overview-and-session-efficiency
status: complete
request: "Persist the repository audit follow-up analysis, add a project overview surface, and design token-to-outcome session governance."
scope: tool
risk: medium
owning_agent: gcs-contract-tools-steward
specialist_agents:
  - gcs-architecture-steward
  - task-scoped-session-closer
affected_contracts:
  - RepositoryAuditSnapshot
  - RepositoryAuditReport
  - AgenticSessionEfficiencyRecord
affected_paths:
  - tools/repository_audit/
  - tests/tools/test_repository_audit.py
  - docs/architecture/
  - docs/reports/repository-audit/
  - docs/agentic/tasks/2026-05-26-repository-audit-overview-and-session-efficiency.md
  - docs/completed-tasks/2026-05-26-repository-audit-overview-and-session-efficiency/
required_evidence:
  - python.repository_audit_tests
  - repository_audit.report
  - repository_audit.check
  - agentic.validate-task-card
  - agentic.validate-completed-task-report
  - agentic.score-closure-report
human_gate_required: false
human_gate_reason: ""
---

## Scope

Advance the repository audit work from JSON-only collection to a durable
human-readable project overview, and persist the proposed token-to-outcome
governance model as an architecture note.

## Non-Goals

- Do not add default quality-gate enforcement.
- Do not add network-dependent external scanners.
- Do not implement historical trend charts or PR diff mode in this node.
- Do not require token telemetry as a blocking gate before a calibration
  baseline exists.

## Context To Read

- `docs/architecture/94-repository-audit-statistics-architecture.md`
- `tools/repository_audit/README.md`
- `docs/research/20260524/agentic-se-dimensions-metrics-research-report.md`
- `docs/agentic/institutional-agents/README.md`

## Acceptance Gates

- `repository_audit.py report` can render a Markdown report from either a
  current collection or a saved snapshot.
- The generated report includes headline totals, artifact classes, module
  coverage, and agentic governance counts.
- Current known unknown-class warnings are resolved or documented.
- A durable architecture note defines session-efficiency metrics, formulas,
  schema, and rollout phases.
- Focused tests and agentic validators pass.

## Verification Plan

```bat
python -m unittest tests.tools.test_repository_audit
python tools\repository_audit\repository_audit.py report --output docs\reports\repository-audit\2026-05-26\README.md
python tools\repository_audit\repository_audit.py check
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-repository-audit-overview-and-session-efficiency.md
python tools\agentic_design\agentic_toolkit.py validate-docs
```

## Evidence Bundle

- `python -m unittest tests.tools.test_repository_audit`: passed, 6 tests.
- `python tools\repository_audit\repository_audit.py report --output docs\reports\repository-audit\2026-05-26\README.md`: wrote Markdown project overview.
- `python tools\repository_audit\repository_audit.py check`: passed with 0 errors and 0 warnings.
- `python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-repository-audit-overview-and-session-efficiency.md`: passed.
- `python tools\agentic_design\agentic_toolkit.py validate-docs`: passed.
- `python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-repository-audit-overview-and-session-efficiency\README.md`: passed.
- `python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-repository-audit-overview-and-session-efficiency\README.md --min-score 30`: passed, 36/40.

## Residual Risks

- Token fields depend on session telemetry availability; the first design
  should allow manual or external capture instead of assuming the Codex UI can
  always write exact token counts into the repo.
- Efficiency metrics can be gamed if used as a scoreboard; first rollout must
  keep them diagnostic and bucketed by task type.
