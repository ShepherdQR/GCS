#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from gcs_session_efficiency import read_record, write_enriched_record, write_markdown_report


ROOT = Path(__file__).resolve().parents[2]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="GCS session efficiency utility")
    subparsers = parser.add_subparsers(dest="command", required=True)

    report = subparsers.add_parser("report", help="Render a Markdown report from one or more records")
    report.add_argument("--record", type=Path, action="append", required=True)
    report.add_argument("--output", type=Path, required=True)

    enrich = subparsers.add_parser("enrich", help="Write an enriched JSON record with derived metrics")
    enrich.add_argument("--record", type=Path, required=True)
    enrich.add_argument("--output", type=Path, required=True)

    return parser


def report_command(args: argparse.Namespace, argv: list[str]) -> int:
    records = [read_record(path) for path in args.record]
    command = "python tools\\session_efficiency\\session_efficiency.py " + " ".join(argv)
    write_markdown_report(records, args.output, command=command)
    print(f"Session efficiency report written: {args.output} ({len(records)} records)")
    return 0


def enrich_command(args: argparse.Namespace) -> int:
    write_enriched_record(read_record(args.record), args.output)
    print(f"Session efficiency enriched record written: {args.output}")
    return 0


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "report":
        return report_command(args, argv)
    if args.command == "enrich":
        return enrich_command(args)
    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
