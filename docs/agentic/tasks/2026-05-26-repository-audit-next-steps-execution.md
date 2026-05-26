---
task_id: 2026-05-26-repository-audit-next-steps-execution
status: complete
request: "Execute the next repository-audit statistics steps after diff mode: diff Markdown projection, trend reports, and opt-in quality gate integration."
scope: tool
risk: medium
owning_agent: gcs-contract-tools-steward
specialist_agents:
  - gcs-quality-steward
  - task-scoped-session-closer
affected_contracts:
  - RepositoryAuditDiff
  - RepositoryAuditTrend
  - repository-audit quality gate
affected_paths:
  - tools/repository_audit/
  - tools/agentic_design/agentic_toolkit.py
  - tests/tools/
  - docs/architecture/94-repository-audit-statistics-architecture.md
  - docs/agentic/tasks/2026-05-26-repository-audit-next-steps-execution.md
  - docs/completed-tasks/2026-05-26-repository-audit-next-steps-execution/
required_evidence:
  - python.repository_audit_tests
  - python.agentic_toolkit_tests
  - repository_audit.diff_report
  - repository_audit.trend
  - agentic.repository_audit_gate
  - agentic.validate-task-card
  - agentic.validate-completed-task-report
human_gate_required: false
human_gate_reason: ""
---

## Scope

Execute the next three repository-audit statistics steps after JSON diff mode:

1. Render `RepositoryAuditDiff` as Markdown.
2. Add a first snapshot trend report projection.
3. Add repository audit as an opt-in quality gate.

## Non-Goals

- Do not add default quality-gate enforcement.
- Do not add external scanners.
- Do not add blocking token-efficiency gates.
- Do not mutate solver, runtime, IO, viewer, fixture, or scene schema behavior.

## Context To Read

- `docs/architecture/94-repository-audit-statistics-architecture.md`
- `tools/repository_audit/README.md`
- `docs/completed-tasks/2026-05-26-repository-audit-diff-mode/README.md`
- `docs/architecture/95-agentic-session-efficiency-governance.md`

## Acceptance Gates

- Diff Markdown output is generated from a saved diff JSON.
- Trend Markdown output is generated from two or more saved snapshots.
- `run-quality-gates --include-repository-audit` runs repository audit check.
- Focused Python tests cover the new report and gate behavior.
- Completed-task archive records all steps, evidence, decisions, and risks.

## Verification Plan

```bat
python -m unittest tests.tools.test_repository_audit
python -m unittest tests.tools.test_agentic_toolkit
python tools\repository_audit\repository_audit.py diff --base HEAD~1 --head HEAD --output var\repository-audit\next.diff.json
python tools\repository_audit\repository_audit.py diff-report --diff var\repository-audit\next.diff.json --output var\repository-audit\next.diff.md
python tools\repository_audit\repository_audit.py trend --snapshot <a> --snapshot <b> --output var\repository-audit\trend.md
python tools\agentic_design\agentic_toolkit.py run-quality-gates --skip-build --skip-ctest --skip-cli --skip-python-tools --include-repository-audit
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-repository-audit-next-steps-execution.md
python tools\agentic_design\agentic_toolkit.py validate-docs
```

## Evidence Bundle

- `python -m unittest tests.tools.test_repository_audit`: passed, 10 tests.
- `python -m unittest tests.tools.test_agentic_toolkit`: passed, 19 tests.
- `python tools\repository_audit\repository_audit.py diff --base HEAD~1 --head HEAD --output var\repository-audit\next.diff.json`: passed, 11 changed files, 728 text-line delta, 0 finding delta.
- `python tools\repository_audit\repository_audit.py diff-report --diff var\repository-audit\next.diff.json --output var\repository-audit\next.diff.md`: passed.
- `python tools\repository_audit\repository_audit.py trend --snapshot var\repository-audit\trend-head.snapshot.json --snapshot var\repository-audit\trend-head.snapshot.json --output var\repository-audit\trend-smoke.md`: passed.
- `python tools\agentic_design\agentic_toolkit.py run-quality-gates --skip-build --skip-ctest --skip-cli --skip-python-tools --include-repository-audit`: passed.
- `python tools\repository_audit\repository_audit.py check`: passed with 0 errors and 0 warnings.
- `python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-26-repository-audit-next-steps-execution.md`: passed.
- `python tools\agentic_design\agentic_toolkit.py validate-docs`: passed.

## Residual Risks

- Trend reports initially compare accepted snapshots by metadata and totals;
  deeper time-series storage and charting remain later work.
- Repository audit remains opt-in until more samples prove low false-positive
  risk.
