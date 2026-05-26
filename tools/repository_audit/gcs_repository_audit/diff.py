from __future__ import annotations

import datetime as _datetime
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from .models import (
    DIFF_SCHEMA_VERSION,
    TOOL_VERSION,
    FileMetricDelta,
    FindingDelta,
    GroupMetricDelta,
    NumericDelta,
    RepositoryAuditDiff,
)


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


def _git_dict(snapshot: dict[str, Any]) -> dict[str, Any]:
    return dict(snapshot.get("git", {}))


def _metric_by_path(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(metric.get("path", "")): dict(metric) for metric in snapshot.get("files", [])}


def _group_by_key(groups: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(group.get("key", "")): dict(group) for group in groups}


def _numeric_delta(base_value: Any, head_value: Any) -> NumericDelta:
    base_int = _as_int(base_value)
    head_int = _as_int(head_value)
    return NumericDelta(base=base_int, head=head_int, delta=head_int - base_int)


def _changed_file(path: str, base: dict[str, Any] | None, head: dict[str, Any] | None) -> FileMetricDelta | None:
    if base is None and head is None:
        return None
    if base is None:
        return FileMetricDelta(
            path=path,
            change_type="added",
            head_artifact_class=str(head.get("artifact_class")) if head else None,
            head_gcs_module=head.get("gcs_module") if head else None,
            head_bytes=_as_int(head.get("bytes")) if head else 0,
            delta_bytes=_as_int(head.get("bytes")) if head else 0,
            head_physical_lines=_as_int(head.get("physical_lines")) if head else 0,
            delta_physical_lines=_as_int(head.get("physical_lines")) if head else 0,
        )
    if head is None:
        return FileMetricDelta(
            path=path,
            change_type="removed",
            base_artifact_class=str(base.get("artifact_class")),
            base_gcs_module=base.get("gcs_module"),
            base_bytes=_as_int(base.get("bytes")),
            delta_bytes=-_as_int(base.get("bytes")),
            base_physical_lines=_as_int(base.get("physical_lines")),
            delta_physical_lines=-_as_int(base.get("physical_lines")),
        )

    changed = any(
        base.get(key) != head.get(key)
        for key in ("artifact_class", "gcs_module", "bytes", "physical_lines", "language_hint")
    )
    if not changed:
        return None

    base_bytes = _as_int(base.get("bytes"))
    head_bytes = _as_int(head.get("bytes"))
    base_lines = _as_int(base.get("physical_lines"))
    head_lines = _as_int(head.get("physical_lines"))
    return FileMetricDelta(
        path=path,
        change_type="modified",
        base_artifact_class=str(base.get("artifact_class")),
        head_artifact_class=str(head.get("artifact_class")),
        base_gcs_module=base.get("gcs_module"),
        head_gcs_module=head.get("gcs_module"),
        base_bytes=base_bytes,
        head_bytes=head_bytes,
        delta_bytes=head_bytes - base_bytes,
        base_physical_lines=base_lines,
        head_physical_lines=head_lines,
        delta_physical_lines=head_lines - base_lines,
    )


def _group_deltas(base_snapshot: dict[str, Any], head_snapshot: dict[str, Any]) -> dict[str, list[GroupMetricDelta]]:
    result: dict[str, list[GroupMetricDelta]] = {}
    group_names = sorted(set(base_snapshot.get("groups", {})) | set(head_snapshot.get("groups", {})))
    for group_name in group_names:
        base_groups = _group_by_key(list(base_snapshot.get("groups", {}).get(group_name, [])))
        head_groups = _group_by_key(list(head_snapshot.get("groups", {}).get(group_name, [])))
        deltas: list[GroupMetricDelta] = []
        for key in sorted(set(base_groups) | set(head_groups)):
            base = base_groups.get(key, {})
            head = head_groups.get(key, {})
            delta = GroupMetricDelta(
                key=key,
                base_files=_as_int(base.get("files")),
                head_files=_as_int(head.get("files")),
                delta_files=_as_int(head.get("files")) - _as_int(base.get("files")),
                base_bytes=_as_int(base.get("bytes")),
                head_bytes=_as_int(head.get("bytes")),
                delta_bytes=_as_int(head.get("bytes")) - _as_int(base.get("bytes")),
                base_physical_lines=_as_int(base.get("physical_lines")),
                head_physical_lines=_as_int(head.get("physical_lines")),
                delta_physical_lines=_as_int(head.get("physical_lines")) - _as_int(base.get("physical_lines")),
            )
            if delta.delta_files or delta.delta_bytes or delta.delta_physical_lines:
                deltas.append(delta)
        result[group_name] = sorted(
            deltas,
            key=lambda item: (abs(item.delta_physical_lines), abs(item.delta_files), item.key),
            reverse=True,
        )
    return result


