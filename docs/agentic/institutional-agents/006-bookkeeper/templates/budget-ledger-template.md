# Budget Ledger Template

Period: `<session | day | week | month | milestone>`
Date range: `<YYYY-MM-DD> to <YYYY-MM-DD>`
Ledger prepared by: `bookkeeper`
Date prepared: `<YYYY-MM-DD>`

## Scope

Sessions / tasks under review:

| Session ID | Date | Task | Primary artifact(s) |
| --- | --- | --- | --- |
| | | | |

## Token / Cost Summary

| Metric | Value | Source | Caveat |
| --- | ---: | --- | --- |
| Total tokens consumed | | `tools/token_audit/` | |
| Estimated USD cost | | cost model | Directional only; model pricing may vary |
| Sessions included | | | |
| Model version(s) | | | Cross-version comparison invalid unless noted |

## Artifact Inventory

| Artifact | Type | Path | Session | Notes |
| --- | --- | --- | --- | --- |
| | commit / doc / task-archive / example / generated | | | |

Artifact counts by type:

| Type | Count |
| --- | ---: |
| Commits | |
| Task archives | |
| Architecture docs | |
| Agentic docs | |
| Examples | |
| Generated artifacts | |
| Other | |

## Efficiency Metrics

| Metric | Value | Baseline (if any) | Direction |
| --- | ---: | ---: | --- |
| BEI score (avg) | | | |
| BEI score (median) | | | |
| Cost per commit | | | |
| Cost per task archive | | | |
| Tokens per artifact | | | |
| Commits per session | | | |

**Baseline status**: `none` / `emerging (2-5 periods)` / `established (6+ periods)`

If baseline is `none`, skip trend section and state: "Insufficient data for
trend analysis. This ledger serves as the first baseline data point."

## Trend Direction

Only populate if baseline exists (2+ comparable periods).

| Metric | Prior period | This period | Delta | Direction |
| --- | ---: | ---: | ---: | --- |
| | | | | ↑ / → / ↓ |

Trend narrative (2-3 sentences):

## Anomalies

| Session / task | Anomaly | Investigation notes | Severity |
| --- | --- | --- | --- |
| | Token count disproportionate to output | | low / medium / high |
| | Unusually high cost per commit | | |
| | Missing token data | | |

## Recommendations

1.
2.
3.

## Caveats

- All USD estimates are directional. Model pricing changes, batch discounts,
  and caching behavior are not accounted for.
- BEI scores are advisory and not calibrated as quality gates.
- Cross-model-version cost comparisons are marked where applicable.
- Sessions with missing token data are excluded from totals (list in anomalies).
