# GCS Token Economic Evaluation System — Detailed Execution Plan

**Date**: 2026-05-28
**Status**: Ready for execution
**Depends on**: [Multi-Paradigm Research Report](token-economics-multi-paradigm-analysis-2026-05-28.md), [Unified Evaluation System Design](token-economics-unified-evaluation-system-2026-05-28.md)
**Target modules**: `tools/token_audit/` (Python), `docs/reports/` (output)

---

## Executive Summary

This document defines the concrete implementation plan for upgrading GCS's token audit system from a first-generation cost-tracking tool to a multi-dimensional token economic evaluation system. The plan covers 5 phases over 5–6 weeks, each producing a working increment. Every phase specifies exact file changes, new code, test criteria, and integration points.

### Gap Summary: Current State → Target State

| Dimension | Current State | Target State | Gap |
|-----------|--------------|-------------|-----|
| Cache metrics | Raw hit rate only (M1) | HR_eff (M2), CWAR (M3), USR (M8) | 3 new metrics |
| Efficiency metrics | TLR implicit in BEI | Explicit TLR (M6), TWR (M7), CGR (M12), TDOR (M13) | 4 new metrics |
| Fixed cost tracking | Not tracked | SCLOR (M4), CLAE (M5) | 2 new metrics |
| Risk adjustment | Not tracked | VCR (M11) | 1 new metric |
| Composite indices | BEI only (5-dim) | THS (CI-1), CTI (CI-2), SER (CI-3), ATEI (CI-4) | 4 new indices |
| Workload classification | None | 8 categories with per-category thresholds | New subsystem |
| Decision rules | 5 budget/cost alerts | 7 semantic rules (D1–D7) | 7 new rules |
| Schema fields | 28 columns | ~38 columns (10 new) | Schema migration |
| Dashboard | Project-level BEI table | Session diagnostic card + cache health + trends | 3 new views |

---

## Phase 0: Preparation & Baseline (Day 0–1)

### 0.1 Current State Snapshot

Before any code changes, capture the current baseline:

```bash
cd C:\Codes\AI\GCS_A
python -m tools.token_audit db stats
python -m tools.token_audit report trend --days 30
```

Save output to `docs/reports/pre-upgrade-baseline-2026-05-28.md`.

### 0.2 Git Worktree

```bash
git worktree add -b token-econ-v2 .claude/worktrees/token-econ-v2
```

### 0.3 Test Baseline

```bash
python -m pytest tools/token_audit/tests/ -v
```

Record any pre-existing test failures. All existing tests must continue to pass after each phase.

### 0.4 Task Card

```bash
python tools/agentic_design/agentic_toolkit.py new-task-card \
  --slug token-econ-metric-system-v2 \
  --scope architecture \
  --risk medium \
  --owner gcs-token-audit-steward \
  --request "Upgrade token audit system from v1 cost-tracking to v2 multi-dimensional token economic evaluation with cache health framework, workload classification, composite indices, and decision rules." \
  --write
```

---

## Phase 1: Data Model Foundation (Day 1–3)

**Goal**: Extend schema and data structures to capture all raw telemetry needed for the new metrics. No metric computation changes yet.

### 1.1 Schema Migration

**File**: `tools/token_audit/schema.sql`

Add columns to `sessions` table:

```sql
ALTER TABLE sessions ADD COLUMN cache_ttl_setting TEXT DEFAULT '5min';
ALTER TABLE sessions ADD COLUMN workload_category TEXT;
ALTER TABLE sessions ADD COLUMN task_type TEXT;
ALTER TABLE sessions ADD COLUMN task_risk_level TEXT DEFAULT 'medium';
ALTER TABLE sessions ADD COLUMN task_outcome TEXT;
ALTER TABLE sessions ADD COLUMN turn_count INTEGER DEFAULT 0;
ALTER TABLE sessions ADD COLUMN estimated_overhead_tokens INTEGER DEFAULT 0;
ALTER TABLE sessions ADD COLUMN staleness_events INTEGER DEFAULT 0;
ALTER TABLE sessions ADD COLUMN verification_tokens_estimate INTEGER DEFAULT 0;
ALTER TABLE sessions ADD COLUMN tool_definition_tokens_estimate INTEGER DEFAULT 0;
```

Add columns to `daily_summary` table:

```sql
ALTER TABLE daily_summary ADD COLUMN avg_hr_effective REAL;
ALTER TABLE daily_summary ADD COLUMN avg_cwar REAL;
ALTER TABLE daily_summary ADD COLUMN total_staleness_events INTEGER DEFAULT 0;
ALTER TABLE daily_summary ADD COLUMN avg_sclor REAL;
ALTER TABLE daily_summary ADD COLUMN avg_tlr REAL;
ALTER TABLE daily_summary ADD COLUMN atei REAL;
```

**Implementation**: Extend the `_migrate()` function in `db.py` to add these columns conditionally (checking `PRAGMA table_info` for each).

### 1.2 TokenUsage Enhancement

**File**: `tools/token_audit/parser.py`

Add properties to `TokenUsage`:

