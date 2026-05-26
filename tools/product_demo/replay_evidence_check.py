#!/usr/bin/env python3
"""Validate a GCS replay evidence report for researcher-facing D3 demos."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = (
    ROOT
    / "docs"
    / "product"
    / "demos"
    / "d3-replay-evidence"
    / "artifacts"
    / "g1-replay-evidence.report.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "docs"
    / "product"
    / "demos"
    / "d3-replay-evidence"
    / "artifacts"
    / "g1-replay-evidence.check.json"
)

REQUIRED_FIELDS = [
    "schema",
    "content_type",
    "accepted",
    "status",
    "base_version",
    "final_version",
    "committed",
    "rolled_back",
    "report_codes",
    "stages",
]
REQUIRED_REPORT_CODES = [
    "runtime.pre_solve_diagnostics",
    "numeric.local_section.converged",
    "runtime.post_local_diagnostics_warning",
    "gluing.accepted",
    "runtime.commit",
]
REQUIRED_STAGE_ORDER = [
    "command_validation",
    "model_validation",
    "constraint_validation",
    "incidence_index",
    "planning",
    "pre_solve_diagnostics",
    "numeric_solve",
    "post_local_diagnostics",
    "gluing",
    "commit",
]


def repo_display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError("replay evidence payload must be a JSON object")
    return payload


def add_check(checks: list[dict[str, Any]], name: str, ok: bool, detail: Any) -> None:
    checks.append({"name": name, "ok": bool(ok), "detail": detail})


def stage_names(payload: dict[str, Any]) -> list[str]:
    stages = payload.get("stages", [])
    if not isinstance(stages, list):
        return []
    names: list[str] = []
    for stage in stages:
        if isinstance(stage, dict) and isinstance(stage.get("stage"), str):
            names.append(stage["stage"])
    return names


def check_stage_order(actual_names: list[str]) -> tuple[bool, dict[str, Any]]:
    positions: list[int] = []
    for required in REQUIRED_STAGE_ORDER:
        try:
            positions.append(actual_names.index(required))
        except ValueError:
            return False, {"missing_stage": required, "actual_stages": actual_names}
    return positions == sorted(positions), {"required_order": REQUIRED_STAGE_ORDER, "actual_stages": actual_names}


def check_replay(payload: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    missing_fields = [field for field in REQUIRED_FIELDS if field not in payload]
    add_check(checks, "required_fields", not missing_fields, {"missing": missing_fields})
    add_check(
        checks,
        "schema",
        payload.get("schema") == "gcs.replay_evidence_report.v1",
        payload.get("schema"),
    )
    add_check(
        checks,
        "content_type",
        payload.get("content_type") == "application/vnd.gcs.replay-evidence+json",
        payload.get("content_type"),
    )
    add_check(checks, "accepted_true", payload.get("accepted") is True, payload.get("accepted"))
    add_check(checks, "status_accepted_with_warnings", payload.get("status") == "AcceptedWithWarnings", payload.get("status"))
    add_check(checks, "committed_true", payload.get("committed") is True, payload.get("committed"))
    add_check(checks, "rolled_back_false", payload.get("rolled_back") is False, payload.get("rolled_back"))
    add_check(checks, "version_advanced", payload.get("final_version") == payload.get("base_version", 0) + 1, {
        "base_version": payload.get("base_version"),
        "final_version": payload.get("final_version"),
    })

    report_codes = payload.get("report_codes", [])
    add_check(checks, "report_codes_list", isinstance(report_codes, list) and all(isinstance(item, str) for item in report_codes), report_codes)
    for code in REQUIRED_REPORT_CODES:
        add_check(checks, f"report_code:{code}", code in report_codes, report_codes)
    if isinstance(report_codes, list):
        try:
            gluing_position = report_codes.index("gluing.accepted")
            commit_position = report_codes.index("runtime.commit")
            add_check(checks, "gluing_before_commit", gluing_position < commit_position, {
                "gluing_position": gluing_position,
                "commit_position": commit_position,
            })
        except ValueError:
            add_check(checks, "gluing_before_commit", False, "missing gluing.accepted or runtime.commit")

    names = stage_names(payload)
    order_ok, order_detail = check_stage_order(names)
    add_check(checks, "stage_order", order_ok, order_detail)
    add_check(
        checks,
        "commit_stage_mutates",
        any(
            isinstance(stage, dict)
            and stage.get("stage") == "commit"
            and stage.get("durable_mutation") is True
            for stage in payload.get("stages", [])
        ),
        "commit stage should be the durable mutation",
    )

    return {
        "schema": "gcs.product_demo.replay_evidence_check.v1",
        "audience": "solver and geometric-constraint researchers",
        "all_passed": all(check["ok"] for check in checks),
        "checks": checks,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    input_path = args.input if args.input.is_absolute() else ROOT / args.input
    output_path = args.output if args.output.is_absolute() else ROOT / args.output

    if not input_path.is_file():
        print(f"[ERROR] missing replay evidence input: {repo_display(input_path)}", file=sys.stderr)
        return 2
    payload = load_json(input_path)
    result = check_replay(payload)
    result["input"] = repo_display(input_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")

    passed = sum(1 for check in result["checks"] if check["ok"])
    total = len(result["checks"])
    print(
        f"[{'OK' if result['all_passed'] else 'FAIL'}] replay evidence check: "
        f"{passed}/{total} checks passed -> {repo_display(output_path)}"
    )
    return 0 if result["all_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
