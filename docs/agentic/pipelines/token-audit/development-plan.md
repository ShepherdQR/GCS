# Token Audit Pipeline — Development Plan

**Status**: proposed (partial tooling exists)
**Priority**: P3
**Owner**: gcs-token-audit-steward

## Purpose

Track AI session token consumption and costs, compute Benefit-Efficiency Index
(BEI) scores, generate daily/weekly/monthly trend reports for budget governance.

## What's Partially Implemented

- `tools/token_audit/` — existing token audit tools and database

## Toolchain Needed

### `tools/solver_testing/pipelines/token_audit.py`

```
TokenAuditPipeline
├── import_session_transcripts(path) → list[SessionRecord]
│   └── parse JSONL transcripts, extract token counts
├── compute_session_metrics(record) → SessionMetrics
│   ├── total_tokens, input_tokens, output_tokens
│   ├── cache_hit_rate
│   ├── tool_call_count
│   └── estimated_cost
├── compute_bei(session) → float
│   └── benefit / cost ratio based on outcomes
├── aggregate_daily(records) → DailyReport
├── aggregate_weekly(records) → WeeklyReport
├── aggregate_monthly(records) → MonthlyReport
├── detect_anomalies(trend) → list[Anomaly]
│   └── sessions with unusually high token/cost
└── generate_trend_report(records, period) → dict
```

### CLI
```bash
python tools/solver_testing/pipelines/token_audit.py \
  --transcripts .claude/transcripts/ \
  --period weekly \
  --output token_report.json
```

## Implementation Plan

| Step | What | Est. |
|------|------|------|
| 1 | `token_audit.py` — transcript parser + metrics | 100行 |
| 2 | BEI computation | 50行 |
| 3 | Trend aggregation (daily/weekly/monthly) | 100行 |
| 4 | CLI + report | 50行 |

**Total**: ~300 lines