```python
@property
def cache_hit_rate_raw(self) -> float:
    """M1: Raw cache hit rate."""
    denom = self.cache_read_tokens + self.cache_creation_tokens
    return self.cache_read_tokens / denom if denom > 0 else 0.0

@property
def uncached_input_tokens(self) -> int:
    """Tokens that were neither read from nor written to cache."""
    return self.input_tokens - self.cache_read_tokens - self.cache_creation_tokens
```

**Note**: The existing `cache_hit_rate` property uses a different denominator (`cache_read / (cache_read + input)`). The new `cache_hit_rate_raw` uses the correct formula (`cache_read / (cache_read + cache_creation)`). We'll deprecate the old property but keep it for backward compatibility.

### 1.3 SessionSnapshot Enhancement

**File**: `tools/token_audit/parser.py`

Add fields to `SessionSnapshot.__init__`:

```python
self.cache_ttl_setting: str = "5min"
self.workload_category: str = ""
self.task_type: str = ""
self.task_risk_level: str = "medium"
self.task_outcome: str = ""
self.turn_count: int = 0
self.estimated_overhead_tokens: int = 0
self.staleness_events: int = 0
self.verification_tokens_estimate: int = 0
self.tool_definition_tokens_estimate: int = 0
```

### 1.4 DB Layer Update

**File**: `tools/token_audit/db.py`

Update `insert_session()` and `upsert_daily_summary()` to handle new columns.

### 1.5 Phase 1 Verification

- [ ] Schema migration runs on existing database without data loss
- [ ] Existing tests pass unchanged
- [ ] `TokenUsage.uncached_input_tokens` computes correctly with test data
- [ ] `SessionSnapshot` can be constructed with new fields
- [ ] `insert_session()` writes and `get_session()` reads all new fields

---

## Phase 2: Derived Metrics Engine (Day 3–7)

**Goal**: Implement M1–M13 metric computation in a new module. No integration with existing code yet.

### 2.1 New Module: `metrics_engine.py`

**File**: `tools/token_audit/metrics_engine.py` (new, ~350 lines)

This is the core computation engine. It takes raw telemetry and produces all 13 derived metrics.

