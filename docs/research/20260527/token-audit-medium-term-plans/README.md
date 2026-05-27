# Token Audit Medium-Term Improvement Plans

Date: 2026-05-27
Status: detailed design, ready for implementation review

## Overview

Three medium-term improvements to the GCS token audit system:

| # | Plan | Goal | Complexity |
|---|------|------|------------|
| 1 | BEI Baseline Calibration | Replace hardcoded thresholds with data-driven percentiles | Medium |
| 2 | Burn Rate Alerts | Predict budget exceedance from cost/time slope | Medium |
| 3 | Cross-Project Dashboard | Multi-project comparison and overview | Low-Medium |

---

## Plan 1: BEI Baseline Calibration

### Problem

Current BEI baselines are hardcoded in `config.yaml`:

```yaml
bei:
  baselines:
    output_per_1M_tokens: 200        # arbitrary
    ideal_cost_per_commit_usd: 0.50  # arbitrary
```

These don't account for:
- Project type (feature work vs bugfix vs docs)
- Historical performance of the specific project
- Model differences (Opus produces different LoC/token than Haiku)

### Design

#### 1.1 Auto-Calibrated Baselines Table

```sql
CREATE TABLE IF NOT EXISTS baselines (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project         TEXT NOT NULL,
    metric          TEXT NOT NULL,       -- output_per_1M_tokens, cost_per_commit, cache_hit_rate, edit_rejection_rate
    p25             REAL,
    p50             REAL,
    p75             REAL,
    sample_size     INTEGER,
    window_days     INTEGER DEFAULT 30,
    updated_at      TEXT DEFAULT (datetime('now')),
    UNIQUE(project, metric, window_days)
);
```

#### 1.2 Calibration Algorithm

```python
def calibrate_baselines(conn, project=None, window_days=30):
    """Compute P25/P50/P75 for each metric from historical sessions."""

    metrics = {
        "output_per_1M_tokens": """
            SELECT (CAST(lines_added + lines_removed AS REAL) * 1000000.0)
                   / NULLIF(total_input_tokens + total_output_tokens, 0) as val
            FROM sessions WHERE total_input_tokens > 0 {project_filter}
        """,
        "cost_per_commit": """
            -- Cost computed at calibration time using default pricing
            ...
        """,
        "cache_hit_rate": """
            SELECT CAST(total_cache_read_tokens AS REAL)
                   / NULLIF(total_cache_read_tokens + total_input_tokens, 0) as val
            FROM sessions WHERE total_input_tokens > 0 {project_filter}
        """,
    }

    for metric, query in metrics.items():
        values = fetch_values(conn, query, project, window_days)
        if len(values) >= 5:  # Minimum sample
            p25, p50, p75 = percentile(values, [25, 50, 75])
            upsert_baseline(conn, project, metric, p25, p50, p75, len(values))
```

Triggered:
- Automatically after each `db import`
- Manually via `python -m tools.token_audit baseline calibrate --project GCS-A`

#### 1.3 BEI Scoring with Calibrated Baselines

```python
def _output_score(self, snapshot, project):
    raw = (snapshot.lines_added + snapshot.lines_removed) * 1e6 / total_tokens

    # Prefer calibrated baseline, fall back to config default
    baseline = self._get_baseline(project, "output_per_1M_tokens")
    if baseline is None:
        baseline = self.baselines.get("output_per_1M_tokens", 200)

    # Score: raw / p75, capped at 1.0
    # P75 means "top quartile performance" → score of 1.0
    return min(raw / baseline.p75, 1.0) if baseline.p75 > 0 else 0.5
```

#### 1.4 Project-Type Classification

Use commit message signals to classify sessions:

| Type | Signal keywords |
|------|----------------|
| `feature` | feat, feature, add, implement, introduce |
| `bugfix` | fix, bug, patch, hotfix, resolve |
| `refactor` | refactor, cleanup, simplify, extract, decouple |
| `docs` | docs, document, readme, guide |
| `chore` | chore, build, ci, release, deps |

Classification stored on session: `project_type TEXT`. Baselines can be computed per-type.

### Files to Change

| File | Change |
|------|--------|
| `schema.sql` | Add `baselines` table, `project_type` to sessions |
| `db.py` | Add `calibrate_baselines()`, `get_baseline()`, `upsert_baseline()` |
| `bei_engine.py` | Use DB baselines with config fallback |
| `cli.py` | Add `baseline calibrate` command |
| `git_linker.py` | Add `classify_project_type()` |
| `config.yaml` | Mark `bei.baselines` as fallback defaults |

---

## Plan 2: Burn Rate Alerts

### Problem

Current alert is a fixed threshold: "session cost exceeds $2.00". This is reactive — by the time it fires, the budget is already blown. No predictive capability.

### Design

#### 2.1 Burn Rate Tracking

During live `watch`, the tracker collects cost at each tick. These data points form a time series:

```
(t0, $0.00), (t1, $0.02), (t2, $0.05), (t3, $0.08), ...
```

The burn rate is the slope of linear regression over the last N points:

```
burn_rate = Δcost / Δtime  (USD/hour)
time_to_budget = (budget - current_cost) / burn_rate
```

#### 2.2 Budget Configuration

