from __future__ import annotations

import datetime as _datetime
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from .models import TOOL_VERSION, TREND_SCHEMA_VERSION


def _to_dict(value: Any) -> dict[str, Any]:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if is_dataclass(value):
        return asdict(value)
    return dict(value)


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _fmt_int(value: Any) -> str:
    return f"{_as_int(value):,}"


def _fmt_delta(value: Any) -> str:
    number = _as_int(value)
    if number > 0:
        return f"+{number:,}"
    return f"{number:,}"


def _table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(item) for item in row) + " |")
    return lines


def _snapshot_label(snapshot: dict[str, Any], index: int) -> str:
    git = dict(snapshot.get("git", {}))
    head = str(git.get("head") or "")[:12]
    generated = str(snapshot.get("generated_at") or f"snapshot-{index + 1}")
    if head:
        return f"{index + 1}: {generated} ({head})"
    return f"{index + 1}: {generated}"


def _finding_count(snapshot: dict[str, Any], severity: str) -> int:
    return sum(1 for finding in snapshot.get("findings", []) if finding.get("severity") == severity)


def _group_map(snapshot: dict[str, Any], group_name: str) -> dict[str, dict[str, Any]]:
    return {
        str(group.get("key", "")): dict(group)
        for group in snapshot.get("groups", {}).get(group_name, [])
    }


def build_trend(
    snapshots: list[Any],
    *,
    generated_at: str | None = None,
    require_two: bool = True,
    source: str = "snapshot-series",
) -> dict[str, Any]:
    data = [_to_dict(snapshot) for snapshot in snapshots]
    if require_two and len(data) < 2:
        raise ValueError("trend requires at least two snapshots")
    if not data:
        raise ValueError("trend requires at least one snapshot")

    rows: list[dict[str, Any]] = []
    for index, snapshot in enumerate(data):
        totals = dict(snapshot.get("totals", {}))
        rows.append(
            {
                "label": _snapshot_label(snapshot, index),
                "generated_at": snapshot.get("generated_at"),
                "head": dict(snapshot.get("git", {})).get("head"),
                "files": _as_int(totals.get("files")),
                "text_files": _as_int(totals.get("text_files")),
                "binary_files": _as_int(totals.get("binary_files")),
                "physical_lines": _as_int(totals.get("physical_lines")),
                "bytes": _as_int(totals.get("bytes")),
                "errors": _finding_count(snapshot, "error"),
                "warnings": _finding_count(snapshot, "warning"),
            }
        )

    first = rows[0]
    last = rows[-1]
    total_delta = {
        key: {
            "base": first[key],
            "head": last[key],
            "delta": last[key] - first[key],
        }
        for key in ["files", "text_files", "binary_files", "physical_lines", "bytes", "errors", "warnings"]
    }

    base_artifacts = _group_map(data[0], "by_artifact_class")
    head_artifacts = _group_map(data[-1], "by_artifact_class")
    artifact_delta: list[dict[str, Any]] = []
    for key in sorted(set(base_artifacts) | set(head_artifacts)):
        base = base_artifacts.get(key, {})
        head = head_artifacts.get(key, {})
        row = {
            "key": key,
            "base_files": _as_int(base.get("files")),
            "head_files": _as_int(head.get("files")),
            "delta_files": _as_int(head.get("files")) - _as_int(base.get("files")),
            "base_physical_lines": _as_int(base.get("physical_lines")),
            "head_physical_lines": _as_int(head.get("physical_lines")),
            "delta_physical_lines": _as_int(head.get("physical_lines")) - _as_int(base.get("physical_lines")),
        }
        if row["delta_files"] or row["delta_physical_lines"]:
            artifact_delta.append(row)
    artifact_delta.sort(
        key=lambda item: (abs(item["delta_physical_lines"]), abs(item["delta_files"]), item["key"]),
        reverse=True,
    )

    return {
        "schema_version": TREND_SCHEMA_VERSION,
        "tool_version": TOOL_VERSION,
        "generated_at": generated_at or _datetime.datetime.now(_datetime.UTC).isoformat(),
        "source": source,
        "snapshot_count": len(data),
        "snapshots": rows,
        "total_delta": total_delta,
        "artifact_class_delta": artifact_delta,
    }


def render_markdown_trend(trend: dict[str, Any], *, command: str | None = None, max_artifact_rows: int = 20) -> str:
    total_delta = dict(trend.get("total_delta", {}))
    artifact_delta = [dict(row) for row in trend.get("artifact_class_delta", [])]
    lines: list[str] = [
        "# GCS Repository Audit Trend",
        "",
        f"Generated: `{trend.get('generated_at', '<unknown>')}`",
        f"Schema: `{trend.get('schema_version', '<unknown>')}`",
        f"Tool: `{trend.get('tool_version', '<unknown>')}`",
        f"Source: `{trend.get('source', '<unknown>')}`",
        f"Snapshots: `{trend.get('snapshot_count', 0)}`",
        "",
        "## Executive Summary",
        "",
        (
            f"- Files changed by {_fmt_delta(total_delta.get('files', {}).get('delta'))}; "
            f"text-line delta is {_fmt_delta(total_delta.get('physical_lines', {}).get('delta'))}; "
            f"byte delta is {_fmt_delta(total_delta.get('bytes', {}).get('delta'))}."
        ),
        (
            f"- Findings changed by errors {_fmt_delta(total_delta.get('errors', {}).get('delta'))} "
            f"and warnings {_fmt_delta(total_delta.get('warnings', {}).get('delta'))}."
        ),
        (
            "- This is a baseline-only trend; collect more accepted snapshots before interpreting growth."
            if _as_int(trend.get("snapshot_count")) < 2
            else "- This trend compares the first and latest snapshots in the supplied series."
        ),
        "",
        "## Snapshot Series",
        "",
    ]
    lines.extend(
        _table(
            ["Snapshot", "Files", "Text", "Binary", "Lines", "Errors", "Warnings"],
            [
                [
                    row.get("label", ""),
                    _fmt_int(row.get("files")),
                    _fmt_int(row.get("text_files")),
                    _fmt_int(row.get("binary_files")),
                    _fmt_int(row.get("physical_lines")),
                    _fmt_int(row.get("errors")),
                    _fmt_int(row.get("warnings")),
                ]
                for row in trend.get("snapshots", [])
            ],
        )
    )

    lines.extend(["", "## Total Delta", ""])
    lines.extend(
        _table(
            ["Metric", "Base", "Head", "Delta"],
            [
                [
                    key,
                    _fmt_int(value.get("base")),
                    _fmt_int(value.get("head")),
                    _fmt_delta(value.get("delta")),
                ]
                for key, value in sorted(total_delta.items())
            ],
        )
    )

    lines.extend(["", "## Artifact Class Delta", ""])
    if artifact_delta:
        lines.extend(
            _table(
                ["Class", "Files", "Lines"],
                [
                    [
                        row.get("key", ""),
                        _fmt_delta(row.get("delta_files")),
                        _fmt_delta(row.get("delta_physical_lines")),
                    ]
                    for row in artifact_delta[:max_artifact_rows]
                ],
            )
        )
    else:
        lines.append("No artifact-class deltas.")

    lines.extend(["", "## Reproduction", ""])
    if command:
        lines.extend(["```bat", command, "```"])
    else:
        lines.append("Generated from a supplied snapshot series.")

    return "\n".join(lines).rstrip() + "\n"


def write_markdown_trend(trend: dict[str, Any], output: Path, *, command: str | None = None) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_markdown_trend(trend, command=command), encoding="utf-8", newline="\n")