```python
"""Derived metrics engine for token economic evaluation.

Implements M1-M13 from the unified evaluation system design.
"""

from dataclasses import dataclass, field
from typing import Optional

@dataclass
class RawTelemetry:
    """Layer 1: raw data from API + session metadata."""
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_creation_tokens: int = 0
    session_duration_seconds: float = 0.0
    turn_count: int = 0
    tool_call_count: int = 0
    task_outcome: str = ""
    task_type: str = ""
    task_risk_level: str = "medium"
    model_id: str = ""
    cache_ttl_setting: str = "5min"
    estimated_overhead_tokens: int = 0
    staleness_events: int = 0
    verification_tokens_estimate: int = 0
    tool_definition_tokens_estimate: int = 0
    lines_added: int = 0
    lines_removed: int = 0
    commits_count: int = 0

@dataclass
class DerivedMetrics:
    """Layer 2: computed metrics M1-M13."""
    # Cache metrics
    hr_raw: float = 0.0            # M1
    hr_effective: float = 0.0      # M2
    cwar: float = 0.0              # M3

    # Overhead metrics
    sclor: float = 0.0             # M4
    clae: float = 0.0              # M5

    # Efficiency metrics
    tlr: float = 0.0               # M6
    twr: float = 0.0               # M7
    usr: float = 0.0               # M8
    stes: float = 0.0              # M9
    cpct: float = 0.0              # M10

    # Risk/quality metrics
    vcr: float = 0.0               # M11
    cgr: float = 0.0               # M12
    tdor: float = 0.0              # M13


class MetricsEngine:
    """Computes all 13 derived metrics from raw telemetry."""

    def __init__(self, cost_model=None, historical_baselines: dict = None,
                 session_count_7d: int = 1):
        self.cost_model = cost_model
        self.baselines = historical_baselines or {}
        self.session_count_7d = session_count_7d

    def compute(self, raw: RawTelemetry) -> DerivedMetrics:
        """Compute all derived metrics from raw telemetry."""
        m = DerivedMetrics()

        # M1: Raw cache hit rate
        denom = raw.cache_read_tokens + raw.cache_creation_tokens
        m.hr_raw = raw.cache_read_tokens / denom if denom > 0 else 0.0

        # M2: Effective cache hit rate (write-premium adjusted)
        m.hr_effective = self._compute_hr_effective(raw)

        # M3: Cache write amortization ratio
        m.cwar = (raw.cache_read_tokens / raw.cache_creation_tokens
                  if raw.cache_creation_tokens > 0 else float('inf'))

        # M4: Session cold-load overhead ratio
        m.sclor = (raw.estimated_overhead_tokens / raw.input_tokens
                   if raw.input_tokens > 0 else 0.0)

        # M5: Cold-load amortization efficiency
        fixed = raw.estimated_overhead_tokens * max(self.session_count_7d, 1)
        task_tokens = raw.input_tokens - raw.estimated_overhead_tokens
        m.clae = task_tokens / fixed if fixed > 0 else 0.0

        # M6: Token leverage ratio
        m.tlr = (raw.output_tokens / raw.input_tokens
                 if raw.input_tokens > 0 else 0.0)

        # M7: Token waste ratio (heuristic estimate)
        m.twr = self._estimate_twr(raw)

        # M8: Unsafe-served rate
        m.usr = (raw.staleness_events / max(raw.turn_count, 1)
                 if raw.staleness_events > 0 else 0.0)

        # M9: Session token efficiency score
        m.stes = self._compute_stes(raw)

        # M10: Cost per completed task — computed at aggregate level
        # (placeholder, filled by aggregate query)

        # M11: Verification coverage ratio
        m.vcr = (raw.verification_tokens_estimate / raw.input_tokens
                 if raw.input_tokens > 0 and raw.verification_tokens_estimate > 0
                 else 0.0)

        # M12: Context growth rate
        m.cgr = self._compute_cgr(raw)

        # M13: Tool definition overhead ratio
        m.tdor = (raw.tool_definition_tokens_estimate / raw.input_tokens
                  if raw.input_tokens > 0 else 0.0)

        return m

    def _compute_hr_effective(self, raw: RawTelemetry) -> float:
        """M2: Cost-adjusted cache efficiency."""
        uncached = raw.input_tokens - raw.cache_read_tokens - raw.cache_creation_tokens
        if uncached < 0:
            uncached = 0

        write_premium = 1.25 if raw.cache_ttl_setting == "5min" else 2.0

        effective_read_cost = raw.cache_read_tokens * 0.10
        effective_write_cost = raw.cache_creation_tokens * write_premium
        effective_uncached_cost = uncached * 1.0
        total_effective_cost = effective_read_cost + effective_write_cost + effective_uncached_cost

        if total_effective_cost == 0:
            return 0.0
        return effective_read_cost / total_effective_cost

    def _estimate_twr(self, raw: RawTelemetry) -> float:
        """M7: Estimate token waste ratio from heuristics."""
        # Heuristic: ratio of input to output beyond a healthy baseline
        # A session with TLR < 0.005 and high tool calls likely has waste
        if raw.input_tokens == 0:
            return 0.0

        tlr = raw.tlr if hasattr(raw, 'tlr') else (
            raw.output_tokens / raw.input_tokens if raw.input_tokens > 0 else 0.0
        )

        # Baseline: healthy TLR is workload-dependent
        # For initial implementation, use a simple heuristic
        if tlr >= 0.05:
            return 0.05  # minimal waste
        elif tlr >= 0.02:
            return 0.15
        elif tlr >= 0.01:
            return 0.30
        else:
            return 0.50

    def _compute_stes(self, raw: RawTelemetry) -> float:
        """M9: Session token efficiency score."""
        if raw.input_tokens == 0:
            return 0.0

        outcome_values = {
            "completed": 1.0,
            "partial": 0.5,
            "failed": 0.15,
            "abandoned": 0.0,
            "": 0.3,  # unknown
        }
        outcome_value = outcome_values.get(raw.task_outcome, 0.3)

        total_tokens = raw.input_tokens + raw.output_tokens
        # Use default cost rate if no cost model
        cost_per_token = 3.0 / 1_000_000  # $3/M input as rough default
        estimated_cost = total_tokens * cost_per_token

        return outcome_value / estimated_cost if estimated_cost > 0 else 0.0

    def _compute_cgr(self, raw: RawTelemetry) -> float:
        """M12: Context growth rate.

        Estimated from total input / estimated first-turn input.
        First-turn input is approximated as overhead + initial user message.
        Since we don't have per-turn breakdown in RawTelemetry,
        this is a coarse estimate.
        """
        if raw.turn_count <= 1:
            return 1.0
        # Assume first turn is ~20% of total for long sessions,
        # ~50% for short sessions
        if raw.turn_count <= 5:
            first_turn_estimate = raw.input_tokens * 0.5
        elif raw.turn_count <= 15:
            first_turn_estimate = raw.input_tokens * 0.25
        else:
            first_turn_estimate = raw.input_tokens * 0.12

        avg_last_turns = raw.input_tokens / max(raw.turn_count, 1) * 3
        # Last 3 turns average
        return avg_last_turns / max(first_turn_estimate, 1)
```

### 2.2 Unit Tests

**File**: `tools/token_audit/tests/test_metrics_engine.py` (new, ~150 lines)

Test cases:
- `test_m1_hr_raw`: Verify correct formula with known values
- `test_m2_hr_effective_5min_ttl`: Write premium 1.25×, verify cost-adjusted rate
- `test_m2_hr_effective_1hour_ttl`: Write premium 2.0×
- `test_m3_cwar_break_even`: CWAR at 1.4 (break-even for 5-min)
- `test_m3_cwar_below_one`: CWAR < 1 means write premium loss
- `test_m4_sclor`: Overhead ratio with known overhead estimate
- `test_m6_tlr`: Token leverage ratio
- `test_m8_usr_zero`: No staleness events → USR = 0
- `test_m8_usr_present`: Staleness events → USR > 0
- `test_m9_stes_completed`: Completed task gets full outcome value
- `test_m9_stes_abandoned`: Abandoned task gets zero
- `test_m11_vcr`: Verification coverage ratio

### 2.3 Phase 2 Verification

