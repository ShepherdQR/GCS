#!/usr/bin/env python3
"""Validate promoted scene fixture manifests and expected CLI outcomes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MILESTONE_MANIFEST = ROOT / "fixtures" / "scene" / "milestone" / "manifest.json"
DEFAULT_COUNTEREXAMPLE_MANIFEST = ROOT / "fixtures" / "scene" / "counterexamples" / "manifest.json"


@dataclass
class ExpectedCliOutcome:
    accepted: bool
    exit_code: int
    status: str
    obstruction: str = ""


@dataclass
class FixtureLibraryResult:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    fixtures_checked: int = 0

    @property
    def ok(self) -> bool:
        return not self.errors


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def canonical_digest(path: Path) -> str:
    data = read_json(path)
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def repo_relative(path: Path, repo_root: Path = ROOT) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return str(path)


def resolve_repo_path(raw_path: str, repo_root: Path = ROOT) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return repo_root / path


def parse_cli_field(lines: list[str], label: str) -> str:
    prefix = f"{label}:"
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return ""


def expected_from_milestone(entry: dict[str, Any], metadata: dict[str, Any]) -> ExpectedCliOutcome:
    accepted = bool(entry.get("solver_accepted"))
    solver_smoke = metadata.get("solver_smoke", {})
    obstruction = ""
    if isinstance(solver_smoke, dict):
        obstruction = str(solver_smoke.get("obstruction", "") or "")
    return ExpectedCliOutcome(
        accepted=accepted,
        exit_code=0 if accepted else 2,
        status=str(entry.get("solver_status", "")),
        obstruction=obstruction,
    )


def expected_from_counterexample(entry: dict[str, Any], metadata: dict[str, Any]) -> ExpectedCliOutcome:
    classification = metadata.get("classification", {})
    obstruction = ""
    if isinstance(classification, dict):
        obstruction = str(classification.get("expected_obstruction", "") or "")
    return ExpectedCliOutcome(
        accepted=bool(entry.get("expected_current_accepted")),
        exit_code=int(entry.get("expected_current_exit_code", 2)),
        status=str(entry.get("expected_current_solver_status", "")),
        obstruction=obstruction,
    )


def trim_lines(text: str, limit: int = 80) -> list[str]:
    return text.splitlines()[:limit]


def run_solver(scene_path: Path,
               solver_command: list[str],
               repo_root: Path,
               timeout_seconds: float) -> dict[str, Any]:
    completed = subprocess.run(
        [*solver_command, str(scene_path)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    return {
        "exit_code": completed.returncode,
        "stdout_lines": trim_lines(completed.stdout),
        "stderr_lines": trim_lines(completed.stderr),
    }


def check_entry(entry: dict[str, Any],
                manifest_kind: str,
                repo_root: Path,
                solver_command: list[str],
                timeout_seconds: float,
                result: FixtureLibraryResult) -> None:
    fixture_id = entry.get("fixture_id")
    model_path = entry.get("model_path")
    metadata_path = entry.get("metadata_path")
    expected_digest = entry.get("digest")
    if not isinstance(fixture_id, str) or not isinstance(model_path, str) or not isinstance(metadata_path, str):
        result.errors.append(f"{manifest_kind}: entry must name fixture_id, model_path, and metadata_path")
        return

    model_file = resolve_repo_path(model_path, repo_root)
    metadata_file = resolve_repo_path(metadata_path, repo_root)
    if not model_file.is_file():
        result.errors.append(f"{fixture_id}: missing model {model_path}")
        return
    if not metadata_file.is_file():
        result.errors.append(f"{fixture_id}: missing metadata {metadata_path}")
        return

    try:
        model = read_json(model_file)
        metadata = read_json(metadata_file)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        result.errors.append(f"{fixture_id}: could not read fixture JSON: {exc}")
        return

    if model.get("format_version") != "gcs-0.3":
        result.errors.append(f"{fixture_id}: model format_version must be gcs-0.3")
    for field_name in ["rigid_sets", "geometries", "constraints"]:
        if not isinstance(model.get(field_name), list):
            result.errors.append(f"{fixture_id}: model field {field_name!r} must be a list")

    digest = canonical_digest(model_file)
    if digest != expected_digest:
        result.errors.append(f"{fixture_id}: canonical digest is {digest}, expected {expected_digest}")

    expected = (
        expected_from_milestone(entry, metadata)
        if manifest_kind == "milestone"
        else expected_from_counterexample(entry, metadata)
    )
    if not expected.status:
        result.errors.append(f"{fixture_id}: expected CLI status is missing")

    try:
        actual = run_solver(model_file, solver_command, repo_root, timeout_seconds)
    except (OSError, subprocess.TimeoutExpired) as exc:
        result.errors.append(f"{fixture_id}: solver command failed to run: {exc}")
        return

    stdout_lines = actual["stdout_lines"]
    stderr_lines = actual["stderr_lines"]
    actual_status = parse_cli_field(stdout_lines, "Status")
    actual_accepted = parse_cli_field(stdout_lines, "Accepted").lower()
    if actual["exit_code"] != expected.exit_code:
        result.errors.append(f"{fixture_id}: CLI exit {actual['exit_code']}, expected {expected.exit_code}")
    if actual_status != expected.status:
        result.errors.append(f"{fixture_id}: CLI status {actual_status!r}, expected {expected.status!r}")
    if actual_accepted != str(expected.accepted).lower():
        result.errors.append(f"{fixture_id}: CLI accepted {actual_accepted!r}, expected {expected.accepted}")
    if expected.obstruction:
        combined = "\n".join([*stdout_lines, *stderr_lines])
        if expected.obstruction not in combined:
            result.errors.append(f"{fixture_id}: expected obstruction {expected.obstruction!r} not present in CLI output")

    result.fixtures_checked += 1


def check_manifest(manifest_path: Path,
                   manifest_kind: str,
                   expected_schema: str,
                   repo_root: Path,
                   solver_command: list[str],
                   timeout_seconds: float,
                   result: FixtureLibraryResult) -> None:
    if not manifest_path.is_file():
        result.errors.append(f"missing {manifest_kind} manifest {repo_relative(manifest_path, repo_root)}")
        return
    try:
        manifest = read_json(manifest_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        result.errors.append(f"could not read {manifest_kind} manifest: {exc}")
        return

    if manifest.get("schema") != expected_schema:
        result.errors.append(f"{manifest_kind} manifest schema must be {expected_schema}")
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        result.errors.append(f"{manifest_kind} manifest must contain entries")
        return
    if manifest.get("entry_count") != len(entries):
        result.errors.append(f"{manifest_kind} manifest entry_count does not match entries")

    for entry in entries:
        if not isinstance(entry, dict):
            result.errors.append(f"{manifest_kind} manifest entry must be an object")
            continue
        check_entry(entry, manifest_kind, repo_root, solver_command, timeout_seconds, result)


def run_checks(milestone_manifest: Path = DEFAULT_MILESTONE_MANIFEST,
               counterexample_manifest: Path = DEFAULT_COUNTEREXAMPLE_MANIFEST,
               repo_root: Path = ROOT,
               solver_command: list[str] | None = None,
               timeout_seconds: float = 20.0) -> FixtureLibraryResult:
    command = solver_command or [str(repo_root / "out" / "build" / "clang-ninja" / ("GCS.exe" if os.name == "nt" else "GCS"))]
    result = FixtureLibraryResult()
    check_manifest(
        milestone_manifest,
        "milestone",
        "gcs-milestone-manifest-v1",
        repo_root,
        command,
        timeout_seconds,
        result,
    )
    check_manifest(
        counterexample_manifest,
        "counterexample",
        "gcs-counterexample-manifest-v1",
        repo_root,
        command,
        timeout_seconds,
        result,
    )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate promoted GCS scene fixture libraries")
    parser.add_argument("--milestone-manifest", type=Path, default=DEFAULT_MILESTONE_MANIFEST)
    parser.add_argument("--counterexample-manifest", type=Path, default=DEFAULT_COUNTEREXAMPLE_MANIFEST)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--gcs-exe", default="")
    parser.add_argument("--solver-command", nargs="+", default=[])
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    return parser


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    solver_command = args.solver_command or ([args.gcs_exe] if args.gcs_exe else None)
    result = run_checks(
        milestone_manifest=args.milestone_manifest,
        counterexample_manifest=args.counterexample_manifest,
        repo_root=args.repo_root,
        solver_command=solver_command,
        timeout_seconds=args.timeout_seconds,
    )

    for warning in result.warnings:
        print(f"[WARN] {warning}")
    for error in result.errors:
        print(f"[FAIL] {error}")
    if result.ok:
        print(f"[OK] fixture-library gate passed for {result.fixtures_checked} promoted scenes")
        return 0
    print(f"[FAIL] fixture-library gate failed for {result.fixtures_checked} promoted scenes")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
