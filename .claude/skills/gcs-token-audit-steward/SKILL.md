---
name: gcs-token-audit-steward
description: Token audit, cost tracking, and session efficiency analysis for GCS. Invoke when work touches AI session token consumption, cost modeling, BEI (Benefit-Efficiency Index) scoring, session transcript parsing, database import/export, daily/weekly/monthly trend reports, or token budget governance.
---

# GCS Token Audit Steward

## Start Here

Use this skill for AI session token and cost tracking. The token audit system
monitors Claude Code sessions, calculates costs, computes benefit-efficiency
scores, and generates trend reports — turning raw token consumption into
reviewable engineering economics.

## Workflow

1. **Watch** an active session with real-time token/cost tracking and burn rate alerts.
2. **Import** historical sessions from JSONL transcripts into the database.
3. **Report** on a single session or time range — includes one-sentence efficiency
   analysis comparing LoC/1M tokens and cache hit rate against calibrated P50/P75
   baselines.
4. **Calibrate** baselines from historical data for data-driven BEI scoring.
5. **Dashboard** cross-project comparison with per-project metrics.
6. **Trend** analysis over days/weeks/months.
7. **Configure** BEI weights, alert thresholds, and pricing.

## Command Reference

```bat
# Watch an active session in real time
python -m tools.token_audit watch

# Import historical sessions
python -m tools.token_audit db import --all
python -m tools.token_audit db import --since 2026-05-01
python -m tools.token_audit db import --force  # re-import existing sessions

# Generate session report (includes baseline efficiency analysis)
python -m tools.token_audit report --session <id>
python -m tools.token_audit report --this-week
python -m tools.token_audit report --this-month
python -m tools.token_audit report --pricing anthropic  # switch pricing model

# Baseline calibration
python -m tools.token_audit baseline calibrate
python -m tools.token_audit baseline calibrate --project GCS-A --days 30

# Cross-project dashboard
python -m tools.token_audit dashboard
python -m tools.token_audit dashboard --format html -o dashboard.html

# Trend analysis
python -m tools.token_audit trend --days 30

# v2 Token economic diagnostics
python -m tools.token_audit diagnose --session <id>
python -m tools.token_audit cache-health --days 30

# Database statistics
python -m tools.token_audit db stats

# Database maintenance
python -m tools.token_audit db vacuum

# Configuration
python -m tools.token_audit config show
python -m tools.token_audit config set bei.weights.output 0.35
```

## Own

- Token consumption database and import pipeline.
- Cost modeling with model-specific pricing.
- BEI (Benefit-Efficiency Index) scoring.
- Session-level, daily, weekly, and monthly reporting.
- Alert thresholds for cost anomalies.
- Git-linked session context enrichment.

## Refuse

- Modifying session transcripts or JSONL files.
- Claiming exact cost when model pricing is approximate.
- Promoting BEI thresholds as quality gates without calibration.

## Guardrails

- Token telemetry from JSONL is the source of truth.
- Cost estimates are directional; mark uncertain pricing explicitly.
- BEI scores are advisory, not quality gates.
- Do not delete or modify historical session data.

## Required Output

Return a structured token report with:
- session identification and duration;
- input/output/cache token breakdown;
- estimated cost in USD;
- one-sentence efficiency analysis vs calibrated baseline (P50/P75);
- BEI composite and dimension scores;
- tools, skills, and edits breakdown;
- trend comparison (when applicable).

## Claude Code Integration

When invoked:
- Use `Bash` to run `python -m tools.token_audit` commands.
- Use `Read` to inspect session JSONL transcripts for debugging.
- Use `Write` to save generated reports to `docs/reports/token-audit/`.
- Integrate with `task-scoped-session-closer` to include token summaries
  in completed-task archives.
- Use `Bash` with `python -m tools.token_audit db import` after each
  significant session to keep the database current.
