"""Derived metrics engine for token economic evaluation.

Implements M1-M13 from the unified evaluation system design.
Phase 2 of token-econ-metric-system-v2.

Key design decisions:
- CACHEABLE_PREFIX_ESTIMATE = 39000 based on empirical JSONL analysis
  (Turn 1 input ~40K minus ~1K user message, confirmed across 5+ sessions)
- Provider-aware: DeepSeek never reports cache_creation, use estimation fallback
- M7 (TWR) uses TLR-based heuristics until per-turn tracing is available
- M12 (CGR) uses coarse estimation from turn_count
"""

from dataclasses import dataclass, field
from typing import Optional

# Empirical constant from JSONL analysis (Phase 0 B1 resolution)
# Turn 1 input ranges 39,595–40,556 across sessions; subtract ~1K user message
CACHEABLE_PREFIX_ESTIMATE = 39000

# Providers that do NOT report cache_creation_input_tokens
PROVIDERS_WITHOUT_CACHE_CREATION = {
    "deepseek-v4-pro",
    "deepseek-v4-flash",
}


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
    task_outcome: str = ""          # completed / partial / failed / abandoned
    task_type: str = ""             # bug-fix / feature / refactor / research / docs / ops
    task_risk_level: str = "medium" # low / medium / high / critical
    model_id: str = ""
    cache_ttl_setting: str = "5min" # 5min / 1hour
    estimated_overhead_tokens: int = 0
    staleness_events: int = 0
    verification_tokens_estimate: int = 0
    tool_definition_tokens_estimate: int = 0
    lines_added: int = 0
    lines_removed: int = 0
    commits_count: int = 0
    session_id: str = ""

    @classmethod
    def from_session_snapshot(cls, snap, estimated_overhead: int = None) -> "RawTelemetry":
        """Build RawTelemetry from an existing SessionSnapshot."""
        overhead = estimated_overhead if estimated_overhead is not None else getattr(
            snap, 'estimated_overhead_tokens', CACHEABLE_PREFIX_ESTIMATE
        )
        return cls(
            input_tokens=snap.tokens.input_tokens,
            output_tokens=snap.tokens.output_tokens,
            cache_read_tokens=snap.tokens.cache_read_tokens,
            cache_creation_tokens=snap.tokens.cache_creation_tokens,
            session_duration_seconds=0.0,
            turn_count=getattr(snap, 'turn_count', 0),
            tool_call_count=getattr(snap, 'tool_calls_total', 0),
            task_outcome=getattr(snap, 'task_outcome', ''),
            task_type=getattr(snap, 'task_type', ''),
            task_risk_level=getattr(snap, 'task_risk_level', 'medium'),
            model_id=getattr(snap, 'model_id', '') or '',
            cache_ttl_setting=getattr(snap, 'cache_ttl_setting', '5min'),
            estimated_overhead_tokens=overhead,
            staleness_events=getattr(snap, 'staleness_events', 0),
            verification_tokens_estimate=getattr(snap, 'verification_tokens_estimate', 0),
            tool_definition_tokens_estimate=getattr(snap, 'tool_definition_tokens_estimate', 0),
            lines_added=getattr(snap, 'lines_added', 0),
            lines_removed=getattr(snap, 'lines_removed', 0),
            commits_count=getattr(snap, 'commits_count', 0),
            session_id=getattr(snap, 'session_id', ''),
        )


@dataclass
class DerivedMetrics:
    """Layer 2: computed metrics M1-M13."""

    # Cache metrics
    hr_raw: float = 0.0            # M1: raw cache hit rate
    hr_effective: float = 0.0      # M2: write-premium adjusted
    cwar: float = 0.0              # M3: cache write amortization ratio

    # Overhead metrics
    sclor: float = 0.0             # M4: session cold-load overhead ratio
    clae: float = 0.0              # M5: cold-load amortization efficiency

    # Efficiency metrics
    tlr: float = 0.0               # M6: token leverage ratio
    twr: float = 0.0               # M7: token waste ratio (estimated)
    usr: float = 0.0               # M8: unsafe-served rate
    stes: float = 0.0              # M9: session token efficiency score
    cpct: float = 0.0              # M10: cost per completed task (aggregate-level)

    # Risk/quality metrics
    vcr: float = 0.0               # M11: verification coverage ratio
    cgr: float = 0.0               # M12: context growth rate (coarse)
    tdor: float = 0.0              # M13: tool definition overhead ratio


