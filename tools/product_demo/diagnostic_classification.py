#!/usr/bin/env python3
"""Run the researcher-facing D2 diagnostic classification demo.

The script intentionally reads expected-output files from docs/architecture
instead of hard-coding pass criteria in the tool. That keeps the benchmark
contract reviewable as documentation and makes this script a thin evidence
collector over the current CLI.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GCS_EXE = ROOT / "out" / "build" / "clang-ninja" / "GCS.exe"
DEFAULT_EXPECTED_DIR = (
    ROOT / "docs" / "architecture" / "benchmarks" / "b1-diagnostic-classification" / "expected"
)
DEFAULT_OUTPUT = (
    ROOT
    / "docs"
    / "product"
    / "demos"
    / "d2-diagnostic-classification"
    / "artifacts"
    / "d2-diagnostic-summary.json"
)


STATUS_RE = re.compile(r"^Status:\s*(?P<status>.+?)\s*$", re.MULTILINE)
ACCEPTED_RE = re.compile(r"^Accepted:\s*(?P<accepted>true|false)\s*$", re.MULTILINE)
OBSTRUCTION_RE = re.compile(r"^Obstruction:\s*(?P<code>[A-Za-z0-9_.-]+)", re.MULTILINE)
REPORT_CODE_RE = re.compile(r"^\s*(?P<code>[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)+):", re.MULTILINE)
RANK_RE = re.compile(
    r"rank_report:\s*rank\s+(?P<rank>\d+),\s*variables\s+(?P<variables>\d+).*?"
    r"residuals\s+(?P<residuals>\d+),\s*nullity\s+(?P<nullity>\d+)"
)
RESIDUAL_RE = re.compile(
    r"residual_report:\s*residuals\s+(?P<residuals>\d+),\s*norm\s+(?P<norm>[-+0-9.eE]+),\s*max\s+(?P<max>[-+0-9.eE]+)"
)


def repo_display(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def load_expected(expected_dir: Path) -> list[dict[str, Any]]:
    files = sorted(expected_dir.glob("*.expected.json"))
    if not files:
        raise FileNotFoundError(f"no expected-output files found under {repo_display(expected_dir)}")

    cases: list[dict[str, Any]] = []
    for path in files:
        with path.open("r", encoding="utf-8") as handle:
            case = json.load(handle)
        case["_expected_file"] = repo_display(path)
        cases.append(case)
    return sorted(cases, key=lambda case: (case.get("order", 9999), case["case_id"]))


def parse_output(text: str) -> dict[str, Any]:
    status_match = STATUS_RE.search(text)
    accepted_match = ACCEPTED_RE.search(text)
    obstruction_match = OBSTRUCTION_RE.search(text)
    report_codes = sorted(set(match.group("code") for match in REPORT_CODE_RE.finditer(text)))

    rank_reports = [
        {
            "rank": int(match.group("rank")),
            "variables": int(match.group("variables")),
            "residuals": int(match.group("residuals")),
            "nullity": int(match.group("nullity")),
        }
        for match in RANK_RE.finditer(text)
    ]
    residual_reports = [
        {
            "residuals": int(match.group("residuals")),
            "norm": float(match.group("norm")),
            "max": float(match.group("max")),
        }
        for match in RESIDUAL_RE.finditer(text)
    ]

    return {
        "status": status_match.group("status") if status_match else None,
        "accepted": accepted_match.group("accepted") == "true" if accepted_match else None,
        "obstruction": obstruction_match.group("code") if obstruction_match else None,
        "load_failed": "Failed to load scene" in text,
        "report_codes": report_codes,
        "rank_reports": rank_reports,
        "residual_reports": residual_reports,
    }


def check_case(expected: dict[str, Any], actual: dict[str, Any], exit_code: int, output_text: str) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []

    def add(name: str, ok: bool, expected_value: Any, actual_value: Any) -> None:
        checks.append(
            {
                "name": name,
                "ok": bool(ok),
                "expected": expected_value,
                "actual": actual_value,
            }
        )

    if "expected_exit_code" in expected:
        add("exit_code", exit_code == expected["expected_exit_code"], expected["expected_exit_code"], exit_code)
    if "expected_status" in expected:
        add("status", actual["status"] == expected["expected_status"], expected["expected_status"], actual["status"])
    if "expected_accepted" in expected:
        add(
            "accepted",
            actual["accepted"] == expected["expected_accepted"],
            expected["expected_accepted"],
            actual["accepted"],
        )
    if "expected_obstruction" in expected:
        add(
            "obstruction",
            actual["obstruction"] == expected["expected_obstruction"],
            expected["expected_obstruction"],
            actual["obstruction"],
        )
    if "expected_load_failure" in expected:
        add(
            "load_failure",
            actual["load_failed"] == expected["expected_load_failure"],
            expected["expected_load_failure"],
            actual["load_failed"],
        )
    for code in expected.get("expected_report_codes", []):
        add(f"report_code:{code}", code in actual["report_codes"], code, actual["report_codes"])
    for snippet in expected.get("expected_contains", []):
        add(f"contains:{snippet}", snippet in output_text, snippet, snippet if snippet in output_text else None)
    if "minimum_rank_reports" in expected:
        add(
            "minimum_rank_reports",
            len(actual["rank_reports"]) >= expected["minimum_rank_reports"],
            expected["minimum_rank_reports"],
            len(actual["rank_reports"]),
        )

    return checks


def run_case(gcs_exe: Path, expected: dict[str, Any]) -> dict[str, Any]:
    scene = ROOT / expected["fixture"]
    command = [str(gcs_exe), str(scene)]
    completed = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output_text = completed.stdout
    actual = parse_output(output_text)
    checks = check_case(expected, actual, completed.returncode, output_text)

    return {
        "case_id": expected["case_id"],
        "classification": expected["classification"],
        "fixture": expected["fixture"],
        "expected_file": expected["_expected_file"],
        "command": [repo_display(gcs_exe), expected["fixture"]],
        "exit_code": completed.returncode,
        "status": actual["status"],
        "accepted": actual["accepted"],
        "obstruction": actual["obstruction"],
        "load_failed": actual["load_failed"],
        "report_codes": actual["report_codes"],
        "rank_reports": actual["rank_reports"],
        "residual_reports": actual["residual_reports"],
        "checks": checks,
        "passed": all(check["ok"] for check in checks),
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gcs-exe", type=Path, default=DEFAULT_GCS_EXE)
    parser.add_argument("--expected-dir", type=Path, default=DEFAULT_EXPECTED_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--print-json", action="store_true", help="also write the JSON summary to stdout")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    gcs_exe = args.gcs_exe if args.gcs_exe.is_absolute() else ROOT / args.gcs_exe
    expected_dir = args.expected_dir if args.expected_dir.is_absolute() else ROOT / args.expected_dir
    output_path = args.output if args.output.is_absolute() else ROOT / args.output

    if not gcs_exe.exists():
        print(f"[ERROR] missing GCS executable: {repo_display(gcs_exe)}", file=sys.stderr)
        return 2

    cases = load_expected(expected_dir)
    results = [run_case(gcs_exe, case) for case in cases]
    summary = {
        "schema": "gcs.product_demo.d2_diagnostic_summary.v1",
        "audience": "solver and geometric-constraint researchers",
        "gcs_exe": repo_display(gcs_exe),
        "expected_dir": repo_display(expected_dir),
        "case_count": len(results),
        "passed_count": sum(1 for result in results if result["passed"]),
        "all_passed": all(result["passed"] for result in results),
        "cases": results,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")

    if args.print_json:
        print(json.dumps(summary, indent=2))
    print(
        f"[{'OK' if summary['all_passed'] else 'FAIL'}] D2 diagnostic classification: "
        f"{summary['passed_count']}/{summary['case_count']} cases passed -> {repo_display(output_path)}"
    )
    return 0 if summary["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