- [ ] All 13 derived metrics compute without error on sample data
- [ ] M2 (HR_eff) ≤ M1 (HR_raw) when write premium is priced in (mathematically guaranteed)
- [ ] CWAR = ∞ when cache_creation == 0 and cache_read > 0
- [ ] STES is higher for completed tasks than abandoned tasks with same token counts
- [ ] All unit tests pass

---

## Phase 3: Composite Indices & Workload Classification (Day 7–12)

**Goal**: Implement CI-1 through CI-4 and the workload classification system.

### 3.1 New Module: `composite_indices.py`

**File**: `tools/token_audit/composite_indices.py` (new, ~250 lines)

```python
"""Composite indices for token economic evaluation.

Implements CI-1 through CI-4 from the unified evaluation system design.
"""

from dataclasses import dataclass
from enum import Enum
from tools.token_audit.metrics_engine import DerivedMetrics, RawTelemetry


class WorkloadCategory(Enum):
    CODE_GEN = "code-gen"
    CODE_REVIEW = "code-review"
    ARCHITECTURE = "architecture"
    RESEARCH = "research"
    DEBUG = "debug"
    DOCS = "docs"
    OPS = "ops"
    PROCESS = "process"


# Per-workload healthy ranges for TLR normalization
TLR_RANGES = {
    WorkloadCategory.CODE_GEN:     (0.05, 0.20),
    WorkloadCategory.CODE_REVIEW:  (0.02, 0.08),
    WorkloadCategory.ARCHITECTURE: (0.02, 0.10),
    WorkloadCategory.RESEARCH:     (0.01, 0.05),
    WorkloadCategory.DEBUG:        (0.02, 0.08),
    WorkloadCategory.DOCS:         (0.03, 0.12),
    WorkloadCategory.OPS:          (0.04, 0.15),
    WorkloadCategory.PROCESS:      (0.01, 0.05),
}

# Per-workload SCLOR healthy maximums
SCLOR_MAX = {
    WorkloadCategory.CODE_GEN:     0.12,
    WorkloadCategory.CODE_REVIEW:  0.15,
    WorkloadCategory.ARCHITECTURE: 0.15,
    WorkloadCategory.RESEARCH:     0.20,
    WorkloadCategory.DEBUG:        0.15,
    WorkloadCategory.DOCS:         0.12,
    WorkloadCategory.OPS:          0.10,
    WorkloadCategory.PROCESS:      0.10,
}

# Per-risk-level VCR targets
VCR_TARGETS = {
    "low":     (0.05, 0.15),
    "medium":  (0.10, 0.25),
    "high":    (0.20, 0.50),
    "critical":(0.30, 0.80),
}

# CWAR break-even by TTL
CWAR_BREAK_EVEN = {
    "5min": 1.4,
    "1hour": 2.2,
}

# Composite index weights (tunable)
DEFAULT_THS_WEIGHTS = {
    "cache": 0.20,
    "overhead": 0.25,
    "leverage": 0.30,
    "waste": 0.25,
}


@dataclass
class CompositeIndices:
    """Layer 3: composite evaluation scores."""
    ths: float = 0.0     # CI-1: Token Health Score (0-100)
    cti: float = 0.0     # CI-2: Cache Trust Index (0-1)
    ser: float = 0.0     # CI-3: Session Efficiency Rating (0-1)
    atei: float = 0.0    # CI-4: Aggregate Token Economic Index (0-1)
    workload: str = ""
    cache_health_state: str = ""  # Ideal, Wasteful, Dangerous, Inefficient, Broken


class CompositeIndexEngine:
    """Computes composite indices from derived metrics."""

    def __init__(self, ths_weights: dict = None):
        self.ths_weights = ths_weights or DEFAULT_THS_WEIGHTS.copy()

    def classify_workload(self, task_type: str, tool_call_pattern: dict = None) -> WorkloadCategory:
        """Classify session into workload category from task type and tool patterns."""
        # Direct mapping from task card scope
        task_map = {
            "bug-fix": WorkloadCategory.CODE_GEN,
            "feature": WorkloadCategory.CODE_GEN,
            "refactor": WorkloadCategory.CODE_GEN,
            "research": WorkloadCategory.RESEARCH,
            "docs": WorkloadCategory.DOCS,
            "ops": WorkloadCategory.OPS,
            "process": WorkloadCategory.PROCESS,
            "review": WorkloadCategory.CODE_REVIEW,
            "design": WorkloadCategory.ARCHITECTURE,
        }
        if task_type in task_map:
            return task_map[task_type]

        # Fallback: use tool patterns if available
        if tool_call_pattern:
            read_ratio = tool_call_pattern.get("read_ratio", 0)
            edit_ratio = tool_call_pattern.get("edit_ratio", 0)
            if read_ratio > 0.6 and edit_ratio < 0.1:
                return WorkloadCategory.RESEARCH
            if edit_ratio > 0.3:
                return WorkloadCategory.CODE_GEN

        return WorkloadCategory.CODE_GEN  # default

    def compute_ths(self, m: DerivedMetrics, workload: WorkloadCategory) -> float:
        """CI-1: Token Health Score (0-100)."""
        w = self.ths_weights

        # Normalize TLR to 0-1 using workload-specific range
        tlr_min, tlr_max = TLR_RANGES.get(workload, (0.02, 0.10))
        tlr_norm = min(max((m.tlr - tlr_min) / max(tlr_max - tlr_min, 0.001), 0), 1)

        # Normalize SCLOR (lower is better)
        sclor_max = SCLOR_MAX.get(workload, 0.15)
        sclor_score = max(0, 1 - m.sclor / sclor_max)

        # Cap infinite CWAR at 10.0 for scoring
        cwar_capped = min(m.cwar, 10.0) if m.cwar != float('inf') else 10.0
        cwar_score = min(cwar_capped / 3.0, 1.0)  # 3.0 reads/write = excellent

        return 100 * (
            w["cache"] * cwar_score
            + w["overhead"] * sclor_score
            + w["leverage"] * tlr_norm
            + w["waste"] * (1 - m.twr)
        )

    def compute_cti(self, m: DerivedMetrics, raw: RawTelemetry) -> float:
        """CI-2: Cache Trust Index (0-1)."""
        ttl = raw.cache_ttl_setting or "5min"
        break_even = CWAR_BREAK_EVEN.get(ttl, 1.4)

        # Dimension 1: Efficiency (HR_eff)
        efficiency = m.hr_effective

        # Dimension 2: Freshness (1 - USR)
        freshness = 1.0 - min(m.usr, 1.0)

        # Dimension 3: Economics (CWAR vs break-even)
        if m.cwar == float('inf'):
            economics = 1.0
        else:
            economics = min(m.cwar / break_even, 1.0)

        cti = efficiency * freshness * economics
        return min(max(cti, 0.0), 1.0)

    def compute_ser(self, m: DerivedMetrics, raw: RawTelemetry,
                    historical_stes_median: float = None) -> float:
        """CI-3: Session Efficiency Rating (0-1)."""
        # Normalize STES against historical median
        if historical_stes_median and historical_stes_median > 0:
            stes_norm = min(m.stes / historical_stes_median, 2.0) / 2.0
        else:
            stes_norm = 0.5

        # VCR adequacy
        risk = raw.task_risk_level or "medium"
        vcr_min, vcr_max = VCR_TARGETS.get(risk, (0.10, 0.25))
        if m.vcr >= vcr_min:
            vcr_adequacy = 1.0
        elif m.vcr > 0:
            vcr_adequacy = m.vcr / vcr_min
        else:
            vcr_adequacy = 0.5  # unknown, neutral

        # Staleness penalty
        alpha = 0.5
        staleness_penalty = 1.0 - alpha * min(m.usr, 1.0)

        ser = stes_norm * vcr_adequacy * staleness_penalty
        return min(max(ser, 0.0), 1.0)

    def compute_atei(self, sessions: list[dict]) -> float:
        """CI-4: Aggregate Token Economic Index over a set of sessions.

        Each session dict should have 'ser' and 'task_type' keys.
        """
        if not sessions:
            return 0.0

        # Task type weights for ATEI aggregation
        type_weights = {
            "bug-fix": 1.0, "feature": 0.85, "refactor": 0.90,
            "research": 0.70, "docs": 0.95, "ops": 0.90,
            "debug": 0.85, "review": 0.90, "process": 0.90,
        }

        weighted_sum = 0.0
        weight_sum = 0.0
        for s in sessions:
            ser = s.get("ser", 0.0)
            task_type = s.get("task_type", "")
            w = type_weights.get(task_type, 0.85)
            weighted_sum += ser * w
            weight_sum += w

        return weighted_sum / weight_sum if weight_sum > 0 else 0.0

    def cache_health_diagnosis(self, m: DerivedMetrics, cti: float) -> str:
        """Determine cache health state from the three dimensions."""
        efficiency_ok = m.hr_effective >= 0.40
        freshness_ok = m.usr <= 0.05
        cwar_ok = m.cwar >= 1.4 if m.cwar != float('inf') else True

        if efficiency_ok and freshness_ok and cwar_ok:
            return "Ideal"
        elif efficiency_ok and freshness_ok and not cwar_ok:
            return "Wasteful"
        elif efficiency_ok and not freshness_ok:
            return "Dangerous"
        elif not efficiency_ok and freshness_ok and cwar_ok:
            return "Inefficient"
        else:
            return "Broken"
```

