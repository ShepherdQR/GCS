# GCS Token Economic Evaluation System — Complete Roadmap

**Date**: 2026-05-28
**Status**: v2 core delivered (Phase 0–5); S1–S4, M1–M4, L1–L4 planned
**Baseline**: 4 commits pushed, 41 tests passing, 8 modules, CLI operational
**Depends on**: [Unified Evaluation System Design](token-economics-unified-evaluation-system-2026-05-28.md), [Execution Plan](token-economics-execution-plan-2026-05-28.md)

---

## Executive Summary

The v2 token economic evaluation system is operational: 13 derived metrics (M1–M13), 4 composite indices (CI-1 through CI-4), 8-category workload classification, 3D cache health diagnosis, 7 decision rules, and CLI tools (`diagnose`, `cache-health`). Five integration gaps were identified during post-delivery audit — these form the short-term plan. Medium-term work focuses on calibration and operational rhythm. Long-term work addresses accuracy limitations in the current estimation-based approach.

---

## Current State Audit

### Delivered (v2 Core)

| Module | Status | Tests | Description |
|--------|--------|-------|-------------|
| `metrics_engine.py` | Done | 30 | M1–M13 computation, DeepSeek fallback, RawTelemetry bridge |
| `composite_indices.py` | Done | 0 | CI-1–CI-4, workload classification, 3D cache health |
| `decision_engine.py` | Done | 0 | D1–D7 rules with severity and fix suggestions |
| `reporter.py` (diagnostic) | Done | 0 | `generate_session_diagnostic_card()` |
| `cli.py` (v2 commands) | Done | 0 | `diagnose`, `cache-health` commands |
| `alerts.py` (v2 types) | Done | 0 | 7 new AlertType enum values |
| `db.py` (migration) | Done | 0 | 15 v2 columns, conditional migration |
| `parser.py` (v2 fields) | Done | 11 | `cache_hit_rate_raw`, `uncached_input_tokens`, 8 SessionSnapshot fields |
| `schema.sql` | Done | — | v2 columns in both tables |

### Integration Gaps (Discovered 2026-05-28)

| # | Gap | Impact | Severity |
|---|-----|--------|----------|
| G1 | `upsert_daily_summary()` doesn't populate v2 fields | ATEI trend always 0; D6 rule never fires; `cache-health` aggregate shows no history | HIGH |
| G2 | `BEIEngine._efficiency_score()` uses naive `cache_hit_rate` | BEI scores don't reflect write-premium economics or CWAR; "high efficiency" BEI possible with wasteful caching | MEDIUM |
| G3 | `generate_session_report()` doesn't embed diagnostic card | Session reports lack v2 metrics; completed-task archives missing cache health data | MEDIUM |
| G4 | `DecisionEngine` not bridged to `AlertEngine` | v2 alerts (D1–D7) don't flow through existing alert pipeline; no DB persistence, no cooldown | MEDIUM |
| G5 | `config.yaml` missing v2 thresholds | CWAR break-even, TLR ranges, VCR targets hardcoded; no operator tuning without code change | LOW |

---

## Short-Term Plan (S1–S4): Integration Completion

**Timeline**: 1–2 weeks
**Goal**: Close all integration gaps. The v2 system becomes fully operational end-to-end.

### S1: Daily Summary v2 Population (G1)

**Problem**: `upsert_daily_summary()` in `db.py` only populates v1 fields (`avg_cache_hit_rate`, `avg_bei_composite`). The 6 new columns (`atei`, `avg_hr_effective`, `avg_cwar`, `total_staleness_events`, `avg_sclor`, `avg_tlr`) are always 0/NULL. This means:
- `cache-health` CLI shows state distribution but no trend
- D6 (ATEI decline) never triggers because historical ATEI is always 0
- Weekly audit can't show efficiency trends

**Design**: Extend `upsert_daily_summary()` to compute v2 aggregates from session-level derived metrics.

