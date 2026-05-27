# Token Billing Roadmap — Short / Medium / Long-Term Plans

Date: 2026-05-28
Status: planning document, updated after all prior billing work completed

## Completed (Sessions 2026-05-27 → 2026-05-28)

| # | Feature | Type | Session |
|---|---------|------|---------|
| 1 | Pricing updated to latest official rates (Opus $5/$25, Sonnet $3/$15, Haiku $1/$5, DeepSeek $0.435/$0.87) | fix | 05-27 |
| 2 | Cost computed at report time from raw tokens (not pre-stored) | arch | 05-27 |
| 3 | DeepSeek V4 Pro as default report pricing | feature | 05-27 |
| 4 | BEI quality dimension with commit message signals (conventional/semantic/architecture) | feature | 05-27 |
| 5 | Chapter segmentation from CCD mark_chapter markers | feature | 05-27 |
| 6 | Cross-project dashboard (terminal/HTML/markdown) | feature | 05-27 |
| 7 | BEI baseline calibration (P25/P50/P75 from historical data) | feature | 05-27 |
| 8 | Burn rate alerts (linear regression prediction of budget exceedance) | feature | 05-27 |
| 9 | One-sentence efficiency analysis vs calibrated baselines in reports | feature | 05-27 |
| 10 | Multi-model cost comparison (--compare: DeepSeek vs Sonnet vs Opus) | feature | 05-28 |
| 11 | Batch API pricing support (--batch, 50% off input/output) | feature | 05-28 |
| 12 | Cache TTL differentiation (--cache-ttl 5min/1hour) | feature | 05-28 |
| 13 | Daily/weekly budget tracking in dashboard | feature | 05-28 |
| 14 | Monthly cost prediction in dashboard | feature | 05-28 |
| 15 | Model routing optimization (routing command) | feature | 05-28 |

---

## Short-Term (next 1-3 sessions)

### S1. Per-Chapter Cost Breakdown
**Goal**: Chapters table exists but reports don't show per-chapter token/cost.
- Parse token usage between chapter markers during import
- Fill `chapters.input_tokens`/`output_tokens`/`cache_read_tokens` columns (already in schema)
- Show per-chapter cost in session report and chapter breakdown table
- **Files**: `cli.py:_import_session`, `reporter.py:_session_report_markdown`
- **Effort**: ~80 lines

### S2. Config-Driven Comparison Models
**Goal**: `CostModel.COMPARISON_MODELS` is hardcoded. Move to config.yaml.
- Add `report.comparison_models` list in config.yaml
- Load in CostModel.__init__, fall back to hardcoded defaults
- Add `config set report.comparison_models` support (list-type values)
- **Files**: `config.yaml`, `cost_model.py`, `cli.py`
- **Effort**: ~40 lines

### S3. Session Output Summary Integration
**Goal**: The linter added a `snap` command for quick DB-only session summary. Enhance it to include token/cost breakdown without JSONL scanning.
- Add token stats, cost, cache rate, BEI to snap output
- Use as lightweight alternative to full `report` for quick status checks
- **Files**: `cli.py` (snap command area)
- **Effort**: ~50 lines

### S4. Routing Enhancement — Per-Tool-Type Classification
**Goal**: Current routing uses `edit_ratio` as proxy. Join `tool_calls` table for accurate counts.
- Count Read/Grep/Glob vs Edit/Write tools per session
- Improve pattern classification accuracy
- Add tool-type breakdown to routing report
- **Files**: `db.py:get_routing_candidates`
- **Effort**: ~60 lines

### S5. Report — Cost Savings Callout
**Goal**: When cache hit rate > 90%, show estimated savings from caching.
- Compute: `cache_read_tokens × (input_rate - cache_read_rate)` = savings from cache
- Add a "Cache Savings" line to the Token & Cost Summary table
- **Files**: `reporter.py`, `cost_model.py`
- **Effort**: ~30 lines

---

## Medium-Term (next 3-10 sessions)

### M1. Automated Session Cost Anomaly Detection
**Goal**: Beyond fixed thresholds — detect sessions that are statistical outliers.
- Compute z-score of session cost vs 30-day distribution
- Flag sessions >2σ from mean as anomalies
- Daily scan via cron or on-demand via `audit anomalies` command
- Add `anomaly_log` table for persistent tracking
- **Files**: `schema.sql`, `db.py`, `alerts.py`, `cli.py`
- **Effort**: ~200 lines, 1 new table

### M2. Provider Cost Comparison (Anthropic vs DeepSeek vs OpenRouter)
**Goal**: Extend multi-model comparison to provider-level: what if ALL sessions used provider X?
- Dashboard section: "If all sessions used DeepSeek: $X | If all used Sonnet: $Y"
- Historical projection: compute counterfactual costs for past 30/90 days
- Add `--provider` flag to dashboard
- **Files**: `cost_model.py`, `reporter.py`, `db.py`
- **Effort**: ~150 lines