### 3.2 Phase 3 Verification

- [ ] Workload classification maps known task types correctly
- [ ] THS is 0-100 range for all workload categories
- [ ] CTI penalizes high HR when USR > 0 or CWAR < break-even
- [ ] SER incorporates all three dimensions (STES, VCR, staleness)
- [ ] ATEI weights different task types appropriately
- [ ] Cache health states map correctly to dimension combinations
- [ ] All unit tests pass

---

## Phase 4: Decision Rules & Alerting (Day 12–16)

**Goal**: Implement the 7 decision rules (D1–D7) and integrate with existing alert infrastructure.

### 4.1 New Module: `decision_engine.py`

**File**: `tools/token_audit/decision_engine.py` (new, ~200 lines)

```python
"""Decision rule engine for token economic evaluation.

Implements D1-D7 from the unified evaluation system design.
"""

from dataclasses import dataclass, field
from enum import Enum
from tools.token_audit.metrics_engine import DerivedMetrics, RawTelemetry
from tools.token_audit.composite_indices import CompositeIndices, WorkloadCategory, VCR_TARGETS, CWAR_BREAK_EVEN


class RuleSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class DecisionAlert:
    rule_id: str
    severity: RuleSeverity
    message: str
    session_id: str = ""
    fix_suggestion: str = ""


class DecisionEngine:
    """Evaluates D1-D7 decision rules against session metrics."""

    def evaluate(self, m: DerivedMetrics, ci: CompositeIndices,
                 raw: RawTelemetry, historical: dict = None) -> list[DecisionAlert]:
        """Evaluate all decision rules. Returns triggered alerts."""
        alerts = []
        sid = getattr(raw, 'session_id', '')

        alerts.extend(self._rule_d1_cache_deception(m, ci, raw, sid))
        alerts.extend(self._rule_d2_context_bloat(m, raw, sid))
        alerts.extend(self._rule_d3_verification_gap(m, raw, sid))
        alerts.extend(self._rule_d4_cold_load_dominance(m, raw, sid))
        alerts.extend(self._rule_d5_write_premium_loss(m, raw, sid))
        alerts.extend(self._rule_d6_atei_decline(ci, historical, sid))
        alerts.extend(self._rule_d7_task_cost_anomaly(m, raw, historical, sid))

        return alerts

    def _rule_d1_cache_deception(self, m, ci, raw, sid) -> list[DecisionAlert]:
        """D1: High raw hit rate but low cache trust."""
        if m.hr_raw > 0.90 and ci.cti < 0.50:
            return [DecisionAlert(
                rule_id="D1",
                severity=RuleSeverity.CRITICAL,
                message=f"Cache deception: HR={m.hr_raw:.1%} but CTI={ci.cti:.2f}. "
                        f"Cache may be losing money or serving stale data.",
                session_id=sid,
                fix_suggestion="Check TTL mismatch, dynamic content in cache blocks, "
                               "or stale file references."
            )]
        return []

    def _rule_d2_context_bloat(self, m, raw, sid) -> list[DecisionAlert]:
        """D2: Context grew 10x but output efficiency is very low."""
        if m.cgr > 10 and m.tlr < 0.02:
            return [DecisionAlert(
                rule_id="D2",
                severity=RuleSeverity.WARNING,
                message=f"Context bloat: CGR={m.cgr:.1f}x, TLR={m.tlr:.4f}. "
                        f"Context grew but output per input token is very low.",
                session_id=sid,
                fix_suggestion="Consider context compaction or starting a fresh session."
            )]
        return []

    def _rule_d3_verification_gap(self, m, raw, sid) -> list[DecisionAlert]:
        """D3: Verification tokens below half of risk-appropriate target."""
        risk = raw.task_risk_level or "medium"
        vcr_min, _ = VCR_TARGETS.get(risk, (0.10, 0.25))
        if m.vcr < vcr_min * 0.5 and m.vcr >= 0:
            severity = RuleSeverity.CRITICAL if risk in ("high", "critical") else RuleSeverity.WARNING
            return [DecisionAlert(
                rule_id="D3",
                severity=severity,
                message=f"Verification gap: VCR={m.vcr:.3f} below {vcr_min*0.5:.3f} "
                        f"(50% of target for {risk}-risk tasks).",
                session_id=sid,
                fix_suggestion=f"Risk level is {risk}; increase verification "
                               f"(tests, linting, review) to at least VCR={vcr_min:.2f}."
            )]
        return []

    def _rule_d4_cold_load_dominance(self, m, raw, sid) -> list[DecisionAlert]:
        """D4: Overhead dominates input in very short sessions."""
        if m.sclor > 0.25 and raw.turn_count < 5:
            return [DecisionAlert(
                rule_id="D4",
                severity=RuleSeverity.INFO,
                message=f"Cold-load dominance: {m.sclor:.0%} of input is fixed overhead "
                        f"in a {raw.turn_count}-turn session.",
                session_id=sid,
                fix_suggestion="Consider whether this task needed a full agentic session, "
                               "or could be done in a simpler mode."
            )]
        return []

    def _rule_d5_write_premium_loss(self, m, raw, sid) -> list[DecisionAlert]:
        """D5: CWAR below break-even for the TTL setting."""
        if m.cwar == float('inf'):
            return []
        ttl = raw.cache_ttl_setting or "5min"
        break_even = CWAR_BREAK_EVEN.get(ttl, 1.4)
        if m.cwar < break_even:
            severity = RuleSeverity.CRITICAL if m.cwar < 1.0 else RuleSeverity.WARNING
            return [DecisionAlert(
                rule_id="D5",
                severity=severity,
                message=f"Write-premium loss: CWAR={m.cwar:.1f} below {ttl} "
                        f"break-even ({break_even}).",
                session_id=sid,
                fix_suggestion=f"Consider switching to {'1hour' if ttl == '5min' else '5min'} "
                               f"TTL, or batching sessions to increase cache reuse."
            )]
        return []

    def _rule_d6_atei_decline(self, ci, historical, sid) -> list[DecisionAlert]:
        """D6: 7-day ATEI dropped >15% below 14-day baseline."""
        if not historical:
            return []
        atei_7d = historical.get("atei_7d", 0)
        atei_14d = historical.get("atei_14d", 0)
        if atei_14d > 0 and atei_7d < atei_14d * 0.85:
            drop_pct = (1 - atei_7d / atei_14d) * 100
            return [DecisionAlert(
                rule_id="D6",
                severity=RuleSeverity.WARNING,
                message=f"ATEI decline: 7d ATEI={atei_7d:.2f} dropped {drop_pct:.0f}% "
                        f"below 14d baseline ({atei_14d:.2f}).",
                session_id=sid,
                fix_suggestion="Review recent changes to skill/agent definitions, "
                               "tool configurations, or workload patterns."
            )]
        return []

    def _rule_d7_task_cost_anomaly(self, m, raw, historical, sid) -> list[DecisionAlert]:
        """D7: Task type cost 50% above historical average."""
        if not historical:
            return []
        task_type = raw.task_type
        if not task_type:
            return []
        current_cpct = m.cpct
        historical_cpct = historical.get(f"cpct_{task_type}", 0)
        if historical_cpct > 0 and current_cpct > historical_cpct * 1.5:
            return [DecisionAlert(
                rule_id="D7",
                severity=RuleSeverity.WARNING,
                message=f"Task cost anomaly: {task_type} CPCT=${current_cpct:.2f} "
                        f"is {current_cpct/historical_cpct:.1f}x historical (${historical_cpct:.2f}).",
                session_id=sid,
                fix_suggestion="Review recent sessions of this type for common "
                               "inefficiency patterns."
            )]
        return []
```

