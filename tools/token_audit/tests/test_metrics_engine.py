"""Tests for derived metrics engine (M1-M13)."""
import pytest
from tools.token_audit.metrics_engine import (
    RawTelemetry, DerivedMetrics, MetricsEngine,
    CACHEABLE_PREFIX_ESTIMATE,
)


class TestM1RawHitRate:
    def test_perfect_hit_rate(self):
        raw = RawTelemetry(cache_read_tokens=32000, cache_creation_tokens=0)
        m = MetricsEngine().compute(raw)
        expected = 32000 / (32000 + CACHEABLE_PREFIX_ESTIMATE)
        assert m.hr_raw == pytest.approx(expected)

    def test_zero_reads(self):
        raw = RawTelemetry(cache_read_tokens=0, cache_creation_tokens=0)
        m = MetricsEngine().compute(raw)
        assert m.hr_raw == 0.0

    def test_with_reported_creation(self):
        """When cache_creation is reported (Anthropic), use it directly."""
        raw = RawTelemetry(cache_read_tokens=8000, cache_creation_tokens=2000)
        m = MetricsEngine().compute(raw)
        assert m.hr_raw == pytest.approx(0.8)  # 8000 / 10000


class TestM2EffectiveHitRate:
    def test_basic_5min_ttl(self, sample_telemetry):
        m = MetricsEngine().compute(sample_telemetry)
        # HR_eff should be lower than HR_raw because write premium is priced in
        assert m.hr_effective < m.hr_raw
        assert 0 <= m.hr_effective <= 1

    def test_1hour_ttl_higher_cost(self):
        raw_5min = RawTelemetry(
            input_tokens=50000, cache_read_tokens=32000,
            cache_ttl_setting="5min")
        raw_1hour = RawTelemetry(
            input_tokens=50000, cache_read_tokens=32000,
            cache_ttl_setting="1hour")
        m5 = MetricsEngine().compute(raw_5min)
        m1 = MetricsEngine().compute(raw_1hour)
        # 1-hour TTL has higher write cost → lower effective rate
        assert m1.hr_effective < m5.hr_effective

    def test_no_cache_usage(self):
        raw = RawTelemetry(input_tokens=50000, cache_read_tokens=0)
        m = MetricsEngine().compute(raw)
        assert m.hr_effective == 0.0


class TestM3CacheWriteAmortization:
    def test_cwar_with_estimation(self):
        raw = RawTelemetry(cache_read_tokens=78000, cache_creation_tokens=0)
        m = MetricsEngine().compute(raw)
        assert m.cwar == pytest.approx(78000 / CACHEABLE_PREFIX_ESTIMATE)

    def test_cwar_with_reported_creation(self):
        raw = RawTelemetry(cache_read_tokens=80000, cache_creation_tokens=20000)
        m = MetricsEngine().compute(raw)
        assert m.cwar == pytest.approx(4.0)

    def test_cwar_zero_reads(self):
        raw = RawTelemetry(cache_read_tokens=0)
        m = MetricsEngine().compute(raw)
        assert m.cwar == 0.0

    def test_cwar_above_break_even(self, sample_telemetry):
        """GCS sessions should have CWAR well above break-even (1.4 for 5-min)."""
        m = MetricsEngine().compute(sample_telemetry)
        assert m.cwar > 1.4, f"CWAR={m.cwar:.1f} should exceed 5-min break-even"


class TestM4M5Overhead:
    def test_sclor(self, sample_telemetry):
        m = MetricsEngine().compute(sample_telemetry)
        expected = sample_telemetry.estimated_overhead_tokens / sample_telemetry.input_tokens
        assert m.sclor == pytest.approx(expected)

    def test_sclor_zero_input(self):
        raw = RawTelemetry(input_tokens=0)
        m = MetricsEngine().compute(raw)
        assert m.sclor == 0.0

    def test_clae(self, sample_telemetry):
        engine = MetricsEngine(session_count_7d=10)
        m = engine.compute(sample_telemetry)
        overhead = sample_telemetry.estimated_overhead_tokens
        task_tokens = max(sample_telemetry.input_tokens - overhead, 0)
        expected = task_tokens / (overhead * 10)
        assert m.clae == pytest.approx(expected)


