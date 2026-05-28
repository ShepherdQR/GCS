"""Shared test fixtures for token audit module."""
import pytest
import sqlite3
import tempfile
from pathlib import Path


@pytest.fixture
def sample_token_usage():
    """Standard TokenUsage for testing — simulates a typical GCS session turn."""
    from tools.token_audit.parser import TokenUsage
    return TokenUsage(
        input_tokens=50000,
        output_tokens=4000,
        cache_read_tokens=32000,
        cache_creation_tokens=0,  # DeepSeek reality: always 0
    )


@pytest.fixture
def sample_telemetry():
    """Standard RawTelemetry for derived metrics testing."""
    from tools.token_audit.metrics_engine import RawTelemetry
    return RawTelemetry(
        input_tokens=50000,
        output_tokens=4000,
        cache_read_tokens=32000,
        cache_creation_tokens=0,
        session_duration_seconds=1800.0,
        turn_count=24,
        tool_call_count=47,
        task_outcome="completed",
        task_type="feature",
        task_risk_level="medium",
        model_id="deepseek-v4-pro",
        cache_ttl_setting="5min",
        estimated_overhead_tokens=32379,
        staleness_events=0,
        verification_tokens_estimate=5000,
        tool_definition_tokens_estimate=7500,
        lines_added=120,
        lines_removed=30,
        commits_count=3,
    )


@pytest.fixture
def sample_telemetry_abandoned():
    """RawTelemetry for an abandoned session."""
    from tools.token_audit.metrics_engine import RawTelemetry
    return RawTelemetry(
        input_tokens=15000,
        output_tokens=500,
        cache_read_tokens=8000,
        cache_creation_tokens=0,
        turn_count=5,
        task_outcome="abandoned",
        task_type="debug",
        task_risk_level="high",
        cache_ttl_setting="5min",
        estimated_overhead_tokens=32379,
    )


@pytest.fixture
def sample_telemetry_stale():
    """RawTelemetry for a session with staleness events."""
    from tools.token_audit.metrics_engine import RawTelemetry
    return RawTelemetry(
        input_tokens=60000,
        output_tokens=3000,
        cache_read_tokens=45000,
        cache_creation_tokens=0,
        turn_count=30,
        task_outcome="partial",
        task_type="bug-fix",
        task_risk_level="medium",
        staleness_events=3,
        estimated_overhead_tokens=32379,
    )


@pytest.fixture
def temp_db():
    """In-memory SQLite database with full schema."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    schema_path = Path(__file__).parent.parent / "schema.sql"
    schema = schema_path.read_text(encoding="utf-8")
    conn.executescript(schema)
    yield conn
    conn.close()
