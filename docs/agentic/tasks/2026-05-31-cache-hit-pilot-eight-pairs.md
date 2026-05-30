---
task_id: 2026-05-31-cache-hit-pilot-eight-pairs
status: draft
request: "Design eight paired Full/Lite cache-hit experiment tasks and start the real pilot execution with recordable run instructions."
scope: test
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
required_evidence:
  - validate-task-card
  - experiment-matrix-review
  - experiment-summary-refresh
human_gate_required: false
human_gate_reason: ""
---

# 2026-05-31-cache-hit-pilot-eight-pairs

## Scope

Design eight paired Full/Lite pilot tasks for the cache-hit diagnosis
experiment, define task boundaries that can produce recordable session-level
token metrics, and prepare the first execution slice without polluting real
pilot rows with setup overhead.

## Non-Goals

- Do not change solver runtime semantics.
- Do not redefine architecture contracts in `docs/agentic`.
- Do not record this setup session as a pilot run.
- Do not promote a permanent Full/Lite policy before paired-run evidence exists.

## Context To Read

- `docs/research/20260530/cache-hit-diagnosis-experiment/README.md`
- `docs/reports/token-audit/cache-hit-diagnosis-20260530/first-pass-diagnostic.md`
- `.agents/skills/gcs-token-audit-steward/SKILL.md`
- Owning skill: `task-scoped-session-closer`

## Acceptance Gates

- Eight paired Full/Lite tasks are defined with comparable scope and acceptance gates.
- Each pair has a stable `task_pair`, lane order, risk level, validation command, and record command template.
- The setup session is excluded from real pilot evidence.
- Required evidence is produced or skipped with a reason.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-31-cache-hit-pilot-eight-pairs.md
python tools\token_audit\cache_hit_experiment.py summarize --runs docs\research\20260530\cache-hit-diagnosis-experiment\experiment-runs.csv --output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.md --json-output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.json
```

## Evidence Bundle

- `python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-31-cache-hit-pilot-eight-pairs.md` passed.
- `python -m py_compile tools\token_audit\cache_hit_experiment.py` passed.
- `python tools\token_audit\cache_hit_experiment.py summarize --runs docs\research\20260530\cache-hit-diagnosis-experiment\experiment-runs.csv --output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.md --json-output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.json` passed; no real pilot rows recorded yet.
- Eight paired Full/Lite pilot tasks were defined in `docs/research/20260530/cache-hit-diagnosis-experiment/pilot-runbook-8-pairs.md`.

## Residual Risks

- Real pilot rows require separate task sessions or cleanly bounded task-only
  sessions; this planning/setup task is intentionally not recorded as a run.
- Manual audit scoring remains subjective until a second reviewer samples rows.
