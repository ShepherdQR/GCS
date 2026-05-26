---
task_id: 2026-05-26-repository-audit-snapshot-registry
status: complete
request: "Continue the repository-audit statistics plan by adding accepted snapshot registry support and pushing the result."
scope: tool
risk: medium
owning_agent: gcs-contract-tools-steward
specialist_agents:
  - task-scoped-session-closer
affected_contracts:
  - RepositoryAuditSnapshot
  - repository-audit accepted snapshot manifest
  - repository-audit registry index
affected_paths:
  - tools/repository_audit/
  - tests/tools/test_repository_audit.py
  - docs/reports/repository-audit/
  - docs/architecture/94-repository-audit-statistics-architecture.md
  - docs/agentic/tasks/2026-05-26-repository-audit-snapshot-registry.md
  - docs/completed-tasks/2026-05-26-repository-audit-snapshot-registry/
required_evidence:
  - python.repository_audit_tests
  - repository_audit.collect_revision
  - repository_audit.index
  - repository_audit.check
  - agentic.validate-task-card
  - agentic.validate-completed-task-report
  - agentic.score-closure-report
  - agentic.validate-docs
human_gate_required: false
human_gate_reason: ""
---

## Scope

Add the first durable accepted snapshot registry for repository-audit
statistics:

1. Support collecting snapshots from committed Git revisions through the CLI.
2. Add accepted snapshot manifest discovery.
3. Generate `docs/reports/repository-audit/README.md` as the registry index.
4. Persist the first accepted baseline snapshot and manifest.

## Non-Goals

- Do not promote repository audit to a default quality gate.
- Do not add external scanners, charts, or token-efficiency blocking gates.
- Do not mutate solver, runtime, IO, viewer, fixture, or scene schema behavior.
- Do not stage unrelated local research edits.

## Context To Read

- `docs/architecture/94-repository-audit-statistics-architecture.md`
- `tools/repository_audit/README.md`
- `docs/completed-tasks/2026-05-26-repository-audit-next-steps-execution/README.md`

## Acceptance Gates

- `collect --revision HEAD` writes a snapshot from a committed revision.
- `index` renders accepted snapshot manifests into a durable Markdown index.
- `docs/reports/repository-audit/2026-05-26/manifest.json` records the
  accepted baseline.
- Focused tests cover registry index rendering.
- Completed-task archive records implementation, evidence, decisions, risks,
  and follow-up.

## Verification Plan

```bat
python -m unittest tests.tools.test_repository_audit
python tools\repository_audit\repository_audit.py collect --revision HEAD --output docs\reports\repository-audit\2026-05-26\snapshot.json
python tools\repository_audit\repository_audit.py index --reports-root docs\reports\repository-audit --output docs\reports\repository-audit\README.md
python tools\repository_audit\repository_audit.py check
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-repository-audit-snapshot-registry.md
python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-26-repository-audit-snapshot-registry\README.md
python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-26-repository-audit-snapshot-registry\README.md --min-score 30
python tools\agentic_design\agentic_toolkit.py validate-docs
```

## Evidence Bundle

- `python -m unittest tests.tools.test_repository_audit`: passed, 11 tests.
- `python tools\repository_audit\repository_audit.py collect --revision HEAD --output docs\reports\repository-audit\2026-05-26\snapshot.json`: passed, 825 files, 149448 text lines, 0 findings.
- `python tools\repository_audit\repository_audit.py report --snapshot docs\reports\repository-audit\2026-05-26\snapshot.json --output docs\reports\repository-audit\2026-05-26\README.md`: passed.
- `python tools\repository_audit\repository_audit.py index --reports-root docs\reports\repository-audit --output docs\reports\repository-audit\README.md`: passed, 1 accepted snapshot.
- `python tools\repository_audit\repository_audit.py check`: passed, 0 errors and 0 warnings.
- Archive, docs, and quality-gate validators are recorded in the completed-task
  archive.

## Residual Risks

- The first accepted snapshot is an initial registry seed; trend policy still
  needs more baselines before default cadence decisions are meaningful.
- Token-efficiency joins remain an architecture plan, not an enforced metric.
