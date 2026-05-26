# GCS Session Efficiency Report

Schema: `gcs-agentic-session-efficiency-0.1`
Tool: `0.1`
Records: `1`
Token-known records: `0`
Average outcome score: `0.926`

## Session Records

| Task | Class | Tokens | Confidence | Artifacts | Checks | Closure | Outcome | Value/1k | Net |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-05-26-repository-audit-plan-execution | implementation | n/a | unknown | 21 | 11/11 | 33/40 | 0.926 | n/a | n/a |

## Interpretation Rules

- Records with unknown token telemetry participate in outcome reporting but not value-per-token aggregates.
- Scores compare best within similar task classes; they are not a global leaderboard.
- Repository-audit deltas and closure evidence should be reviewed alongside any token metric.

## Reproduction

```bat
python tools\session_efficiency\session_efficiency.py report --record docs\reports\session-efficiency\2026-05-26\session-efficiency.json --output docs\reports\session-efficiency\2026-05-26\README.md
```