def _finding_key(finding: dict[str, Any]) -> tuple[str, str, str | None]:
    return (
        str(finding.get("id", "")),
        str(finding.get("severity", "")),
        finding.get("path"),
    )


def _finding_deltas(base_snapshot: dict[str, Any], head_snapshot: dict[str, Any]) -> list[FindingDelta]:
    base_findings = {_finding_key(dict(finding)): dict(finding) for finding in base_snapshot.get("findings", [])}
    head_findings = {_finding_key(dict(finding)): dict(finding) for finding in head_snapshot.get("findings", [])}
    deltas: list[FindingDelta] = []
    for key in sorted(set(base_findings) - set(head_findings)):
        finding = base_findings[key]
        deltas.append(
            FindingDelta(
                change_type="removed",
                id=str(finding.get("id", "")),
                severity=str(finding.get("severity", "")),
                path=finding.get("path"),
                message=str(finding.get("message", "")),
            )
        )
    for key in sorted(set(head_findings) - set(base_findings)):
        finding = head_findings[key]
        deltas.append(
            FindingDelta(
                change_type="added",
                id=str(finding.get("id", "")),
                severity=str(finding.get("severity", "")),
                path=finding.get("path"),
                message=str(finding.get("message", "")),
            )
        )
    return deltas


def compare_snapshots(
    base_snapshot: Any,
    head_snapshot: Any,
    *,
    generated_at: str | None = None,
) -> RepositoryAuditDiff:
    base = _to_dict(base_snapshot)
    head = _to_dict(head_snapshot)
    total_keys = sorted(set(base.get("totals", {})) | set(head.get("totals", {})))
    totals = {
        key: _numeric_delta(base.get("totals", {}).get(key), head.get("totals", {}).get(key))
        for key in total_keys
    }

    base_files = _metric_by_path(base)
    head_files = _metric_by_path(head)
    files = [
        delta
        for path in sorted(set(base_files) | set(head_files))
        if (delta := _changed_file(path, base_files.get(path), head_files.get(path))) is not None
    ]
    files = sorted(files, key=lambda item: (item.change_type, item.path))
    summary = {
        "changed_files": len(files),
        "added_files": sum(1 for item in files if item.change_type == "added"),
        "removed_files": sum(1 for item in files if item.change_type == "removed"),
        "modified_files": sum(1 for item in files if item.change_type == "modified"),
        "delta_physical_lines": totals.get("physical_lines", NumericDelta()).delta,
        "delta_bytes": totals.get("bytes", NumericDelta()).delta,
        "added_findings": 0,
        "removed_findings": 0,
    }
    findings = _finding_deltas(base, head)
    summary["added_findings"] = sum(1 for item in findings if item.change_type == "added")
    summary["removed_findings"] = sum(1 for item in findings if item.change_type == "removed")

    return RepositoryAuditDiff(
        schema_version=DIFF_SCHEMA_VERSION,
        tool_version=TOOL_VERSION,
        generated_at=generated_at or _datetime.datetime.now(_datetime.UTC).isoformat(),
        base_git=_git_dict(base),
        head_git=_git_dict(head),
        summary=summary,
        totals=totals,
        groups=_group_deltas(base, head),
        files=files,
        findings=findings,
    )


def write_diff(diff: RepositoryAuditDiff, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(diff.to_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
