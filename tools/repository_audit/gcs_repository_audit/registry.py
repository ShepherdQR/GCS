from __future__ import annotations

import datetime as _datetime
import json
import os
from pathlib import Path
from typing import Any

from .collect import read_snapshot
from .trend import build_trend, write_markdown_trend


MANIFEST_SCHEMA_VERSION = "gcs-repository-audit-manifest-0.1"


def _fmt_int(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def _escape(value: Any) -> str:
    return str(value).replace("|", "\\|")


def _short_revision(value: str | None) -> str:
    if not value:
        return "<unknown>"
    return value[:12]


def _link(from_dir: Path, target: Path) -> str:
    return os.path.relpath(target, start=from_dir).replace("\\", "/")


def _table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_escape(item) for item in row) + " |")
    return lines


def _read_snapshot_summary(snapshot_path: Path) -> dict[str, Any]:
    if not snapshot_path.exists():
        return {
            "exists": False,
            "revision": None,
            "generated_at": None,
            "totals": {},
            "findings": [],
        }

    data = json.loads(snapshot_path.read_text(encoding="utf-8"))
    return {
        "exists": True,
        "revision": (data.get("git") or {}).get("head"),
        "generated_at": data.get("generated_at"),
        "totals": dict(data.get("totals") or {}),
        "findings": list(data.get("findings") or []),
    }


def load_registry_entries(reports_root: Path) -> list[dict[str, Any]]:
    reports_root = reports_root.resolve()
    entries: list[dict[str, Any]] = []

    for manifest_path in sorted(reports_root.rglob("manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("acceptance_state", "accepted") != "accepted":
            continue

        snapshot_path = (manifest_path.parent / str(manifest.get("snapshot_path", "snapshot.json"))).resolve()
        report_path = (manifest_path.parent / str(manifest.get("report_path", "README.md"))).resolve()
        summary = _read_snapshot_summary(snapshot_path)
        revision = manifest.get("revision") or summary.get("revision")

        entries.append(
            {
                "snapshot_id": manifest.get("snapshot_id") or manifest_path.parent.name,
                "accepted_at": manifest.get("accepted_at") or summary.get("generated_at") or "",
                "accepted_by": manifest.get("accepted_by") or "<unknown>",
                "acceptance_state": manifest.get("acceptance_state", "accepted"),
                "acceptance_scope": manifest.get("acceptance_scope") or "<unspecified>",
                "description": manifest.get("description") or "",
                "revision": revision,
                "manifest": manifest,
                "manifest_path": manifest_path,
                "snapshot_path": snapshot_path,
                "report_path": report_path,
                "snapshot_summary": summary,
            }
        )

    return sorted(entries, key=lambda entry: (str(entry["accepted_at"]), str(entry["snapshot_id"])))


def render_markdown_index(
    reports_root: Path,
    entries: list[dict[str, Any]],
    *,
    output: Path | None = None,
    command: str | None = None,
    generated_at: str | None = None,
) -> str:
    reports_root = reports_root.resolve()
    output_dir = (output.resolve().parent if output else reports_root)
    generated = generated_at or _datetime.datetime.now(_datetime.UTC).isoformat()

    lines: list[str] = [
        "# GCS Repository Audit Index",
        "",
        f"Generated: `{generated}`",
        f"Registry root: `{reports_root.as_posix()}`",
        f"Accepted snapshots: `{len(entries)}`",
        f"Manifest schema: `{MANIFEST_SCHEMA_VERSION}`",
        "",
        "## Registry Contract",
        "",
        "- `manifest.json` is the durable acceptance record for one repository audit snapshot.",
        "- `snapshot.json` is the canonical machine-readable audit artifact.",
        "- Per-snapshot `README.md` files are human projections and may be regenerated from the snapshot.",
        "- Accepted snapshots should target committed Git revisions, not dirty worktree state.",
        "",
        "## Companion Reports",
        "",
        f"- Accepted trend: [trend.md]({_link(output_dir, reports_root / 'trend.md')})",
        "",
    ]

    if entries:
        latest = entries[-1]
        summary = latest["snapshot_summary"]
        totals = summary.get("totals", {})
        lines.extend(
            [
                "## Latest Accepted Snapshot",
                "",
                f"- Snapshot: `{latest['snapshot_id']}`",
                f"- Revision: `{_short_revision(latest.get('revision'))}`",
                f"- Accepted at: `{latest['accepted_at']}`",
                f"- Scope: `{latest['acceptance_scope']}`",
                (
                    f"- Totals: {_fmt_int(totals.get('files'))} files, "
                    f"{_fmt_int(totals.get('physical_lines'))} physical text lines, "
                    f"{_fmt_int(len(summary.get('findings', [])))} findings."
                ),
                "",
            ]
        )

    lines.extend(["## Accepted Snapshots", ""])
    if entries:
        rows: list[list[Any]] = []
        for entry in reversed(entries):
            summary = entry["snapshot_summary"]
            totals = summary.get("totals", {})
            rows.append(
                [
                    entry["snapshot_id"],
                    entry["accepted_at"],
                    _short_revision(entry.get("revision")),
                    _fmt_int(totals.get("files")),
                    _fmt_int(totals.get("physical_lines")),
                    _fmt_int(len(summary.get("findings", []))),
                    f"[report]({_link(output_dir, entry['report_path'])})",
                    f"[snapshot]({_link(output_dir, entry['snapshot_path'])})",
                    f"[manifest]({_link(output_dir, entry['manifest_path'])})",
                    entry["description"],
                ]
            )
        lines.extend(
            _table(
                [
                    "Snapshot",
                    "Accepted At",
                    "Revision",
                    "Files",
                    "Lines",
                    "Findings",
                    "Report",
                    "JSON",
                    "Manifest",
                    "Description",
                ],
                rows,
            )
        )
    else:
        lines.append("No accepted repository audit snapshots were found.")

    lines.extend(["", "## Reproduction", ""])
    if command:
        lines.extend(["```bat", command, "```"])
    else:
        lines.append("Generated from registry manifests; no command string was provided.")

    return "\n".join(lines).rstrip() + "\n"


def write_markdown_index(
    reports_root: Path,
    output: Path,
    *,
    command: str | None = None,
) -> list[dict[str, Any]]:
    entries = load_registry_entries(reports_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        render_markdown_index(reports_root, entries, output=output, command=command),
        encoding="utf-8",
        newline="\n",
    )
    return entries


def accepted_snapshots(reports_root: Path) -> list[dict[str, Any]]:
    snapshots: list[dict[str, Any]] = []
    for entry in load_registry_entries(reports_root):
        snapshot_path = Path(entry["snapshot_path"])
        if snapshot_path.exists():
            snapshots.append(read_snapshot(snapshot_path))
    return snapshots


def write_accepted_trend(
    reports_root: Path,
    output: Path,
    *,
    command: str | None = None,
    allow_single: bool = True,
) -> int:
    snapshots = accepted_snapshots(reports_root)
    trend = build_trend(
        snapshots,
        require_two=not allow_single,
        source="accepted-snapshot-registry",
    )
    write_markdown_trend(trend, output, command=command)
    return len(snapshots)
