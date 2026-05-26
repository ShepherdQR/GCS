"""Repository audit collector for GCS support tooling."""

from .collect import collect_index_snapshot, collect_revision_snapshot, collect_snapshot, read_snapshot, write_snapshot
from .diff import (
    compare_snapshots,
    read_diff,
    render_archive_delta,
    render_markdown_diff,
    write_archive_delta,
    write_diff,
    write_markdown_diff,
)
from .models import DIFF_SCHEMA_VERSION, SCHEMA_VERSION, TOOL_VERSION, TREND_SCHEMA_VERSION
from .policy import check_snapshot
from .registry import (
    MANIFEST_SCHEMA_VERSION,
    accepted_snapshots,
    load_registry_entries,
    render_markdown_index,
    write_accepted_trend,
    write_markdown_index,
)
from .report import render_markdown_report, write_markdown_report
from .trend import build_trend, render_markdown_trend, write_markdown_trend

__all__ = [
    "SCHEMA_VERSION",
    "DIFF_SCHEMA_VERSION",
    "MANIFEST_SCHEMA_VERSION",
    "TREND_SCHEMA_VERSION",
    "TOOL_VERSION",
    "build_trend",
    "check_snapshot",
    "collect_revision_snapshot",
    "collect_index_snapshot",
    "collect_snapshot",
    "compare_snapshots",
    "accepted_snapshots",
    "load_registry_entries",
    "read_diff",
    "read_snapshot",
    "render_archive_delta",
    "render_markdown_diff",
    "render_markdown_index",
    "render_markdown_report",
    "render_markdown_trend",
    "write_diff",
    "write_accepted_trend",
    "write_archive_delta",
    "write_markdown_diff",
    "write_markdown_index",
    "write_markdown_report",
    "write_markdown_trend",
    "write_snapshot",
]