### 4.2 Integration with AlertEngine

**File**: `tools/token_audit/alerts.py`

Add new alert types to the `AlertType` enum:

```python
class AlertType(Enum):
    COST_SPIKE = "cost_spike"
    EFFICIENCY_DROP = "efficiency_drop"
    CACHE_DROP = "cache_drop"
    REJECTION_SPIKE = "rejection_spike"
    AGENT_LOOP = "agent_loop"
    # New types for v2
    CACHE_DECEPTION = "cache_deception"
    CONTEXT_BLOAT = "context_bloat"
    VERIFICATION_GAP = "verification_gap"
    COLD_LOAD_DOMINANCE = "cold_load_dominance"
    WRITE_PREMIUM_LOSS = "write_premium_loss"
    ATEI_DECLINE = "atei_decline"
    TASK_COST_ANOMALY = "task_cost_anomaly"
```

### 4.3 Phase 4 Verification

- [ ] D1 triggers when HR > 0.90 and CTI < 0.50
- [ ] D2 triggers when CGR > 10 and TLR < 0.02
- [ ] D3 triggers with CRITICAL for high-risk tasks, WARNING for medium
- [ ] D4 triggers for very short sessions with high overhead
- [ ] D5 triggers when CWAR < break-even
- [ ] D6 correctly compares 7d vs 14d ATEI
- [ ] D7 triggers when CPCT > 1.5× historical
- [ ] All existing alert types still work

