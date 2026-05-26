---
task_id: 2026-05-26-repository-audit-diff-mode
status: complete
request: "Persist and execute the next repository-audit statistics plan by adding diff mode."
scope: tool
risk: medium
owning_agent: gcs-contract-tools-steward
specialist_agents:
  - task-scoped-session-closer
affected_contracts:
  - RepositoryAuditSnapshot
  - RepositoryAuditDiff
affected_paths:
  - tools/repository_audit/
  - tests/tools/test_repository_audit.py
  - docs/architecture/94-repository-audit-statistics-architecture.md
  - docs/agentic/tasks/2026-05-26-repository-audit-diff-mode.md
  - docs/completed-tasks/2026-05-26-repository-audit-diff-mode/
required_evidence:
  - python.repository_audit_tests
  - repository_audit.diff
  - repository_audit.check
  - agentic.validate-task-card
  - agentic.validate-completed-task-report
  - agentic.score-closure-report
human_gate_required: false
human_gate_reason: ""
---

## Scope

Implement the next repository-audit node: deterministic diff mode for comparing
two audit snapshots or two Git revisions. The output should quantify changed
files, totals, artifact classes, lifecycle layers, top-level directories,
modules, and findings.

## Non-Goals

- Do not add default quality-gate enforcement.
- Do not add historical trend charts in this node.
- Do not add external tool adapters.
- Do not mutate solver, runtime, IO, viewer, fixture, or scene schema behavior.

## Context To Read

- `docs/architecture/94-repository-audit-statistics-architecture.md`
- `tools/repository_audit/README.md`
- `docs/completed-tasks/2026-05-26-repository-audit-overview-and-session-efficiency/README.md`

## Acceptance Gates

- `repository_audit.py diff --base-snapshot ... --head-snapshot ...` writes a
  deterministic JSON diff.
- `repository_audit.py diff --base <rev> --head <rev>` can collect committed
  revision snapshots and compare them.
- Focused tests cover added, removed, and modified files plus group deltas.
- Existing collect, report, and check behavior remains intact.
- The completed-task archive records verification and residual risks.

## Verification Plan

```bat
python -m unittest tests.tools.test_repository_audit
python tools\repository_audit\repository_audit.py diff --base HEAD~1 --head HEAD --output var\repository-audit\diff-head-prev.json
python tools\repository_audit\repository_audit.py check
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-repository-audit-diff-mode.md
python tools\agentic_design\agentic_toolkit.py validate-docs
```

## Evidence Bundle

- `python -m unittest tests.tools.test_repository_audit`: passed, 8 tests.
- `python tools\repository_audit\repository_audit.py diff --base HEAD~1 --head HEAD --output var\repository-audit\diff-head-prev.json`: passed, 13 changed files, 1104 text-line delta, 0 added findings, 0 removed findings.
- `python tools\repository_audit\repository_audit.py check`: passed with 0 errors and 0 warnings.
- `python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-repository-audit-diff-mode.md`: passed.
- `python tools\agentic_design\agentic_toolkit.py validate-docs`: passed.

## Residual Risks

- Revision snapshots use the current `module_inventory.json` for module joins;
  historical inventory-at-revision support can be added later if needed.
- Rename detection is out of scope; diff mode reports renames as remove plus
  add unless a future Git-aware layer adds explicit rename pairing.