class TestM6M7Efficiency:
    def test_tlr(self, sample_telemetry):
        m = MetricsEngine().compute(sample_telemetry)
        expected = sample_telemetry.output_tokens / sample_telemetry.input_tokens
        assert m.tlr == pytest.approx(expected)

    def test_tlr_zero_input(self):
        raw = RawTelemetry(input_tokens=0, output_tokens=100)
        m = MetricsEngine().compute(raw)
        assert m.tlr == 0.0

    def test_twr_high_efficiency(self):
        """High TLR → low waste estimate."""
        raw = RawTelemetry(input_tokens=10000, output_tokens=800)
        m = MetricsEngine().compute(raw)  # TLR=0.08 → minimal waste
        assert m.twr == 0.05

    def test_twr_low_efficiency(self):
        """Low TLR → high waste estimate."""
        raw = RawTelemetry(input_tokens=50000, output_tokens=200)
        m = MetricsEngine().compute(raw)  # TLR=0.004 → high waste
        assert m.twr == 0.50


class TestM8UnsafeServedRate:
    def test_no_staleness(self, sample_telemetry):
        m = MetricsEngine().compute(sample_telemetry)
        assert m.usr == 0.0

    def test_with_staleness(self, sample_telemetry_stale):
        m = MetricsEngine().compute(sample_telemetry_stale)
        assert m.usr == pytest.approx(3 / 30)

    def test_zero_turns(self):
        raw = RawTelemetry(staleness_events=5, turn_count=0)
        m = MetricsEngine().compute(raw)
        assert m.usr == 0.0


class TestM9SessionTokenEfficiency:
    def test_completed_task(self, sample_telemetry):
        m = MetricsEngine().compute(sample_telemetry)
        assert m.stes > 0

    def test_abandoned_task(self, sample_telemetry_abandoned):
        m = MetricsEngine().compute(sample_telemetry_abandoned)
        assert m.stes == 0.0

    def test_completed_beats_abandoned(self, sample_telemetry, sample_telemetry_abandoned):
        """Same tokens, completed > abandoned."""
        engine = MetricsEngine()
        m_completed = engine.compute(sample_telemetry)
        m_abandoned = engine.compute(sample_telemetry_abandoned)
        assert m_completed.stes > m_abandoned.stes


class TestM11M12M13:
    def test_vcr(self, sample_telemetry):
        m = MetricsEngine().compute(sample_telemetry)
        expected = sample_telemetry.verification_tokens_estimate / sample_telemetry.input_tokens
        assert m.vcr == pytest.approx(expected)

    def test_cgr_short_session(self):
        raw = RawTelemetry(input_tokens=10000, turn_count=3)
        m = MetricsEngine().compute(raw)
        assert m.cgr > 0

    def test_cgr_single_turn(self):
        raw = RawTelemetry(input_tokens=10000, turn_count=1)
        m = MetricsEngine().compute(raw)
        assert m.cgr == 1.0

    def test_tdor(self, sample_telemetry):
        m = MetricsEngine().compute(sample_telemetry)
        expected = sample_telemetry.tool_definition_tokens_estimate / sample_telemetry.input_tokens
        assert m.tdor == pytest.approx(expected)


class TestRawTelemetryFromSnapshot:
    def test_from_snapshot(self):
        from tools.token_audit.parser import SessionSnapshot
        snap = SessionSnapshot()
        snap.tokens.input_tokens = 50000
        snap.tokens.output_tokens = 4000
        snap.tokens.cache_read_tokens = 32000
        snap.turn_count = 24
        snap.task_outcome = "completed"

        raw = RawTelemetry.from_session_snapshot(snap)
        assert raw.input_tokens == 50000
        assert raw.output_tokens == 4000
        assert raw.cache_read_tokens == 32000
        assert raw.turn_count == 24
        assert raw.task_outcome == "completed"

    def test_from_snapshot_uses_attr_overhead(self):
        from tools.token_audit.parser import SessionSnapshot
        snap = SessionSnapshot()
        snap.tokens.input_tokens = 50000
        snap.estimated_overhead_tokens = 25000

        raw = RawTelemetry.from_session_snapshot(snap)
        assert raw.estimated_overhead_tokens == 25000

    def test_from_snapshot_fallback_overhead(self):
        from tools.token_audit.parser import SessionSnapshot
        snap = SessionSnapshot()
        snap.tokens.input_tokens = 50000
        # estimated_overhead_tokens defaults to 0 on SessionSnapshot

        raw = RawTelemetry.from_session_snapshot(snap, estimated_overhead=CACHEABLE_PREFIX_ESTIMATE)
        assert raw.estimated_overhead_tokens == CACHEABLE_PREFIX_ESTIMATE
