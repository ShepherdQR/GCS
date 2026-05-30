---
task_id: 2026-05-30-cache-hit-experiment-implementation
status: complete
request: "Implement a lightweight cache-hit Full/Lite experiment runner that reads token-audit SQLite telemetry, records pilot runs, summarizes Full vs Lite deltas, and works without token_audit CLI optional dependencies."
scope: tool
risk: medium
owning_agent: task-scoped-session-closer
specialist_agents:
  - gcs-architecture-steward
narrative_lines:
  - "14:primary"
token_budget:
  max_total: 500000
  budget_consumed: 0
affected_contracts:
  - none
affected_paths:
  - docs/agentic/
  - docs/research/20260530/cache-hit-diagnosis-experiment/
  - docs/reports/token-audit/cache-hit-diagnosis-20260530/
  - tools/token_audit/
required_evidence:
  - validate-task-card
  - py-compile
  - experiment-tool-smoke
  - completed-task-report
human_gate_required: false
human_gate_reason: ""
---

# 2026-05-30-cache-hit-experiment-implementation

## Scope

Implement the first executable support slice for the cache-hit diagnosis
experiment: a stdlib-only runner that can inspect token-audit SQLite telemetry,
append/validate Full-vs-Lite pilot run rows, and summarize deltas without using
the currently dependency-blocked `python -m tools.token_audit` CLI.

## Non-Goals

- Do not change solver runtime semantics.
- Do not redefine architecture contracts in `docs/agentic`.
- Do not modify historical JSONL transcripts.
- Do not modify token-audit database rows.
- Do not promote a permanent Full/Lite policy before paired-run evidence exists.

## Context To Read

- `docs/research/20260530/cache-hit-diagnosis-experiment/README.md`
- `docs/reports/token-audit/cache-hit-diagnosis-20260530/baseline.md`
- `docs/reports/token-audit/cache-hit-diagnosis-20260530/first-pass-diagnostic.md`
- `tools/token_audit/schema.sql`
- Owning skill: `task-scoped-session-closer`

## Acceptance Gates

- A stdlib-only experiment runner exists under `tools/token_audit/`.
- The runner can inspect the current baseline DB.
- The runner can validate or append CSV records without requiring PyYAML or click.
- The runner can summarize Full/Lite deltas into Markdown and JSON.
- Required evidence is produced or skipped with a reason.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-30-cache-hit-experiment-implementation.md
python -m py_compile tools\token_audit\cache_hit_experiment.py
python tools\token_audit\cache_hit_experiment.py inspect-db --format json
python tools\token_audit\cache_hit_experiment.py summarize --runs docs\research\20260530\cache-hit-diagnosis-experiment\experiment-runs.csv --output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.md --json-output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.json
```

## Evidence Bundle

- `python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-30-cache-hit-experiment-implementation.md` passed.
- `python -m py_compile tools\token_audit\cache_hit_experiment.py` passed.
- `python tools\token_audit\cache_hit_experiment.py inspect-db --format json` passed: 38 sessions, 1210 turns, 1548 tool calls, legacy cache hit 98.67%, estimated raw hit 99.55%.
- `python tools\token_audit\cache_hit_experiment.py list-sessions --limit 3 --format json` passed.
- `python tools\token_audit\cache_hit_experiment.py summarize --runs docs\research\20260530\cache-hit-diagnosis-experiment\experiment-runs.csv --output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.md --json-output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.json` passed.
- Temporary Full/Lite record smoke in `%TEMP%\cache-hit-runs-smoke.csv` passed and produced a complete pair classification.

## Residual Risks

- The existing `python -m tools.token_audit` CLI still requires missing optional
  dependencies in this runtime (`yaml` / `click`).
- The experiment remains a pilot until 6 to 8 paired Full/Lite runs are recorded.
- Stored USD cost is not a reliable decision signal until normalized.