```python
def upsert_daily_summary(conn, date: str) -> None:
    # ... existing v1 logic ...

    # v2: Compute derived metrics for all sessions on this date
    from tools.token_audit.metrics_engine import RawTelemetry, MetricsEngine, CACHEABLE_PREFIX_ESTIMATE
    from tools.token_audit.composite_indices import CompositeIndexEngine

    engine = MetricsEngine()
    cie = CompositeIndexEngine()

    sessions = conn.execute(
        "SELECT * FROM sessions WHERE date(started_at) = ?", (date,)
    ).fetchall()

    hr_eff_vals, cwar_vals, sclor_vals, tlr_vals, ser_vals = [], [], [], [], []
    total_staleness = 0

    for s in sessions:
        raw = RawTelemetry(
            input_tokens=s["total_input_tokens"] or 0,
            output_tokens=s["total_output_tokens"] or 0,
            cache_read_tokens=s["total_cache_read_tokens"] or 0,
            cache_creation_tokens=s["total_cache_creation_tokens"] or 0,
            turn_count=s["turn_count"] or 0,
            task_type=s["task_type"] or "",
            task_risk_level=s["task_risk_level"] or "medium",
            model_id=s["model_id"] or "",
            cache_ttl_setting=s["cache_ttl_setting"] or "5min",
            estimated_overhead_tokens=s["estimated_overhead_tokens"] or CACHEABLE_PREFIX_ESTIMATE,
            staleness_events=s["staleness_events"] or 0,
            verification_tokens_estimate=s["verification_tokens_estimate"] or 0,
        )
        m = engine.compute(raw)
        ci = cie.compute_all(m, raw)

        hr_eff_vals.append(m.hr_effective)
        cwar_vals.append(m.cwar if m.cwar != float('inf') else 100.0)
        sclor_vals.append(m.sclor)
        tlr_vals.append(m.tlr)
        ser_vals.append(ci.ser)
        total_staleness += s["staleness_events"] or 0

    n = max(len(sessions), 1)
    atei = cie.compute_atei([
        {"ser": s, "task_type": sessions[i]["task_type"] or ""}
        for i, s in enumerate(ser_vals)
    ])

    conn.execute("""UPDATE daily_summary SET
        avg_hr_effective = ?, avg_cwar = ?, total_staleness_events = ?,
        avg_sclor = ?, avg_tlr = ?, atei = ?
        WHERE date = ?""",
        (sum(hr_eff_vals)/n, sum(cwar_vals)/n, total_staleness,
         sum(sclor_vals)/n, sum(tlr_vals)/n, atei, date))
```

**Files**: `tools/token_audit/db.py` (modify `upsert_daily_summary`)
**Tests**: `test_daily_summary_v2.py` — verify v2 columns populated after import
**Verification**: After `db import --all`, run `SELECT date, atei, avg_hr_effective FROM daily_summary` — values should be non-zero

### S2: BEI Efficiency Score v2 Upgrade (G2)

**Problem**: `BEIEngine._efficiency_score()` computes cache efficiency as `cache_hit_rate / ideal_cache_hit_rate` where `cache_hit_rate` is the naive formula. This means:
- A session with 98% naive hit rate but CWAR < 1.0 (losing money) scores HIGH on BEI efficiency
- The BEI system was designed before the v2 cache health framework existed

**Design**: Add v2-awareness to BEI efficiency scoring without breaking backward compatibility. The BEI efficiency dimension should blend cache efficiency AND cost efficiency:

```python
def _efficiency_score(self, snapshot: SessionSnapshot) -> float:
    # Try v2 metrics first
    cache_score = self._v2_cache_score(snapshot)

    # Cost-per-commit (unchanged)
    cost_score = self._cost_per_commit_score(snapshot)

    return cache_score * 0.4 + cost_score * 0.6

def _v2_cache_score(self, snapshot: SessionSnapshot) -> float:
    """Use CTI when available, fall back to naive hit rate."""
    try:
        from tools.token_audit.metrics_engine import RawTelemetry, MetricsEngine
        from tools.token_audit.composite_indices import CompositeIndexEngine
        raw = RawTelemetry.from_session_snapshot(snapshot)
        m = MetricsEngine().compute(raw)
        cie = CompositeIndexEngine()
        ci = cie.compute_all(m, raw)
        return ci.cti  # Cache Trust Index (0-1), already multi-dimensional
    except Exception:
        # Fallback to v1 behavior
        cache_rate = snapshot.tokens.cache_hit_rate
        ideal = self._config_baselines.get("ideal_cache_hit_rate", 0.85)
        return min(cache_rate / max(ideal, 0.01), 1.0)
```

**Design decision**: The v2 path returns CTI (Cache Trust Index) which inherently penalizes high naive hit rates with poor economics or staleness. The v1 path remains as fallback.

**Files**: `tools/token_audit/bei_engine.py` (modify `_efficiency_score`)
**Tests**: `test_bei_v2_efficiency.py` — verify CTI-based scoring penalizes low-CWAR sessions
**Verification**: Run BEI on a known session with high HR but low CWAR; efficiency score should drop vs v1

### S3: Session Report v2 Embedding (G3)

**Problem**: `generate_session_report()` produces v1 reports with token counts, cost, and BEI. The v2 diagnostic card is generated separately via `diagnose` CLI. They should be unified — the session report should include a v2 metrics section.