---

## Phase 5: Reporter, Dashboard & Integration (Day 16–22)

**Goal**: Wire everything together. Update the reporter to produce session diagnostic cards, update the CLI, and integrate with session-close-orchestrator.

### 5.1 Reporter Enhancement

**File**: `tools/token_audit/reporter.py`

Add new function: `generate_session_diagnostic_card()`:

```python
def generate_session_diagnostic_card(
    raw: RawTelemetry,
    metrics: DerivedMetrics,
    indices: CompositeIndices,
    alerts: list[DecisionAlert],
    cost_model: CostModel = None,
) -> str:
    """Generate the session-level token economic diagnostic card (text-based).

    Produces the formatted output shown in the design doc Section 5.1.
    """
    ...
```

Add new function: `generate_cache_health_report()`:

```python
def generate_cache_health_report(
    sessions: list[dict],  # each with metrics + indices
    days: int = 30,
) -> str:
    """Generate a focused cache health deep-dive report.

    Produces the 3D cache health analysis: Efficiency × Freshness × Economics.
    """
    ...
```

Update `generate_session_report()` to include the new metrics section when available:

- Add "Cache Health" subsection with M1–M3 and CTI
- Add "Token Economic Health" subsection with THS and SER
- Add workload category and alert summary

### 5.2 CLI Enhancement

**File**: `tools/token_audit/cli.py`

Add new subcommand: `diagnose`:

```python
@main.command()
@click.option("--session", "-s", "session_id", required=True)
@click.option("--format", "-f", "output_fmt", default="text")
def diagnose(session_id, output_fmt):
    """Generate a full token economic diagnostic for a session."""
    ...
```

Add new subcommand: `cache-health`:

```python
@main.command()
@click.option("--days", "-d", default=30)
@click.option("--format", "-f", "output_fmt", default="text")
def cache_health(days, output_fmt):
    """Generate a cache health deep-dive report."""
    ...
```

Update `report session` to accept `--diagnostic` flag that includes the full diagnostic card.

### 5.3 Dashboard Enhancement

**File**: `tools/token_audit/reporter.py` (`generate_dashboard` function)

Add to the terminal dashboard:
- Cache health summary row (CTI average, USR total, CWAR average)
- ATEI trend (7d vs 14d vs 30d)
- Active alerts count by severity

