# Night-Watch Calibration Run — 2026-05-30

## What is a night-watch run?

A night-watch run is a **read-only patrol** of project health executed by the
night-watch institutional agent (`gcs-night-watch-steward`). It inspects CI
status, quality gates, stale tasks, uncommitted work, documentation drift, and
repository hygiene, then writes a dated report that humans can review in the
morning.

The agent's guiding principle: **observe and report, never mutate.** It does
not commit, push, merge, delete branches, or modify source files. Its only
writes are into `docs/agentic/nightly-runs/YYYY-MM-DD/`.

## What does this calibration run cover?

This is the **first real exercise** of the night-watch institutional agent.
The run is a calibration pass — meaning:

- We execute the core patrol checks to verify they work in the local environment.
- We note what is signal vs. noise, what tools produce useful output, and what
  should be added or removed from future runs.
- We do NOT perform automated repairs. The first two runs are calibration-only
  per the agent's guardrails.

Checks executed in this run:

| # | Check | Tool |
|---|-------|------|
| 1 | Architecture doc validation | `agentic_toolkit.py validate-docs` |
| 2 | Stale worktree detection | `git worktree list` |
| 3 | Repository dirty state | `git status` |
| 4 | Completed-task archive completeness | Manual sampling + glob scan |
| 5 | Agent definition file count and health | `ls .claude/agents/` + line counts |
| 6 | Night-watch agent output template | Read `.claude/agents/night-watch.md` |
| 7 | Institutional agent directory structure | Directory listing |

## Output Files

| File | Purpose |
|------|---------|
| `README.md` | This file — run overview and index |
| `findings.md` | Detailed findings with PASS/WARN/FAIL classification |

## Guardrails

- No commits, pushes, merges, or branch deletions.
- No modifications to source files outside this run directory.
- Findings are classified before any repair is recommended.
- All repair suggestions require human action.

## Residual Uncertainty

This is a calibration run. The set of checks is deliberately narrow. Future
runs should expand coverage to include:
- `validate-inventory` and `validate-skills` (tools exist per the nightly
  immune diagnostics spec but were not tested here)
- Scene corpus health
- Focused quality gate (skipping full builds)
- Cross-run trend detection (needs 3+ runs)