### M3. Token Budget Governance View
**Goal**: A dashboard mode for budget committee / team lead review.
- Monthly budget vs actual with burn-down chart
- Per-project allocation vs consumption
- Alert digest: sessions that triggered cost alerts
- HTML export with print-friendly layout
- **Files**: `reporter.py` (new renderer), `cli.py`
- **Effort**: ~250 lines

### M4. Trend Report Enhancement — Week-over-Week / Month-over-Month
**Goal**: Current trend shows absolute values. Add delta columns.
- WoW/MoM change percentages for tokens, cost, LoC, BEI
- Color-coded direction indicators
- Rolling 7-day and 30-day averages
- **Files**: `reporter.py:_trend_report_markdown`, `db.py`
- **Effort**: ~120 lines

### M5. Token Efficiency Leaderboard
**Goal**: Rank sessions by efficiency metrics within a project or across all projects.
- Top 10 sessions by LoC/1M tokens, lowest cost/commit, highest cache rate
- Bottom 10 sessions for improvement focus
- Filterable by project, date range, model
- **Files**: `db.py`, `reporter.py`, `cli.py`
- **Effort**: ~150 lines

---

## Long-Term (vision, 10+ sessions out)

### L1. Predictive Model Selection
**Goal**: ML-based recommendation of which model to use for a given task type.
- Train on historical session data: tool pattern + output complexity → optimal model
- Real-time suggestion during session: "This looks like a reading-heavy session, consider Haiku"
- Integrate with Claude Code hooks or status line
- **Dependencies**: M1 (anomaly detection patterns), S4 (tool-type classification)
- **Effort**: ~500 lines + training pipeline

### L2. Feature/Module Cost Attribution
**Goal**: Attribute token costs to specific features or modules being worked on.
- Parse commit messages and changed file paths to infer feature area
- Tag sessions with feature labels
- Aggregate cost per feature/module over time
- Report: "Feature X cost $12.30 in AI tokens across 15 sessions"
- **Dependencies**: git_linker enhancements, session tagging
- **Effort**: ~300 lines + tagging system

### L3. Sprint/Project Token Budgeting
**Goal**: Set token budgets per sprint or project, track burn-down.
- Budget allocation: feature team A gets $50/week, team B gets $30/week
- Burndown chart: budget remaining vs sprint days remaining
- Integration with project management tools (optional)
- **Dependencies**: M3 (budget governance)
- **Effort**: ~350 lines

### L4. CI/CD Token Cost Tracking
**Goal**: Track token costs from automated CI/CD agents (code review bots, test generators).
- Tag automated sessions vs human-driven sessions
- Separate cost tracking for CI pipeline
- Per-PR token cost summary
- **Dependencies**: Session classification
- **Effort**: ~200 lines

### L5. Real-Time Token Cost Overlay
**Goal**: Live token cost display in IDE or terminal during Claude Code sessions.
- Status bar widget showing session cost, burn rate, time-to-budget
- Integration with Claude Code status line hooks
- Minimizable overlay with color-coded budget status
- **Dependencies**: Burn rate alerts (already implemented)
- **Effort**: ~200 lines + UI integration

### L6. Token Economics Research Reports
**Goal**: Quarterly or per-milestone research reports on AI cost efficiency.
- Automated report generation: cost trends, efficiency evolution, model migration impact
- Comparison: pre-AI vs AI-assisted development cost (using ROI config)
- Executive summary with key charts
- PDF export via HTML→PDF pipeline
- **Dependencies**: M2, M4
- **Effort**: ~300 lines + report templates

---

## Priority Matrix

| Impact \ Effort | Low (~50L) | Medium (~150L) | High (~300L+) |
|-----------------|------------|----------------|---------------|
| **High** | S1 (chapter cost), S5 (cache savings) | M4 (WoW/MoM trends), M5 (leaderboard) | M3 (budget governance), L2 (feature attribution) |
| **Medium** | S2 (config comparison), S4 (tool-type routing) | M1 (anomaly detection), M2 (provider comp) | L3 (sprint budgeting), L5 (real-time overlay) |
| **Low** | S3 (snap enhancement) | — | L1 (predictive ML), L6 (research reports) |

## Recommended Next Session

Based on impact/effort and dependency chain:
1. **S5** (Cache savings callout) — 30 lines, immediate visible value
2. **S1** (Per-chapter cost) — 80 lines, fills existing schema gap
3. **M4** (WoW/MoM trends) — 120 lines, dashboard enhancement
4. **M2** (Provider comparison) — 150 lines, strategic value