Add to the HTML dashboard:
- Cache health gauge chart (3 gauges: Efficiency, Freshness, Economics)
- ATEI trend line chart
- Alert timeline

### 5.4 Integration: Session Close Orchestrator

**File**: `.claude/skills/session-close-orchestrator/SKILL.md`

Update the skill to call the new diagnostic after session report generation:

```
After generating the session report:
1. Run: python -m tools.token_audit diagnose --session <id>
2. Include the diagnostic card in the completed-task archive
3. If any CRITICAL alerts fire, flag for human review
```

### 5.5 Integration: Token Audit Steward

**File**: `.claude/skills/gcs-token-audit-steward/SKILL.md`

Update the weekly audit procedure:
```
Weekly audit steps:
1. python -m tools.token_audit report trend --days 7
2. python -m tools.token_audit cache-health --days 7
3. python -m tools.token_audit dashboard --days 30
4. Review ATEI trend; if declining >15%, trigger D6 investigation
5. Review cache health states; if any D1 alerts, review cache strategy
```

### 5.6 Memory Update

After Phase 5 is complete, update project memory with baseline metrics.

### 5.7 Phase 5 Verification

- [ ] `diagnose` CLI command produces valid output for a real session
- [ ] `cache-health` CLI command aggregates correctly
- [ ] Session diagnostic card includes all sections from the design
- [ ] Dashboard shows cache health summary
- [ ] Session close orchestrator integration works end-to-end
- [ ] All existing CLI commands still work
- [ ] Full integration test: import a real session JSONL, run full pipeline

---

## Dependency Graph

```
Phase 1 (Schema + Data)
    │
    ▼
Phase 2 (Metrics Engine M1-M13)
    │
    ▼
Phase 3 (Composite Indices CI1-CI4 + Workload Classification)
    │
    ▼
Phase 4 (Decision Rules D1-D7)
    │
    ▼
Phase 5 (Reporter, Dashboard, CLI, Integration)
```

Each phase depends on the previous one. Within each phase, implementation order is:
1. New module/file
2. Unit tests
3. Integration with existing code
4. Verification

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Schema migration breaks existing DB | Low | High | Backup DB before migration; test on copy first |
| New metrics produce NaN/Inf | Medium | Medium | Guard all divisions; cap infinite values |
| Performance regression (too many metrics) | Low | Low | Metrics computed on-demand, not in hot path |
| BEI scoring conflicts with new indices | Medium | Low | Keep BEI as-is; new indices are additive |
| Workload classification misclassifies edge cases | Medium | Low | Log confidence; allow manual override |
| TWR estimation is inaccurate | High | Low | Clearly label as estimate; refine in Phase 5 calibration |

---

## Success Criteria

After all 5 phases:

1. **Cache hit rate is never reported alone** — always paired with CTI and cache health state
2. **Every session close** produces a diagnostic card with THS, CTI, SER, and any active alerts
3. **Weekly audit** includes ATEI trend, cache health summary, and alert review
4. **At least one D-rule alert** has fired and been acted upon within 14 days of deployment
5. **All 13 derived metrics** can be computed from live session data
6. **Existing BEI scores and reports** continue to work without modification
7. **Cold-load overhead (SCLOR)** is tracked and trends downward as skill/agent definitions are optimized

---

## File Change Summary

| File | Action | Lines (est.) |
|------|--------|-------------|
| `tools/token_audit/schema.sql` | Modify | +12 |
| `tools/token_audit/db.py` | Modify | +30 |
| `tools/token_audit/parser.py` | Modify | +30 |
| `tools/token_audit/metrics_engine.py` | **New** | ~350 |
| `tools/token_audit/composite_indices.py` | **New** | ~250 |
| `tools/token_audit/decision_engine.py` | **New** | ~200 |
| `tools/token_audit/alerts.py` | Modify | +10 |
| `tools/token_audit/reporter.py` | Modify | ~200 |
| `tools/token_audit/cli.py` | Modify | ~80 |
| `tools/token_audit/tests/test_metrics_engine.py` | **New** | ~150 |
| `tools/token_audit/tests/test_composite_indices.py` | **New** | ~100 |
| `tools/token_audit/tests/test_decision_engine.py` | **New** | ~120 |
| **Total** | | **~1,530** |

---

## Appendix A: Quick-Start After Implementation

```bash
# 1. Run migration
python -m tools.token_audit db init

# 2. Import a recent session for testing
python -m tools.token_audit import --jsonl <path-to-jsonl>

# 3. Generate a full diagnostic
python -m tools.token_audit diagnose --session <session-id>

# 4. Check cache health across all recent sessions
python -m tools.token_audit cache-health --days 7

# 5. View the enhanced dashboard
python -m tools.token_audit dashboard --days 30
```

## Appendix B: Rollback Plan

If the new system produces incorrect results:

1. Git revert the Phase 1–5 commits
2. Run schema downgrade: remove columns added in Phase 1
3. Restore `audit.db` from pre-upgrade backup
4. Existing BEI-only reports continue to work

The modular design ensures that new modules (`metrics_engine.py`, `composite_indices.py`, `decision_engine.py`) can be removed without affecting existing `bei_engine.py`, `reporter.py`, or `cli.py` functionality.