```yaml
alerts:
  budgets:
    per_session_usd: 2.00        # Warn when predicted to exceed
    per_session_critical_usd: 5.00  # Critical threshold
    per_day_usd: 10.00
    per_week_usd: 50.00
  burn_rate:
    window_ticks: 10             # Use last 10 ticks for slope
    min_ticks_for_prediction: 5  # Need at least 5 data points
    warning_minutes: 30          # Warn if predicted to exceed in <30 min
    critical_minutes: 10         # Critical if <10 min
```

#### 2.3 Alert Logic

```python
def _check_burn_rate(self, tracker, sid):
    ticks = tracker.recent_cost_ticks(window=self.burn_config["window_ticks"])
    if len(ticks) < self.burn_config["min_ticks_for_prediction"]:
        return []

    # Linear regression on (seconds_elapsed, cost_micro)
    slope_usd_per_second = linear_regression_slope(ticks)
    burn_rate_hourly = slope_usd_per_second * 3600 * 1e6  # micro → USD

    current_cost = ticks[-1].cost_usd_micro / 1e6
    budget = self.budget_config["per_session_usd"]
    remaining = budget - current_cost

    if slope_usd_per_second <= 0:
        return []  # Cost not increasing

    minutes_to_budget = (remaining / (slope_usd_per_second * 1e6)) / 60

    if minutes_to_budget < self.burn_config["critical_minutes"]:
        return [Alert(COST_BURN_CRITICAL, f"Budget exceeded in {minutes_to_budget:.0f}m")]
    elif minutes_to_budget < self.burn_config["warning_minutes"]:
        return [Alert(COST_BURN_WARNING, f"On track to exceed budget in {minutes_to_budget:.0f}m")]

    return []
```

#### 2.4 Cost Tick Storage

Add cost ticks to the in-memory tracker. Each tick records `(timestamp, cumulative_cost_usd_micro)`. Not persisted to DB — only used during live watch.

### Files to Change

| File | Change |
|------|--------|
| `tracker.py` | Add `recent_cost_ticks` ring buffer |
| `alerts.py` | Add `_check_burn_rate` method |
| `config.yaml` | Add `alerts.budgets` and `alerts.burn_rate` sections |

---

## Plan 3: Cross-Project Dashboard

### Problem

The user works across multiple Claude Code projects but the token audit system is project-scoped. No way to compare projects or see total spend.

### Design

#### 3.1 Multi-Project Import

`db import` already supports `--all-projects`. The `project_name` column in `sessions` already tracks which project each session belongs to. No schema change needed.

#### 3.2 Dashboard Command

```bat
# Terminal dashboard
python -m tools.token_audit dashboard

# HTML export
python -m tools.token_audit dashboard --format html --output dashboard.html
```

#### 3.3 Dashboard Layout (Terminal)

```
┌──────────────────────────────────────────────────────────────────┐
│  GCS Token Audit — Cross-Project Dashboard    2026-05-27         │
├──────────────────────────────────────────────────────────────────┤
│  Period: last 30 days    Total cost: $12.45    Total tokens: 8.2M│
├──────────────────────────────────────────────────────────────────┤
│ Project     │Sessions│Tokens  │Cost   │LoC   │BEI  │Trend │Type  │
│─────────────│────────│────────│───────│──────│─────│──────│──────│
│ GCS-A       │   45   │  5.2M  │ $8.20 │12.3K │0.62 │  ↗   │ code │
│ s009        │   12   │  1.8M  │ $2.80 │ 3.1K │0.55 │  →   │ data │
│ Docs        │    8   │  1.2M  │ $1.45 │ 8.5K │0.71 │  ↗   │ docs │
├──────────────────────────────────────────────────────────────────┤
│ TOTALS      │   65   │  8.2M  │$12.45 │23.9K │0.63 │  ↗   │      │
└──────────────────────────────────────────────────────────────────┘

Per-Project Sparklines (7-day BEI):
  GCS-A:  ▁▂█▄▃▅▆  ↑
  s009:   ▃▄▄▅▅▄▄  →
  Docs:   ▂▃▅▆█▇▆  ↑
```

#### 3.4 HTML Dashboard

If `--format html`, generate a self-contained HTML file with:
- Sortable table (JavaScript)
- Mini sparklines (CSS bar charts, no JS dependency needed)
- Color-coded BEI ratings
- Project type distribution pie chart (Unicode block chars)
- Dark theme matching GCS visual tokens

### Files to Change

| File | Change |
|------|--------|
| `cli.py` | Add `dashboard` command |
| `reporter.py` | Add `generate_dashboard()` function |
| `db.py` | Add `get_project_summaries()` aggregation query |

---

## Implementation Sequence

1. **Plan 3 first** (simplest, most visible value): dashboard gives immediate cross-project view
2. **Plan 1 second** (improves BEI accuracy): depends on having enough historical data
3. **Plan 2 third** (most complex): requires live watch infrastructure, ring buffer, linear regression

Estimated effort: 2-3 sessions total.

---

## Dependencies on Current Work

All three plans depend on the short-term improvements just completed:
- Tool call extraction fix → accurate tool counts for project-type classification
- Commit quality signals → project-type classification inputs
- Chapter markers → could be used to show per-chapter cost in dashboard
- Force re-import → needed to backfill historical data for baseline calibration