**Design**: Add an optional `--diagnostic` flag to `report session` that appends the v2 diagnostic card. Keep the default behavior unchanged (v1 report only).

```python
@click.option("--diagnostic", is_flag=True, help="Include v2 token economic diagnostic")
```

When `--diagnostic` is set, the report appends:
- Token Health Score (THS) and rating
- Cache Trust Index (CTI) and cache health state
- Session Efficiency Rating (SER)
- Active decision rule alerts

**Files**: `tools/token_audit/cli.py` (add flag), `tools/token_audit/reporter.py` (append diagnostic section)
**Verification**: `python -m tools.token_audit report --session <id> --diagnostic` produces combined report

### S4: DecisionEngine ↔ AlertEngine Bridge (G4)

**Problem**: `DecisionEngine` returns `DecisionAlert` objects with `rule_id`, `severity`, `message`, and `fix_suggestion`. `AlertEngine` uses `Alert` objects with `AlertType` enum and has cooldown tracking, DB persistence, and real-time monitoring integration. They don't connect.

**Design**: Add a bridge method to `AlertEngine` that consumes `DecisionAlert` objects:

```python
def evaluate_v2(self, raw, metrics, indices, session_id: str) -> list[Alert]:
    """Evaluate v2 decision rules through the alert pipeline."""
    from tools.token_audit.decision_engine import DecisionEngine
    de = DecisionEngine()
    historical = self._load_v2_historical()
    decisions = de.evaluate(metrics, indices, raw, historical)

    alerts = []
    for d in decisions:
        alert_type = AlertType(d.rule_id.lower())  # D1 → cache_deception, etc.
        if not self._in_cooldown(alert_type, session_id):
            alerts.append(Alert(
                alert_type=alert_type,
                severity=AlertSeverity.WARNING if d.severity.value == "warning" else
                         AlertSeverity.CRITICAL if d.severity.value == "critical" else
                         AlertSeverity.WARNING,
                message=d.message,
                session_id=session_id,
                context={"fix_suggestion": d.fix_suggestion},
            ))
    return alerts
```

**Design decision**: Map D-rule IDs to AlertType enum values. D1→CACHE_DECEPTION, D2→CONTEXT_BLOAT, etc. The bridge uses existing cooldown and persistence infrastructure.

**Files**: `tools/token_audit/alerts.py` (add `evaluate_v2`), `tools/token_audit/decision_engine.py` (no changes)
**Tests**: `test_alert_decision_bridge.py` — verify D1 alert flows through AlertEngine cooldown
**Verification**: Run `watch` on a session; verify v2 alerts appear alongside existing cost/efficiency alerts

---

## Medium-Term Plan (M1–M4): Calibration & Operations

**Timeline**: 3–6 weeks (requires data accumulation)
**Goal**: The v2 system transitions from "works with estimates" to "calibrated against real data."

### M1: Per-Workload Baseline Calibration

**Problem**: Composite indices (THS, SER) normalize metrics against per-workload thresholds (TLR ranges, SCLOR max, VCR targets). These thresholds are currently hardcoded from industry benchmarks. GCS-specific data may differ significantly.

**Design**: After 30 days of v2 data collection (sessions tagged with `task_type`), run calibration:

```bash
python -m tools.token_audit baseline calibrate-v2 --days 30
```

This computes per-workload P25/P50/P75 for:
- TLR (token leverage ratio) — replaces hardcoded TLR_RANGES
- SCLOR (cold-load overhead ratio) — replaces hardcoded SCLOR_MAX
- STES (session token efficiency score) — enables SER normalization
- CPCT (cost per completed task) — enables D7 anomaly detection
- CWAR (cache write amortization) — validates CACHEABLE_PREFIX_ESTIMATE

**Output**: `tools/token_audit/baselines_v2.json` — loaded by `CompositeIndexEngine` and `DecisionEngine`.

**Key decision**: After calibration, review whether `CACHEABLE_PREFIX_ESTIMATE = 39000` is accurate. If the per-session CWAR systematically deviates from the estimated value, adjust the constant.

### M2: Automated Weekly Audit Rhythm

**Problem**: The v2 system can generate diagnostics but nobody is scheduled to review them. The `gcs-token-audit-steward` skill should have a weekly procedure.

**Design**: Enhance `gcs-token-audit-steward` SKILL.md with a weekly checklist:

```markdown
## Weekly Audit Procedure

1. Import new sessions: `python -m tools.token_audit db import --since $(date -d '7 days ago' +%Y-%m-%d)`
2. Update daily summaries: `python -m tools.token_audit db update-summaries`
3. Check ATEI trend: `python -m tools.token_audit trend --days 30`
4. Cache health deep-dive: `python -m tools.token_audit cache-health --days 7`
5. Review active D-rule alerts: `python -m tools.token_audit alerts list --active`
6. If ATEI declining >15%: trigger investigation (D6)
7. If any session has CTI < 0.40: flag for cache strategy review
8. Generate weekly report: `python -m tools.token_audit report --this-week --diagnostic`
```

**Trigger**: Scheduled via `night-watch` agent or manual invocation.

### M3: Dashboard v2 Enhancement

**Problem**: The terminal/HTML dashboard shows project-level BEI and token counts but no cache health or v2 metrics.

**Design**: Add to `generate_dashboard()`:
- **Cache health summary row**: Avg CTI, USR total, CWAR average, state distribution
- **ATEI trend sparkline**: 7-day ATEI with arrow indicator
- **Top alerts**: Most recent 3 CRITICAL/WARNING v2 alerts

**HTML dashboard additions**:
- Cache health gauge (3 gauges: Efficiency, Freshness, Economics)
- ATEI trend line chart (7d, 14d, 30d)
- Workload distribution pie chart

### M4: Config.yaml v2 Section (G5)

**Problem**: v2 thresholds are hardcoded in `composite_indices.py` and `decision_engine.py`. Operators (or future agents) can't tune them without editing Python code.

**Design**: Add a `v2` section to `config.yaml`:

```yaml
v2:
  cache:
    cacheable_prefix_estimate: 39000
    cwar_break_even_5min: 1.4
    cwar_break_even_1hour: 2.2
  thresholds:
    tlr_ranges:
      code-gen: [0.05, 0.20]
      research: [0.01, 0.05]
      # ... per-workload
    sclor_max:
      code-gen: 0.12
      research: 0.20
      # ... per-workload
    vcr_targets:
      low: [0.05, 0.15]
      medium: [0.10, 0.25]
      high: [0.20, 0.50]
      critical: [0.30, 0.80]
  weights:
    ths:
      cache: 0.20
      overhead: 0.25
      leverage: 0.30
      waste: 0.25
    atei_type_weights:
      bug-fix: 1.0
      research: 0.70
      # ... per-type
```

`CompositeIndexEngine` loads from config on init, falling back to hardcoded defaults.

---

## Long-Term Plan (L1–L4): Accuracy & Automation

**Timeline**: 2–4 months
**Goal**: Replace estimation-based metrics with accurate, data-driven measurements. Automate manual processes.

### L1: Per-Turn Token Waste Tracking (TWR Accuracy)

**Problem**: M7 (Token Waste Ratio) uses a TLR-based heuristic: TLR < 0.01 → 50% waste, TLR > 0.05 → 5% waste. This conflates "exploratory reasoning" (valuable) with "wasted context processing" (not valuable). A research session with legitimate deep exploration would be flagged as "50% waste."

**Design**: Enhance the JSONL parser to track per-turn token attribution:

1. **Tag each turn** with its purpose: `action` (edits, tool calls), `verification` (tests, lint), `exploration` (reads, searches), `planning` (analysis before action)
2. **Compute TWR per turn**: wasted = turns tagged `exploration` that produced no downstream action + identical retries of failed tool calls
3. **Session TWR** = wasted_tokens / total_input_tokens

This requires:
- Parser enhancement: classify each turn by tool call pattern
- New DB columns: `turn_purpose` in `turns` table
- New metric: `twr_accurate` (replaces heuristic `twr`)

**Accuracy improvement**: From ±30% heuristic to ±10% measured.

### L2: Per-Turn Context Growth Rate (CGR Accuracy)

**Problem**: M12 (Context Growth Rate) estimates first-turn input as a fraction of total input based on turn_count. This is coarse (±40% error). The `turns` table already stores per-turn `input_tokens` but the field is never populated.

**Design**: Populate `turns.input_tokens` during JSONL import. Then compute CGR directly:

```python
def _m12_cgr_accurate(raw: RawTelemetry, turn_inputs: list[int]) -> float:
    """M12 accurate: actual growth from first turn to last-3-turns average."""
    if len(turn_inputs) < 3:
        return 1.0
    first_turn = turn_inputs[0]
    last_3_avg = sum(turn_inputs[-3:]) / 3
    return last_3_avg / first_turn if first_turn > 0 else 1.0
```

**Prerequisite**: Fix JSONL import to populate `turns.input_tokens` from `message.usage.input_tokens` per record.

### L3: Automatic Staleness Detection (USR Automation)

