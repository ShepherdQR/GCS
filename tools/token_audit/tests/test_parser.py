"""Tests for TokenUsage and SessionSnapshot data structures."""
import pytest
from tools.token_audit.parser import TokenUsage, SessionSnapshot


class TestTokenUsage:
    def test_empty_usage(self):
        u = TokenUsage()
        assert u.input_tokens == 0
        assert u.output_tokens == 0
        assert u.cache_read_tokens == 0
        assert u.cache_creation_tokens == 0
        assert u.total_tokens == 0

    def test_total_tokens(self):
        u = TokenUsage(input_tokens=100, output_tokens=50)
        assert u.total_tokens == 150

    def test_cache_hit_rate_perfect(self):
        u = TokenUsage(input_tokens=1000, cache_read_tokens=9000)
        assert u.cache_hit_rate == 0.9

    def test_cache_hit_rate_zero(self):
        u = TokenUsage(input_tokens=1000, cache_read_tokens=0)
        assert u.cache_hit_rate == 0.0

    def test_cache_hit_rate_no_input(self):
        u = TokenUsage(input_tokens=0, cache_read_tokens=0)
        assert u.cache_hit_rate == 0.0

    def test_cache_hit_rate_raw(self, sample_token_usage):
        """cache_hit_rate_raw uses the correct formula: reads / (reads + creates)."""
        assert sample_token_usage.cache_hit_rate_raw == pytest.approx(1.0)  # 32000/32000

    def test_uncached_input_tokens(self, sample_token_usage):
        """uncached = input - cache_read - cache_create."""
        assert sample_token_usage.uncached_input_tokens == 18000  # 50000-32000-0

    def test_addition(self):
        u1 = TokenUsage(input_tokens=100, output_tokens=50, cache_read_tokens=80, cache_creation_tokens=10)
        u2 = TokenUsage(input_tokens=200, output_tokens=30, cache_read_tokens=160, cache_creation_tokens=20)
        u3 = u1 + u2
        assert u3.input_tokens == 300
        assert u3.output_tokens == 80
        assert u3.cache_read_tokens == 240
        assert u3.cache_creation_tokens == 30

    def test_iadd(self):
        u1 = TokenUsage(input_tokens=100, output_tokens=50)
        u2 = TokenUsage(input_tokens=200, output_tokens=30)
        u1 += u2
        assert u1.input_tokens == 300
        assert u1.output_tokens == 80


class TestSessionSnapshot:
    def test_default_construction(self):
        snap = SessionSnapshot()
        assert snap.session_id == ""
        assert snap.tokens.total_tokens == 0
        assert snap.workload_category == ""
        assert snap.task_risk_level == "medium"

    def test_new_fields_default(self):
        """Verify all v2 fields have sensible defaults."""
        snap = SessionSnapshot()
        assert snap.cache_ttl_setting == "5min"
        assert snap.workload_category == ""
        assert snap.task_type == ""
        assert snap.task_risk_level == "medium"
        assert snap.task_outcome == ""
        assert snap.turn_count == 0
        assert snap.estimated_overhead_tokens == 0
        assert snap.staleness_events == 0
        assert snap.verification_tokens_estimate == 0
        assert snap.tool_definition_tokens_estimate == 0
