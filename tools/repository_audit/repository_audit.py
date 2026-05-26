#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gcs_repository_audit import (
    build_trend,
    check_snapshot,
    collect_revision_snapshot,
    collect_snapshot,
    compare_snapshots,
    read_diff,
    read_snapshot,
    write_diff,
    write_markdown_index,
    write_markdown_diff,
    write_markdown_report,
    write_markdown_trend,
    write_snapshot,
)


ROOT = Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GCS repository audit utility")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    subparsers = parser.add_subparsers(dest="command", required=True)

    collect = subparsers.add_parser("collect", help="Collect a repository audit snapshot")
    collect.add_argument("--output", type=Path, required=True)
    collect.add_argument("--base", default=None)
    collect.add_argument("--revision", default=None, help="Collect from a committed Git revision instead of the worktree")

    check = subparsers.add_parser("check", help="Check a snapshot or the current repository")
    check.add_argument("--snapshot", type=Path, default=None)

    report = subparsers.add_parser("report", help="Render a Markdown repository audit report")
    report.add_argument("--snapshot", type=Path, default=None)
    report.add_argument("--output", type=Path, required=True)
    report.add_argument("--base", default=None)

    diff = subparsers.add_parser("diff", help="Compare two snapshots or Git revisions")
    diff.add_argument("--base", default=None, help="Base Git revision when snapshots are not provided")
    diff.add_argument("--head", default="HEAD", help="Head Git revision when snapshots are not provided")
    diff.add_argument("--base-snapshot", type=Path, default=None)
    diff.add_argument("--head-snapshot", type=Path, default=None)
    diff.add_argument("--output", type=Path, required=True)

    diff_report = subparsers.add_parser("diff-report", help="Render a Markdown repository audit diff report")
    diff_report.add_argument("--diff", type=Path, required=True)
    diff_report.add_argument("--output", type=Path, required=True)

    trend = subparsers.add_parser("trend", help="Render a Markdown trend report from snapshots")
    trend.add_argument("--snapshot", type=Path, action="append", required=True)
    trend.add_argument("--output", type=Path, required=True)

    index = subparsers.add_parser("index", help="Render the accepted repository audit snapshot index")
    index.add_argument(
        "--reports-root",
        type=Path,
        default=ROOT / "docs" / "reports" / "repository-audit",
    )
    index.add_argument("--output", type=Path, required=True)

    return parser


def load_findings(snapshot_path: Path) -> list[dict]:
    data = json.loads(snapshot_path.read_text(encoding="utf-8"))
    return list(data.get("findings", []))


def collect_command(args: argparse.Namespace) -> int:
    if args.revision:
        snapshot = collect_revision_snapshot(args.repo_root, args.revision, base=args.base)
    else:
        snapshot = collect_snapshot(args.repo_root, base=args.base)
    write_snapshot(snapshot, args.output)
    print(
        "Repository audit snapshot written: "
        f"{args.output} ({snapshot.totals['files']} files, "
        f"{snapshot.totals['physical_lines']} text lines, "
        f"{len(snapshot.findings)} findings)"
    )
    return 0


def check_command(args: argparse.Namespace) -> int:
    if args.snapshot:
        findings = load_findings(args.snapshot)
    else:
        findings = [finding.__dict__ for finding in check_snapshot(collect_snapshot(args.repo_root))]

    errors = [finding for finding in findings if finding.get("severity") == "error"]
    warnings = [finding for finding in findings if finding.get("severity") == "warning"]
    print(f"Repository audit findings: {len(errors)} errors, {len(warnings)} warnings")
    for finding in findings[:20]:
        path = finding.get("path") or "<repo>"
        print(f"[{finding.get('severity')}] {finding.get('id')}: {path} - {finding.get('message')}")
    if len(findings) > 20:
        print(f"... {len(findings) - 20} more findings omitted from console output")
    return 1 if errors else 0


def report_command(args: argparse.Namespace, argv: list[str]) -> int:
    if args.snapshot:
        snapshot = read_snapshot(args.snapshot)
    else:
        snapshot = collect_snapshot(args.repo_root, base=args.base)

    command = "python tools\\repository_audit\\repository_audit.py " + " ".join(argv)
    write_markdown_report(snapshot, args.output, command=command)
    print(f"Repository audit report written: {args.output}")
    return 0


def diff_command(args: argparse.Namespace) -> int:
    if args.base_snapshot or args.head_snapshot:
        if not args.base_snapshot or not args.head_snapshot:
            print("diff requires both --base-snapshot and --head-snapshot", file=sys.stderr)
            return 2
        base_snapshot = read_snapshot(args.base_snapshot)
        head_snapshot = read_snapshot(args.head_snapshot)
    else:
        if not args.base:
            print("diff requires --base when snapshots are not provided", file=sys.stderr)
            return 2
        base_snapshot = collect_revision_snapshot(args.repo_root, args.base, base=args.base)
        head_snapshot = collect_revision_snapshot(args.repo_root, args.head, base=args.base)

    diff = compare_snapshots(base_snapshot, head_snapshot)
    write_diff(diff, args.output)
    summary = diff.summary
    print(
        "Repository audit diff written: "
        f"{args.output} ({summary['changed_files']} changed files, "
        f"{summary['delta_physical_lines']} text-line delta, "
        f"{summary['added_findings']} added findings, "
        f"{summary['removed_findings']} removed findings)"
    )
    return 0


def diff_report_command(args: argparse.Namespace, argv: list[str]) -> int:
    diff = read_diff(args.diff)
    command = "python tools\\repository_audit\\repository_audit.py " + " ".join(argv)
    write_markdown_diff(diff, args.output, command=command)
    print(f"Repository audit diff report written: {args.output}")
    return 0


def trend_command(args: argparse.Namespace, argv: list[str]) -> int:
    snapshots = [read_snapshot(path) for path in args.snapshot]
    try:
        trend = build_trend(snapshots)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2
    command = "python tools\\repository_audit\\repository_audit.py " + " ".join(argv)
    write_markdown_trend(trend, args.output, command=command)
    print(f"Repository audit trend report written: {args.output}")
    return 0


def index_command(args: argparse.Namespace, argv: list[str]) -> int:
    command = "python tools\\repository_audit\\repository_audit.py " + " ".join(argv)
    entries = write_markdown_index(args.reports_root, args.output, command=command)
    print(f"Repository audit index written: {args.output} ({len(entries)} accepted snapshots)")
    return 0


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "collect":
        return collect_command(args)
    if args.command == "check":
        return check_command(args)
    if args.command == "report":
        return report_command(args, argv)
    if args.command == "diff":
        return diff_command(args)
    if args.command == "diff-report":
        return diff_report_command(args, argv)
    if args.command == "trend":
        return trend_command(args, argv)
    if args.command == "index":
        return index_command(args, argv)
    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
