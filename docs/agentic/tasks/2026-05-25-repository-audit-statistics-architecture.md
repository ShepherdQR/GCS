---
task_id: 2026-05-25-repository-audit-statistics-architecture
status: complete
request: "Research mature repository audit/statistics practices and design a GCS repository statistics architecture."
scope: architecture
risk: medium
owning_agent: gcs-architecture-steward
specialist_agents:
  - gcs-contract-tools-steward
affected_contracts:
  - RepositoryAuditSnapshot
affected_paths:
  - docs/research/20260525/repository-audit-statistics/
  - docs/architecture/94-repository-audit-statistics-architecture.md
  - docs/agentic/tasks/2026-05-25-repository-audit-statistics-architecture.md
  - docs/completed-tasks/2026-05-25-repository-audit-statistics-architecture/
required_evidence:
  - agentic.validate-task-card
  - agentic.validate-docs
  - source-register-review
  - git-status-scope-check
human_gate_required: false
human_gate_reason: ""
---

## Scope

Research mature repository audit and statistics practices, capture a current
GCS repository statistics baseline, and design a GCS-specific repository audit
architecture that fits the existing agentic tooling and quality-gate layer.

## Non-Goals

- Do not change C++ solver runtime semantics.
- Do not add a default quality-gate step before the metric schema and generated
  snapshots are implemented and stabilized.
- Do not include unrelated local edits in the commit.

## Context To Read

- `docs/architecture/README.md`
- `docs/architecture/10-system/system-topology.md`
- `docs/architecture/40-quality/verification-strategy.md`
- `docs/architecture/69-ci-ready-quality-gates.md`
- `tools/agentic_design/module_inventory.json`
- External primary sources for Linguist, cloc, tokei, SonarQube, CNCF,
  OpenSSF, Chromium, and Linux Kernel reporting practices.

## Acceptance Gates

- The research report has a source register and separates sourced facts from
  GCS-specific inference.
- The architecture note identifies ownership, data flow, schemas, commands,
  report locations, gates, and non-goals.
- Current GCS baseline statistics are reproducible from Git-tracked files.
- Task card, architecture doc coverage, and completed-task report validations
  pass or skipped checks are recorded as residual risk.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-25-repository-audit-statistics-architecture.md
python tools\agentic_design\agentic_toolkit.py validate-docs
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-25-repository-audit-statistics-architecture\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-25-repository-audit-statistics-architecture\README.md --min-score 30
```

## Evidence Bundle

- `docs/research/20260525/repository-audit-statistics/README.md` records the
  source-aware research report, source register, GCS baseline statistics, and
  recommendations.
- `docs/architecture/94-repository-audit-statistics-architecture.md` defines
  the proposed audit ownership, data flow, JSON schema, commands, artifact
  classes, module join, storage policy, quality-gate integration, and phases.
- `python tools\agentic_design\agentic_toolkit.py validate-docs` passed.
- Initial task-card validation failed only on a leftover affected-contracts
  template placeholder; it was replaced with `RepositoryAuditSnapshot`.
- Full build/CTest gates were skipped because no code, fixtures, schemas, or
  runtime behavior changed.

## Residual Risks

- External project metrics evolve over time; cite source access dates and prefer
  architecture principles over fixed vendor-specific thresholds.
