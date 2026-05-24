from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = ROOT / "fixtures" / "scene" / "showcase" / "manifest.json"

REQUIRED_POSITIVE_PANELS = {
    "scene_contract",
    "constraint_graph",
    "boundary_plan",
    "numeric_evidence",
    "gluing_and_diagnostics",
    "negative_variant",
    "gate_chain",
}
REQUIRED_TOKENS = {
    "evidence.domain",
    "evidence.graph",
    "evidence.planner",
    "evidence.numeric",
    "evidence.diagnostic",
    "evidence.failure",
    "evidence.boundary",
    "state.ok",
    "state.warning",
    "state.error",
}
REQUIRED_QUALITY_GATES = {
    "IoAdaptersContract.ShowcaseJsonSceneCarriesSolveIntentBehavior",
    "ViewerBridgeContract.ShowcaseFixtureProjectsBoundaryRankAndResidualEvidence",
    "SessionRuntimeContract.ReplayArtifactIsRuntimeTraceNotSceneConstructionHistory",
    "ViewerBridgeContract.RuntimeHistoryFrameProjectsAsReportEvidenceOnly",
    "cli.showcase_scene",
}


@dataclass
class ShowcaseEvidenceResult:
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


def require_dict(parent: dict[str, Any],
                 key: str,
                 label: str,
                 result: ShowcaseEvidenceResult) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        result.errors.append(f"{label}: missing object {key!r}")
        return {}
    return value


def require_list(parent: dict[str, Any],
                 key: str,
                 label: str,
                 result: ShowcaseEvidenceResult) -> list[Any]:
    value = parent.get(key)
    if not isinstance(value, list):
        result.errors.append(f"{label}: missing list {key!r}")
        return []
    return value


def compare_int(actual: int,
                expected: Any,
                label: str,
                field: str,
                result: ShowcaseEvidenceResult) -> None:
    if not isinstance(expected, int):
        result.errors.append(f"{label}: expected_public_evidence.{field} must be an integer")
    elif actual != expected:
        result.errors.append(f"{label}: {field} is {actual}, expected {expected}")


def check_brief(metadata: dict[str, Any],
                label: str,
                repo_root: Path,
                result: ShowcaseEvidenceResult) -> None:
    brief = require_dict(metadata, "showcase_brief", label, result)
    brief_path = brief.get("brief_path")
    if not isinstance(brief_path, str) or not brief_path:
        result.errors.append(f"{label}: showcase_brief.brief_path must be present")
    elif not resolve_repo_path(brief_path, repo_root).is_file():
        result.errors.append(f"{label}: showcase brief does not exist at {brief_path}")


