---
task_id: 2026-05-26-repository-audit-collector-mvp
status: complete
request: "Implement the first repository audit collector MVP from the repository audit architecture plan."
scope: tool
risk: medium
owning_agent: gcs-contract-tools-steward
specialist_agents:
  - gcs-quality-steward
affected_contracts:
  - RepositoryAuditSnapshot
affected_paths:
  - tools/repository_audit/
  - tests/tools/test_repository_audit.py
  - docs/agentic/tasks/2026-05-26-repository-audit-collector-mvp.md
  - docs/completed-tasks/2026-05-26-repository-audit-collector-mvp/
required_evidence:
  - agentic.validate-docs
  - python.repository_audit_tests
  - repository_audit.collect
  - agentic.validate-task-card
  - agentic.validate-completed-task-report
human_gate_required: false
human_gate_reason: ""
---

## Scope

Implement the Phase 1 repository audit collector MVP: typed snapshot data,
tracked-file collection, artifact classification, basic module inventory join,
JSON output, CLI surface, and focused unit tests.

## Non-Goals

- Do not add default quality-gate enforcement.
- Do not add network-dependent external adapters.
- Do not implement historical trend reports or PR diff mode in this task.
- Do not change solver core, fixtures, scene schemas, or GUI behavior.

## Context To Read

- `docs/architecture/94-repository-audit-statistics-architecture.md`
- `docs/research/20260525/repository-audit-statistics/README.md`
- `tools/agentic_design/module_inventory.json`
- `docs/architecture/65-agentic-implementation-tooling.md`

## Acceptance Gates

- `tools/repository_audit/repository_audit.py collect` writes deterministic
  `RepositoryAuditSnapshot` JSON from Git tracked files.
- Artifact classification covers every class named in the architecture note.
- Non-ASCII paths and Windows separators are handled without quoted-path
  corruption.
- Module source, contract-test, and skill coverage are joined from
  `module_inventory.json`.
- Focused tests pass.

## Verification Plan

```bat
python -m unittest tests.tools.test_repository_audit
python tools\repository_audit\repository_audit.py collect --output var\repository-audit\latest.snapshot.json
python tools\repository_audit\repository_audit.py check --snapshot var\repository-audit\latest.snapshot.json
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-repository-audit-collector-mvp.md
python tools\agentic_design\agentic_toolkit.py validate-docs
```

## Evidence Bundle

- `python -m unittest tests.tools.test_repository_audit`: passed, 5 tests.
- `python tools\repository_audit\repository_audit.py collect --output var\repository-audit\latest.snapshot.json`: wrote deterministic snapshot.
- `python tools\repository_audit\repository_audit.py check --snapshot var\repository-audit\latest.snapshot.json`: passed with 0 errors and 2 warnings.
- `python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-repository-audit-collector-mvp.md`: passed.
- `python tools\agentic_design\agentic_toolkit.py validate-docs`: passed.
- `python tools\agentic_design\agentic_toolkit.py validate-pr-audit docs\agentic\pr-audits\2026-05-26-repository-audit-collector-mvp.json`: passed.

## Residual Risks

- Full quality gates may remain skipped if this task only changes Python
  support tooling and documentation.
- The collector implements the Phase 1 collect/check MVP only; report, diff,
  and quality-gate integration remain future phases.
