#!/usr/bin/env python3
"""Run the R1 researcher-preview package smoke path."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "docs" / "product" / "releases" / "artifacts" / "r1-researcher-preview-smoke-20260526.json"
DEFAULT_D2_OUTPUT = (
    ROOT
    / "docs"
    / "product"
    / "demos"
    / "d2-diagnostic-classification"
    / "artifacts"
    / "d2-diagnostic-summary.json"
)
DEFAULT_D3_REPLAY = (
    ROOT
    / "docs"
    / "product"
    / "demos"
    / "d3-replay-evidence"
    / "artifacts"
    / "g1-replay-evidence.report.json"
)


def repo_display(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def run_command(check_id: str, command: list[str], expected_exit_codes: list[int] | None = None) -> dict[str, Any]:
    expected_exit_codes = expected_exit_codes or [0]
    completed = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = completed.stdout.strip()
    return {
        "id": check_id,
        "kind": "command",
        "command": command,
        "expected_exit_codes": expected_exit_codes,
        "exit_code": completed.returncode,
        "passed": completed.returncode in expected_exit_codes,
        "output_excerpt": output[:1200],
    }


def check_json_file(check_id: str, path: Path, required_fields: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "id": check_id,
        "kind": "json_file",
        "path": repo_display(path),
        "required_fields": required_fields,
        "passed": False,
    }
    if not path.exists():
        result["error"] = "missing file"
        return result
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    missing = [field for field in required_fields if field not in payload]
    result["missing_fields"] = missing
    result["passed"] = not missing
    result["schema"] = payload.get("schema")
    result["status"] = payload.get("status")
    result["accepted"] = payload.get("accepted")
    result["all_passed"] = payload.get("all_passed")
    return result


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--d2-output", type=Path, default=DEFAULT_D2_OUTPUT)
    parser.add_argument("--d3-replay", type=Path, default=DEFAULT_D3_REPLAY)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    d2_output = args.d2_output if args.d2_output.is_absolute() else ROOT / args.d2_output
    d3_replay = args.d3_replay if args.d3_replay.is_absolute() else ROOT / args.d3_replay

    checks = [
        run_command("validate-docs", [sys.executable, "tools/agentic_design/agentic_toolkit.py", "validate-docs"]),
        run_command("validate-inventory", [sys.executable, "tools/agentic_design/agentic_toolkit.py", "validate-inventory"]),
        run_command("validate-skills", [sys.executable, "tools/agentic_design/agentic_toolkit.py", "validate-skills"]),
        run_command("check-dependencies", [sys.executable, "tools/agentic_design/agentic_toolkit.py", "check-dependencies"]),
        run_command("d1-cli-smoke", ["out/build/clang-ninja/GCS.exe", "fixtures/scene/basic/g1.txt"]),
        run_command(
            "d2-diagnostic-classification",
            [
                sys.executable,
                "tools/product_demo/diagnostic_classification.py",
                "--output",
                repo_display(d2_output),
            ],
        ),
        check_json_file(
            "d3-replay-evidence-artifact",
            d3_replay,
            ["schema", "accepted", "status", "committed", "rolled_back", "report_codes", "stages"],
        ),
    ]
    summary = {
        "schema": "gcs.product_release.r1_package_smoke.v1",
        "release_mode": "R1 researcher preview",
        "audience": "solver and geometric-constraint researchers",
        "all_passed": all(check["passed"] for check in checks),
        "checks": checks,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")

    print(
        f"[{'OK' if summary['all_passed'] else 'FAIL'}] R1 package smoke: "
        f"{sum(1 for check in checks if check['passed'])}/{len(checks)} checks passed -> {repo_display(output_path)}"
    )
    return 0 if summary["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
