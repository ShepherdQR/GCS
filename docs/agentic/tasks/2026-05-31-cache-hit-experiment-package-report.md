---
task_id: 2026-05-31-cache-hit-experiment-package-report
status: complete
request: "Package the cache-hit-rate experiment into a dedicated subfolder under the experiment directory and add a detailed experiment report."
scope: docs
risk: low
owning_agent: task-scoped-session-closer
specialist_agents:
  - none
narrative_lines:
  - "14:primary"
token_budget:
  max_total: 200000
  budget_consumed: 0
affected_contracts:
  - none
affected_paths:
  - docs/agentic/
  - docs/research/20260530/cache-hit-diagnosis-experiment/
  - docs/reports/token-audit/cache-hit-diagnosis-20260530/
  - tools/token_audit/cache_hit_experiment.py
required_evidence:
  - validate-task-card
  - cache-hit-summary-refresh
  - scoped-diff-check
human_gate_required: false
human_gate_reason: ""
---

# 2026-05-31-cache-hit-experiment-package-report

## Scope

Package the completed cache-hit-rate Full/Lite pilot into a dedicated
subfolder under `docs/research/20260530/cache-hit-diagnosis-experiment/`, add a
detailed experiment report, keep a root index, and update live references and
tool defaults to the new data path.

## Non-Goals

- Do not change solver runtime semantics.
- Do not redefine architecture contracts in `docs/agentic`.
- Do not change historical JSONL transcripts or token-audit database rows.
- Do not reinterpret the pilot into a global Lite policy.

## Context To Read

- `docs/research/20260530/cache-hit-diagnosis-experiment/`
- `docs/reports/token-audit/cache-hit-diagnosis-20260530/pilot-summary.md`
- `docs/completed-tasks/2026-05-31-cache-hit-pilot-eight-pairs/README.md`
- Owning skill: `task-scoped-session-closer`
- Token-audit context: `.agents/skills/gcs-token-audit-steward/SKILL.md`

## Acceptance Gates

- The experiment is in a dedicated subfolder under the experiment directory.
- The subfolder has a detailed report covering experiment process,
  implementation process, key data, and conclusions.
- The root experiment directory has a short navigation README.
- The cache-hit summary command works against the moved `experiment-runs.csv`.
- Required evidence is produced or skipped with a reason.

## Verification Plan

```bat
python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-31-cache-hit-experiment-package-report.md
python tools\token_audit\cache_hit_experiment.py summarize --runs docs\research\20260530\cache-hit-diagnosis-experiment\cache-hit-rate-full-lite-pilot\experiment-runs.csv --output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.md --json-output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.json
git diff --check -- docs\agentic\tasks\2026-05-31-cache-hit-experiment-package-report.md docs\research\20260530\cache-hit-diagnosis-experiment docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.md docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.json tools\token_audit\cache_hit_experiment.py
```

## Evidence Bundle

- `python tools\token_audit\cache_hit_experiment.py summarize --runs docs\research\20260530\cache-hit-diagnosis-experiment\cache-hit-rate-full-lite-pilot\experiment-runs.csv --output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.md --json-output docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.json` passed.
- `python -m py_compile tools\token_audit\cache_hit_experiment.py` passed.
- Initial `validate-task-card` failed because the generated card used a non-`.codex` owner and `00:primary`; the card was corrected to `task-scoped-session-closer` and `14:primary`.
- `python tools\agentic_design\agentic_toolkit.py validate-task-card docs\agentic\tasks\2026-05-31-cache-hit-experiment-package-report.md` passed after correction.
- `git diff --check -- docs\agentic\tasks\2026-05-31-cache-hit-experiment-package-report.md docs\research\20260530\cache-hit-diagnosis-experiment docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.md docs\reports\token-audit\cache-hit-diagnosis-20260530\pilot-summary.json tools\token_audit\cache_hit_experiment.py` passed.
- `python tools\agentic_design\agentic_toolkit.py validate-docs` passed.

## Residual Risks

- Historical baseline JSON may still contain old path strings as captured
  provenance; those are not rewritten.
- Some moved run artifacts include command evidence from the original run time;
  path references inside command snippets are historical unless explicitly
  updated by this packaging task.