def check_positive(metadata: dict[str, Any],
                   scene: dict[str, Any],
                   repo_root: Path,
                   result: ShowcaseEvidenceResult) -> None:
    label = "integrated_feature_showcase"
    check_brief(metadata, label, repo_root, result)

    expected = require_dict(metadata, "expected_public_evidence", label, result)
    compare_int(len(scene.get("rigid_sets", [])), expected.get("rigid_sets"), label, "rigid_sets", result)
    compare_int(len(scene.get("geometries", [])), expected.get("geometries"), label, "geometries", result)
    compare_int(len(scene.get("constraints", [])), expected.get("constraints"), label, "constraints", result)

    behavior = scene.get("behavior", {})
    fixed_ids = behavior.get("fixed_geometry_ids") if isinstance(behavior, dict) else None
    if fixed_ids != expected.get("fixed_geometry_ids"):
        result.errors.append(f"{label}: fixed_geometry_ids are {fixed_ids}, expected {expected.get('fixed_geometry_ids')}")

    brief = metadata.get("showcase_brief", {})
    if isinstance(brief, dict):
        missing_panels = REQUIRED_POSITIVE_PANELS.difference(set(brief.get("required_panels", [])))
        for panel in sorted(missing_panels):
            result.errors.append(f"{label}: missing required showcase panel {panel!r}")
        missing_tokens = REQUIRED_TOKENS.difference(set(brief.get("canonical_tokens", [])))
        for token in sorted(missing_tokens):
            result.errors.append(f"{label}: missing canonical token {token!r}")

    solver = require_dict(metadata, "expected_solver_evidence", label, result)
    if solver.get("accepted") is not True:
        result.errors.append(f"{label}: expected_solver_evidence.accepted must be true")
    if solver.get("state_version_after_solve") != 1:
        result.errors.append(f"{label}: state_version_after_solve must be 1")
    if solver.get("cover_contexts") != 3:
        result.errors.append(f"{label}: cover_contexts must be 3")

    rank_reports = require_list(solver, "local_numeric_reports", label, result)
    expected_numeric_reports = expected.get("numeric_reports")
    if isinstance(expected_numeric_reports, int) and len(rank_reports) != expected_numeric_reports:
        result.errors.append(
            f"{label}: local_numeric_reports count is {len(rank_reports)}, expected {expected_numeric_reports}"
        )
    required_rank_keys = {
        "rank",
        "variables",
        "free_variables",
        "frozen_variables",
        "residuals",
        "nullity",
        "max_residual",
    }
    for index, report in enumerate(rank_reports):
        if not isinstance(report, dict):
            result.errors.append(f"{label}: local_numeric_reports[{index}] must be an object")
            continue
        for key in sorted(required_rank_keys):
            if key not in report:
                result.errors.append(f"{label}: local_numeric_reports[{index}] missing {key!r}")
        if report.get("rank") != 2:
            result.errors.append(f"{label}: local_numeric_reports[{index}].rank must be 2")
        if report.get("residuals") != 2:
            result.errors.append(f"{label}: local_numeric_reports[{index}].residuals must be 2")
        if report.get("max_residual") != 0.0:
            result.errors.append(f"{label}: local_numeric_reports[{index}].max_residual must be 0.0")

    gluing = require_dict(solver, "gluing", label, result)
    if gluing.get("report_code") != "gluing.accepted":
        result.errors.append(f"{label}: gluing.report_code must be gluing.accepted")

    diagnostics = require_dict(solver, "diagnostics", label, result)
    if diagnostics.get("post_local_diagnostics_warnings") != expected.get("post_local_diagnostics"):
        result.errors.append(f"{label}: diagnostics warning count does not match expected_public_evidence")
    if diagnostics.get("residual_reports") != expected.get("numeric_reports"):
        result.errors.append(f"{label}: residual report count does not match numeric_reports")

    replay = require_dict(solver, "replay_boundary", label, result)
    if replay.get("runtime_trace_is_report_evidence") is not True:
        result.errors.append(f"{label}: replay_boundary.runtime_trace_is_report_evidence must be true")
    replay_gates = set(replay.get("quality_gates", []))
    for gate in [
        "SessionRuntimeContract.ReplayArtifactIsRuntimeTraceNotSceneConstructionHistory",
        "ViewerBridgeContract.RuntimeHistoryFrameProjectsAsReportEvidenceOnly",
    ]:
        if gate not in replay_gates:
            result.errors.append(f"{label}: replay_boundary missing quality gate {gate}")

    quality_gates = set(require_list(metadata, "quality_gates", label, result))
    for gate in sorted(REQUIRED_QUALITY_GATES):
        if gate not in quality_gates:
            result.errors.append(f"{label}: missing quality gate {gate}")


