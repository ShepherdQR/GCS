#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gcs_repository_audit import check_snapshot, collect_snapshot, write_snapshot


ROOT = Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GCS repository audit utility")
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    subparsers = parser.add_subparsers(dest="command", required=True)

    collect = subparsers.add_parser("collect", help="Collect a repository audit snapshot")
    collect.add_argument("--output", type=Path, required=True)
    collect.add_argument("--base", default=None)

    check = subparsers.add_parser("check", help="Check a snapshot or the current repository")
    check.add_argument("--snapshot", type=Path, default=None)

    return parser


def load_findings(snapshot_path: Path) -> list[dict]:
    data = json.loads(snapshot_path.read_text(encoding="utf-8"))
    return list(data.get("findings", []))


def collect_command(args: argparse.Namespace) -> int:
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


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "collect":
        return collect_command(args)
    if args.command == "check":
        return check_command(args)
    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