class MetricsEngine:
    """Computes all 13 derived metrics from raw telemetry.

    Usage:
        engine = MetricsEngine(session_count_7d=14)
        raw = RawTelemetry(input_tokens=50000, ...)
        metrics = engine.compute(raw)
        print(f"CTI would use: HR_eff={metrics.hr_effective:.3f}, CWAR={metrics.cwar:.1f}")
    """

    def __init__(self, session_count_7d: int = 1):
        self.session_count_7d = max(session_count_7d, 1)

    # ── public API ──────────────────────────────────────────────

    def compute(self, raw: RawTelemetry) -> DerivedMetrics:
        """Compute all 13 derived metrics from raw telemetry."""
        m = DerivedMetrics()

        m.hr_raw = self._m1_hr_raw(raw)
        m.hr_effective = self._m2_hr_effective(raw)
        m.cwar = self._m3_cwar(raw)
        m.sclor = self._m4_sclor(raw)
        m.clae = self._m5_clae(raw)
        m.tlr = self._m6_tlr(raw)
        m.twr = self._m7_twr(raw, m.tlr)
        m.usr = self._m8_usr(raw)
        m.stes = self._m9_stes(raw)
        m.cpct = self._m10_cpct(raw)
        m.vcr = self._m11_vcr(raw)
        m.cgr = self._m12_cgr(raw)
        m.tdor = self._m13_tdor(raw)

        return m

    # ── M1-M3: Cache metrics ────────────────────────────────────

    @staticmethod
    def _m1_hr_raw(raw: RawTelemetry) -> float:
        """M1: Raw cache hit rate = reads / (reads + writes).

        For DeepSeek (cache_creation always 0), uses estimated cacheable prefix
        as the denominator for writes. For providers that report cache_creation,
        uses the reported value directly.
        """
        reported_creates = raw.cache_creation_tokens
        if reported_creates > 0:
            denom = raw.cache_read_tokens + reported_creates
            return raw.cache_read_tokens / denom if denom > 0 else 0.0

        # DeepSeek fallback: estimate writes from cacheable prefix
        estimated_writes = CACHEABLE_PREFIX_ESTIMATE
        denom = raw.cache_read_tokens + estimated_writes
        return raw.cache_read_tokens / denom if denom > 0 else 0.0

    @staticmethod
    def _m2_hr_effective(raw: RawTelemetry) -> float:
        """M2: Cost-adjusted cache efficiency.

        Weights each token type by its actual cost multiplier:
        - cache_read:  0.10× (90% discount)
        - cache_write: 1.25× (5-min TTL) or 2.0× (1-hour TTL)
        - uncached:    1.00× (base price)

        For DeepSeek: estimates cache_write as CACHEABLE_PREFIX_ESTIMATE tokens.
        """
        write_premium = 1.25 if raw.cache_ttl_setting == "5min" else 2.0

        # Determine cache_write tokens
        if raw.cache_creation_tokens > 0:
            write_tokens = raw.cache_creation_tokens
        else:
            # DeepSeek: estimate one write of the cacheable prefix per session
            write_tokens = CACHEABLE_PREFIX_ESTIMATE

        # Uncached = total input minus what was cached (read or written)
        uncached = raw.input_tokens - raw.cache_read_tokens - write_tokens
        if uncached < 0:
            uncached = 0

        effective_read = raw.cache_read_tokens * 0.10
        effective_write = write_tokens * write_premium
        effective_uncached = uncached * 1.0
        total_effective = effective_read + effective_write + effective_uncached

        if total_effective == 0:
            return 0.0
        return effective_read / total_effective

    @staticmethod
    def _m3_cwar(raw: RawTelemetry) -> float:
        """M3: Cache write amortization ratio = reads / writes.

        CWAR < 1.4: losing money on 5-min TTL
        CWAR < 2.2: losing money on 1-hour TTL
        CWAR = inf when cache_creation is 0 and cache_read > 0 (DeepSeek).
        """
        if raw.cache_creation_tokens > 0:
            return raw.cache_read_tokens / raw.cache_creation_tokens

        if raw.cache_read_tokens > 0:
            # DeepSeek: reads / estimated prefix write
            return raw.cache_read_tokens / CACHEABLE_PREFIX_ESTIMATE

        return 0.0

    # ── M4-M5: Overhead metrics ─────────────────────────────────

    @staticmethod
    def _m4_sclor(raw: RawTelemetry) -> float:
        """M4: Session cold-load overhead ratio."""
        if raw.input_tokens == 0:
            return 0.0
        overhead = raw.estimated_overhead_tokens or CACHEABLE_PREFIX_ESTIMATE
        return overhead / raw.input_tokens

    def _m5_clae(self, raw: RawTelemetry) -> float:
        """M5: Cold-load amortization efficiency."""
        overhead = raw.estimated_overhead_tokens or CACHEABLE_PREFIX_ESTIMATE
        fixed = overhead * self.session_count_7d
        task_tokens = raw.input_tokens - overhead
        if task_tokens < 0:
            task_tokens = 0
        return task_tokens / fixed if fixed > 0 else 0.0

    # ── M6-M10: Efficiency metrics ──────────────────────────────

    @staticmethod
    def _m6_tlr(raw: RawTelemetry) -> float:
        """M6: Token leverage ratio = output / input."""
        if raw.input_tokens == 0:
            return 0.0
        return raw.output_tokens / raw.input_tokens

    @staticmethod
    def _m7_twr(raw: RawTelemetry, tlr: float) -> float:
        """M7: Token waste ratio — heuristic estimate based on TLR.

        Lower TLR suggests more tokens are spent on context processing
        rather than productive output. This is a coarse estimate;
        per-turn tracing would give more accurate results.
        """
        if raw.input_tokens == 0:
            return 0.0
        if tlr >= 0.05:
            return 0.05   # minimal waste
        elif tlr >= 0.02:
            return 0.15
        elif tlr >= 0.01:
            return 0.30
        else:
            return 0.50   # very low output/input ratio

    @staticmethod
    def _m8_usr(raw: RawTelemetry) -> float:
        """M8: Unsafe-served rate — fraction of turns with staleness events."""
        if raw.turn_count == 0:
            return 0.0
        return min(raw.staleness_events / raw.turn_count, 1.0)

    @staticmethod
    def _m9_stes(raw: RawTelemetry) -> float:
        """M9: Session token efficiency score = outcome_value / estimated_cost."""
        if raw.input_tokens == 0:
            return 0.0

        outcome_values = {
            "completed": 1.0,
            "partial": 0.5,
            "failed": 0.15,
            "abandoned": 0.0,
        }
        outcome_value = outcome_values.get(raw.task_outcome, 0.3)

        total_tokens = raw.input_tokens + raw.output_tokens
        cost_per_token = 3.0 / 1_000_000  # $3/M input as default
        estimated_cost = total_tokens * cost_per_token

        return outcome_value / estimated_cost if estimated_cost > 0 else 0.0

    @staticmethod
    def _m10_cpct(raw: RawTelemetry) -> float:
        """M10: Cost per completed task — placeholder computed at aggregate level.

        Returns 0 for single-session calls; meaningful only when aggregated
        across sessions of the same task type.
        """
        return 0.0

    # ── M11-M13: Risk/quality metrics ────────────────────────────

    @staticmethod
    def _m11_vcr(raw: RawTelemetry) -> float:
        """M11: Verification coverage ratio."""
        if raw.input_tokens == 0:
            return 0.0
        return raw.verification_tokens_estimate / raw.input_tokens

    @staticmethod
    def _m12_cgr(raw: RawTelemetry) -> float:
        """M12: Context growth rate — coarse estimate.

        Without per-turn input token data, estimates from turn_count:
        - Short sessions (≤5 turns): first turn ≈ 50% of total input
        - Medium sessions (6-15 turns): first turn ≈ 25%
        - Long sessions (>15 turns): first turn ≈ 12%

        CGR = avg_last_3_turns / first_turn_estimate
        """
        if raw.turn_count <= 1:
            return 1.0

        if raw.turn_count <= 5:
            first_turn_est = raw.input_tokens * 0.50
        elif raw.turn_count <= 15:
            first_turn_est = raw.input_tokens * 0.25
        else:
            first_turn_est = raw.input_tokens * 0.12

        if first_turn_est <= 0:
            return 1.0

        avg_last_turns = (raw.input_tokens / raw.turn_count) * 3
        return avg_last_turns / first_turn_est

    @staticmethod
    def _m13_tdor(raw: RawTelemetry) -> float:
        """M13: Tool definition overhead ratio."""
        if raw.input_tokens == 0:
            return 0.0
        return raw.tool_definition_tokens_estimate / raw.input_tokens