def check_negative(metadata: dict[str, Any],
                   scene: dict[str, Any],
                   repo_root: Path,
                   result: ShowcaseEvidenceResult) -> None:
    label = "integrated_feature_showcase_missing_fixed"
    check_brief(metadata, label, repo_root, result)

    brief = metadata.get("showcase_brief", {})
    if isinstance(brief, dict):
        if brief.get("required_panel") != "negative_variant":
            result.errors.append(f"{label}: required_panel must be negative_variant")
        if brief.get("canonical_token") != "evidence.failure":
            result.errors.append(f"{label}: canonical_token must be evidence.failure")

    expected = require_dict(metadata, "expected_public_evidence", label, result)
    if expected.get("load") != "rejected":
        result.errors.append(f"{label}: expected load must be rejected")
    if expected.get("report_code") != "kernel.solve_intent_missing_fixed_entity":
        result.errors.append(f"{label}: report_code must be kernel.solve_intent_missing_fixed_entity")

    behavior = scene.get("behavior", {})
    fixed_ids = behavior.get("fixed_geometry_ids") if isinstance(behavior, dict) else None
    if fixed_ids != expected.get("missing_fixed_geometry_ids"):
        result.errors.append(
            f"{label}: negative fixed ids are {fixed_ids}, expected {expected.get('missing_fixed_geometry_ids')}"
        )

    solver = require_dict(metadata, "expected_solver_evidence", label, result)
    if solver.get("accepted") is not False:
        result.errors.append(f"{label}: expected_solver_evidence.accepted must be false")
    if solver.get("report_code") != expected.get("report_code"):
        result.errors.append(f"{label}: expected_solver_evidence.report_code must match expected_public_evidence")


def run_checks(manifest_path: Path = DEFAULT_MANIFEST,
               repo_root: Path = ROOT) -> ShowcaseEvidenceResult:
    result = ShowcaseEvidenceResult()
    if not manifest_path.is_file():
        result.errors.append(f"missing showcase manifest {repo_relative(manifest_path, repo_root)}")
        return result

    try:
        manifest = read_json(manifest_path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        result.errors.append(f"could not read showcase manifest: {exc}")
        return result

    if manifest.get("schema") != "gcs-showcase-scene-manifest-v1":
        result.errors.append("showcase manifest schema must be gcs-showcase-scene-manifest-v1")

    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        result.errors.append("showcase manifest must contain entries")
        return result

    for entry in entries:
        if not isinstance(entry, dict):
            result.errors.append("showcase manifest entry must be an object")
            continue
        fixture_id = entry.get("fixture_id")
        model_path = entry.get("model_path")
        metadata_path = entry.get("metadata_path")
        if not isinstance(fixture_id, str) or not isinstance(model_path, str) or not isinstance(metadata_path, str):
            result.errors.append("showcase manifest entry must name fixture_id, model_path, and metadata_path")
            continue
        model_file = resolve_repo_path(model_path, repo_root)
        metadata_file = resolve_repo_path(metadata_path, repo_root)
        if not model_file.is_file():
            result.errors.append(f"{fixture_id}: missing model {model_path}")
            continue
        if not metadata_file.is_file():
            result.errors.append(f"{fixture_id}: missing metadata {metadata_path}")
            continue
        try:
            scene = read_json(model_file)
            metadata = read_json(metadata_file)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            result.errors.append(f"{fixture_id}: could not read fixture data: {exc}")
            continue

        if metadata.get("fixture_id") != fixture_id:
            result.errors.append(f"{fixture_id}: metadata fixture_id mismatch")
        if metadata.get("model_path") != model_path:
            result.errors.append(f"{fixture_id}: metadata model_path mismatch")

        if fixture_id == "integrated_feature_showcase":
            check_positive(metadata, scene, repo_root, result)
        elif fixture_id == "integrated_feature_showcase_missing_fixed":
            check_negative(metadata, scene, repo_root, result)
        else:
            result.warnings.append(f"{fixture_id}: no specialized showcase evidence checks")
        result.fixtures_checked += 1

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check integrated showcase fixture evidence metadata")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    args = parser.parse_args(argv)

    result = run_checks(args.manifest)
    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")
    if result.ok:
        print(f"GCS showcase fixture evidence checks passed ({result.fixtures_checked} fixtures)")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