**Problem**: M8 (Unsafe-Served Rate) depends on `staleness_events` which is currently always 0 because nobody is detecting staleness. The metric exists but has no data source.

**Design**: Add staleness detection to the session tracker or post-hoc importer:

1. **During import**: For each `Read` or `Edit` tool call, record the file path and the JSONL timestamp
2. **Staleness check**: If the same file is read twice in a session, and the file's filesystem modification time changed between reads, increment `staleness_events`
3. **Cross-session staleness**: If a file read in this session was modified by a different session (detectable via git log), flag as cross-session staleness

**Implementation**:
- New module: `tools/token_audit/staleness_detector.py`
- Called during `db import` as a post-processing step
- Updates `sessions.staleness_events`

### L4: Real-Time v2 Metric Streaming

**Problem**: The v2 system is batch-oriented — metrics are computed post-hoc during import or via CLI. The `watch` command shows real-time token counts and cost but no v2 metrics.

**Design**: Integrate `MetricsEngine` and `CompositeIndexEngine` into `SessionTracker.tick()`:

```python
def tick(self) -> Optional[SessionSnapshot]:
    records = self.parser.read_new_records()
    if records:
        self._process_records(records)
        # v2: compute metrics incrementally
        raw = RawTelemetry.from_session_snapshot(self.snapshot)
        self._latest_metrics = self.metrics_engine.compute(raw)
        self._latest_indices = self.indices_engine.compute_all(
            self._latest_metrics, raw)
    return self.snapshot
```

The `watch` terminal output adds a v2 line:
```
THS: 78 (Adequate) | CTI: 0.87 (Trustworthy) | Cache: IDEAL | Alerts: 0
```

---

## Priority Matrix

| ID | Item | Effort | Impact | Urgency | Priority |
|----|------|--------|--------|---------|----------|
| S1 | Daily summary v2 population | 2h | HIGH | HIGH | **1** |
| S2 | BEI efficiency v2 upgrade | 1.5h | MEDIUM | MEDIUM | **2** |
| S4 | DecisionEngine↔AlertEngine bridge | 1.5h | MEDIUM | MEDIUM | **3** |
| S3 | Session report v2 embedding | 1h | MEDIUM | LOW | **4** |
| M4 | Config.yaml v2 section | 1h | LOW | LOW | **5** |
| M3 | Dashboard v2 enhancement | 3h | MEDIUM | LOW | **6** |
| M1 | Per-workload calibration | 4h | HIGH | MEDIUM | **7** (needs 30d data) |
| M2 | Weekly audit rhythm | 1h | MEDIUM | LOW | **8** |
| L1 | Per-turn TWR tracking | 6h | HIGH | LOW | **9** |
| L2 | Per-turn CGR tracking | 3h | MEDIUM | LOW | **10** |
| L3 | Automatic staleness detection | 4h | MEDIUM | LOW | **11** |
| L4 | Real-time v2 streaming | 4h | LOW | LOW | **12** |

---

## Dependency Graph

```
S1 (daily summary) ─────────────────────────────────────────────────┐
    │                                                                │
    ▼                                                                │
S2 (BEI upgrade) ──► S3 (report embedding) ──► M3 (dashboard)       │
    │                                                                │
    ▼                                                                │
S4 (alert bridge) ──► M2 (weekly rhythm)                             │
                                                                     │
M4 (config) ◄───────────────────────────────────────────────────────┘
    │
    ▼
M1 (calibration) ←── requires 30 days of S1 data
    │
    ▼
L1 (per-turn TWR) ──► L2 (per-turn CGR) ──► L3 (staleness) ──► L4 (streaming)
```

---

## Success Metrics

| Metric | Current | S1–S4 Target | M1–M4 Target | L1–L4 Target |
|--------|---------|-------------|-------------|-------------|
| Tests | 41 | 55+ | 65+ | 80+ |
| Daily summary v2 fields populated | 0/6 | 6/6 | 6/6 | 6/6 |
| BEI efficiency uses CTI | No | Yes | Yes | Yes |
| D-rule alerts flow to AlertEngine | No | Yes | Yes | Yes |
| Per-workload baselines calibrated | Hardcoded | Hardcoded | Calibrated | Calibrated |
| TWR accuracy | ±30% (heuristic) | ±30% | ±30% | ±10% (measured) |
| CGR accuracy | ±40% (estimated) | ±40% | ±40% | ±5% (measured) |
| USR data source | None | None | None | Automated |
| Real-time v2 in `watch` | No | No | No | Yes |
| Weekly audit automated | No | No | Yes | Yes |
