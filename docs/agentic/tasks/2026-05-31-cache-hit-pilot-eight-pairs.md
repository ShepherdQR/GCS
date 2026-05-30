---
task_id: 2026-05-31-cache-hit-pilot-eight-pairs
status: complete
request: "Design, execute, summarize, and close eight paired Full/Lite cache-hit experiment tasks with recordable run instructions and durable evidence."
scope: test
risk: medium
owning_agent: task-scoped-session-closer
specialist_agents:
  - gcs-architecture-steward
narrative_lines:
  - "14:primary"
token_budget:
  max_total: 7000000
  budget_consumed: 6960078
affected_contracts:
  - none
affected_paths:
  - docs/agentic/
  - docs/completed-tasks/2026-05-31-cache-hit-pilot-eight-pairs/
  - docs/research/20260530/cache-hit-diagnosis-experiment/
  - docs/reports/token-audit/cache-hit-diagnosis-20260530/
  - tools/token_audit/
required_evidence:
  - validate-task-card
  - validate-completed-task-report
  - score-closure-report
  - experiment-matrix-review
  - experiment-summary-refresh
human_gate_required: false
human_gate_reason: ""
---

# 2026-05-31-cache-hit-pilot-eight-pairs

## Scope

Design and execute eight paired Full/Lite pilot tasks for the cache-hit
diagnosis experiment, define task boundaries that can produce recordable
session-level token metrics, record all run rows without polluting real pilot
evidence with setup overhead, and close the task with durable archive evidence.

## Non-Goals

- Do not change solver runtime semantics.
- Do not redefine architecture contracts in `docs/agentic`.
- Do not record this setup session as a pilot run.
- Do not promote a permanent Full/Lite policy from the pilot without a
  task-class policy review and second-reviewer calibration.

## Context To Read

- `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/experiment-plan.md`
- `docs/reports/token-audit/cache-hit-diagnosis-20260530/first-pass-diagnostic.md`
- `.agents/skills/gcs-token-audit-steward/SKILL.md`
- Owning skill: `task-scoped-session-closer`

## Acceptance Gates

- Eight paired Full/Lite tasks are defined with comparable scope and acceptance gates.
- All eight pairs are recorded in `experiment-runs.csv`.
- Each pair has a stable `task_pair`, lane order, risk level, validation command, and record command template.
- Codex Desktop JSONL token-count telemetry can be recorded without modifying
  historical transcripts or token-audit database rows.
- The setup session is excluded from real pilot evidence.
- Required evidence is produced or skipped with a reason.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-31-cache-hit-pilot-eight-pairs.md
python -m py_compile tools\token_audit\cache_hit_experiment.py
python tools\token_audit\cache_hit_experiment.py record-jsonl --help
python tools\token_audit\cache_hit_experiment.py summarize --runs docs\research\20260530\cache-hit-diagnosis-experiment\cache-hit-rate-full-lite-pilot\experiment-runs.csv --output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.md --json-output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.json
```

## Evidence Bundle

- `python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-31-cache-hit-pilot-eight-pairs.md` passed.
- `python -m py_compile tools\token_audit\cache_hit_experiment.py` passed.
- `python tools\token_audit\cache_hit_experiment.py summarize --runs docs\research\20260530\cache-hit-diagnosis-experiment\cache-hit-rate-full-lite-pilot\experiment-runs.csv --output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.md --json-output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.json` passed.
- `python tools\agentic_design\agentic_toolkit.py validate-completed-task-report docs\completed-tasks\2026-05-31-cache-hit-pilot-eight-pairs\README.md` passed.
- `python tools\agentic_design\agentic_toolkit.py score-closure-report docs\completed-tasks\2026-05-31-cache-hit-pilot-eight-pairs\README.md --min-score 30` passed with closure score `34/40`.
- `git diff --check` over the scoped cache-hit closure files passed.
- Eight paired Full/Lite pilot tasks were defined in `docs/research/20260530/cache-hit-diagnosis-experiment/cache-hit-rate-full-lite-pilot/pilot-runbook-8-pairs.md`.
- `python tools\token_audit\cache_hit_experiment.py record-jsonl --help` passed.
- All 16 dedicated run rows were recorded from Codex Desktop JSONL `token_count` telemetry.
- Final pilot result: `8 / 8` pairs complete; aggregate classification `redundant-overhead`.
- Aggregate Full vs Lite metrics: Lite saved `53.1%` input tokens, average audit score dropped `4.3%`, average BEI proxy dropped `8.3%`, Full validation pass rate was `100%`, Lite validation pass rate was `87.5%`, and Lite recorded one defect/reopen.
- Pair-level classification counts: `3` redundant-overhead, `1` healthy-institutionalization, `4` mixed-or-inconclusive.
- `python-gui-smoke-1-lite` is the key guardrail case: Lite saved tokens but failed validation because the active Python environment lacked `matplotlib`.
- `docs/completed-tasks/2026-05-31-cache-hit-pilot-eight-pairs/README.md` records closure decisions, residual risks, and follow-up.

## Residual Risks

- Manual audit scoring remains subjective until a second reviewer samples rows.
- BEI values are experiment-only proxies and should not become hard policy gates
  before cost/BEI calibration.
- The pilot supports a task-class split review, not a global Lite default.
- GUI/environment-sensitive work still needs Full-lane context unless future
  Lite evidence closes the validation gap.
